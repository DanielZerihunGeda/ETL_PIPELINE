#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
prompt_file="$script_dir/prompt.md"

if [[ ! -f "$prompt_file" ]]; then
  echo "Missing prompt file: $prompt_file" >&2
  exit 1
fi

issue_files=()
if [[ -d "$repo_root/issues" ]]; then
  while IFS= read -r -d '' issue_file; do
    issue_files+=("$issue_file")
  done < <(find "$repo_root/issues" -maxdepth 1 -type f -name '*.md' -print0 | sort -z)
fi

if ((${#issue_files[@]})); then
  issues="$(cat "${issue_files[@]}")"
else
  issues="No issues found"
fi

commits="$(
  git -C "$repo_root" log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null ||
    echo "No commits found"
)"
prompt="$(<"$prompt_file")"

codex --ask-for-approval never exec -C "$repo_root" --sandbox danger-full-access - <<EOF
Previous commits:
$commits

Issues:
$issues

$prompt
EOF
