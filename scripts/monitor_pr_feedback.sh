#!/usr/bin/env bash
set -euo pipefail

# Intended usage:
#   1) Start after requesting Copilot review on an open PR.
#   2) Wait until new PR feedback or new PR commits arrive.
#   3) Exit immediately on the first detected update.
#
# Examples:
#   scripts/monitor_pr_feedback.sh 3 2>&1 | tee -a ~/claude.log
#   POLL_SECONDS=10 scripts/monitor_pr_feedback.sh 2>&1 | tee -a ~/claude.log

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 2
fi

PR_NUMBER="${1:-}"
POLL_SECONDS="${POLL_SECONDS:-20}"

if [[ -z "${PR_NUMBER}" ]]; then
  PR_NUMBER="$(gh pr view --json number --jq '.number')"
fi

if ! [[ "${POLL_SECONDS}" =~ ^[0-9]+$ ]] || [[ "${POLL_SECONDS}" -lt 1 ]]; then
  echo "POLL_SECONDS must be a positive integer" >&2
  exit 2
fi

REPO_FULL_NAME="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
OWNER="${REPO_FULL_NAME%%/*}"
REPO="${REPO_FULL_NAME##*/}"
AUTH_USER="$(gh api user --jq '.login')"
START_ISO="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

count_all_pages() {
  local endpoint="$1"
  gh api --paginate "${endpoint}" | jq -s 'map(.[]) | length'
}

count_actionable_issue_comments_since() {
  local endpoint="$1"
  gh api --paginate "${endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.created_at // "") > $start) |
      select((.user.login // "") != $auth) |
      select((.user.login // "") != "Copilot")
    ) |
    length
  '
}

count_actionable_review_comments_since() {
  local endpoint="$1"
  gh api --paginate "${endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.created_at // "") > $start) |
      select((.user.login // "") != $auth)
    ) |
    length
  '
}

count_actionable_reviews_since() {
  local endpoint="$1"
  gh api --paginate "${endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.submitted_at // "") > $start) |
      select(((.state // "") | ascii_downcase) != "pending") |
      select((.user.login // "") != $auth)
    ) |
    length
  '
}

print_recent_feedback() {
  local issue_endpoint="$1"
  local review_comment_endpoint="$2"
  local review_endpoint="$3"

  echo "Recent actionable issue comments:"
  gh api --paginate "${issue_endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.created_at // "") > $start) |
      select((.user.login // "") != $auth) |
      select((.user.login // "") != "Copilot") |
      {
        at: .created_at,
        user: .user.login,
        body: ((.body // "") | split("\n")[0])
      }
    ) |
    sort_by(.at) |
    .[-5:]
  '

  echo "Recent actionable review comments:"
  gh api --paginate "${review_comment_endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.created_at // "") > $start) |
      select((.user.login // "") != $auth) |
      {
        at: .created_at,
        user: .user.login,
        path: (.path // ""),
        body: ((.body // "") | split("\n")[0])
      }
    ) |
    sort_by(.at) |
    .[-10:]
  '

  echo "Recent actionable submitted reviews:"
  gh api --paginate "${review_endpoint}" | jq -s --arg start "${START_ISO}" --arg auth "${AUTH_USER}" '
    map(.[]) |
    map(
      select((.submitted_at // "") > $start) |
      select(((.state // "") | ascii_downcase) != "pending") |
      select((.user.login // "") != $auth) |
      {
        at: .submitted_at,
        user: .user.login,
        state: .state,
        body: ((.body // "") | split("\n")[0])
      }
    ) |
    sort_by(.at) |
    .[-5:]
  '
}

COMMITS_ENDPOINT="repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/commits"
ISSUE_COMMENTS_ENDPOINT="repos/${OWNER}/${REPO}/issues/${PR_NUMBER}/comments"
REVIEW_COMMENTS_ENDPOINT="repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments"
REVIEWS_ENDPOINT="repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/reviews"

BASELINE_COMMITS="$(count_all_pages "${COMMITS_ENDPOINT}")"

echo "Monitoring PR #${PR_NUMBER} on ${REPO_FULL_NAME}"
echo "Authenticated user: ${AUTH_USER}"
echo "Started at ${START_ISO} (UTC), poll interval ${POLL_SECONDS}s"
echo "Baseline commits: ${BASELINE_COMMITS}"
echo "Actionable signals: non-self commits, non-self review comments, non-self submitted reviews, non-Copilot issue comments"

while true; do
  CURRENT_COMMITS="$(count_all_pages "${COMMITS_ENDPOINT}")"
  NEW_ISSUE_COMMENTS="$(count_actionable_issue_comments_since "${ISSUE_COMMENTS_ENDPOINT}")"
  NEW_REVIEW_COMMENTS="$(count_actionable_review_comments_since "${REVIEW_COMMENTS_ENDPOINT}")"
  NEW_REVIEWS="$(count_actionable_reviews_since "${REVIEWS_ENDPOINT}")"

  if [[ "${CURRENT_COMMITS}" -gt "${BASELINE_COMMITS}" ]]; then
    echo "Detected new commits on PR #${PR_NUMBER}: ${BASELINE_COMMITS} -> ${CURRENT_COMMITS}"
    exit 0
  fi

  if [[ "${NEW_ISSUE_COMMENTS}" -gt 0 ]] || [[ "${NEW_REVIEW_COMMENTS}" -gt 0 ]] || [[ "${NEW_REVIEWS}" -gt 0 ]]; then
    echo "Detected actionable feedback on PR #${PR_NUMBER}: issue_comments=${NEW_ISSUE_COMMENTS}, review_comments=${NEW_REVIEW_COMMENTS}, reviews=${NEW_REVIEWS}"
    print_recent_feedback "${ISSUE_COMMENTS_ENDPOINT}" "${REVIEW_COMMENTS_ENDPOINT}" "${REVIEWS_ENDPOINT}"
    exit 0
  fi

  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") waiting: no new actionable commits or feedback"
  sleep "${POLL_SECONDS}"
done
