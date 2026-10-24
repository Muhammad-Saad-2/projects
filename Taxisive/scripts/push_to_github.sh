#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(git -C "$project_dir" rev-parse --show-toplevel)"
project_prefix="$(git -C "$project_dir" rev-parse --show-prefix)"
remote="${1:-origin}"
branch="$(git -C "$repo_root" branch --show-current)"

if [[ -z "$branch" ]]; then
    echo "Refusing to push from a detached HEAD." >&2
    exit 1
fi

if ! git -C "$repo_root" remote get-url "$remote" >/dev/null 2>&1; then
    echo "Git remote '$remote' is not configured." >&2
    exit 1
fi

while IFS= read -r staged_path; do
    if [[ -n "$staged_path" && "$staged_path" != "$project_prefix"* ]]; then
        echo "Refusing to include staged changes outside this project: $staged_path" >&2
        exit 1
    fi
done < <(git -C "$repo_root" diff --cached --name-only)

git -C "$repo_root" add -- \
    "${project_prefix}.gitignore" \
    "${project_prefix}.env.example" \
    "${project_prefix}README.md" \
    "${project_prefix}Docker" \
    "${project_prefix}app" \
    "${project_prefix}pyproject.toml" \
    "${project_prefix}requirements.txt" \
    "${project_prefix}uv.lock" \
    "${project_prefix}.python-version" \
    "${project_prefix}scripts"

if git -C "$repo_root" diff --cached --quiet; then
    echo "No new project changes to commit; pushing existing commits."
else
    git -C "$repo_root" commit \
        -m "feat: use PostgreSQL for persisted charges" \
        -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
fi

git -C "$repo_root" push "$remote" "$branch"
