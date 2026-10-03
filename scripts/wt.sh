#!/usr/bin/env bash
# Git worktrees for agents: each branch gets its own folder, so parallel agents
# (and the CEO's main folder) never switch branches under each other.
#
#   scripts/wt.sh new <branch>    create (or reuse) a worktree; prints its path
#   scripts/wt.sh path <branch>   print the worktree path for a branch
#   scripts/wt.sh done <branch>   remove the worktree (refuses if work is uncommitted)
#   scripts/wt.sh list            list all worktrees
#
# Worktrees live next to the repo: ../<repo>-worktrees/<branch with / replaced by ->
set -euo pipefail

ROOT="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
BASE="$ROOT-worktrees"
cmd="${1:-}"; branch="${2:-}"
dir_for() { echo "$BASE/${1//\//-}"; }
need_branch() { [ -n "$branch" ] || { echo "usage: scripts/wt.sh $cmd <branch>" >&2; exit 2; }; }

case "$cmd" in
  new)
    need_branch
    dir="$(dir_for "$branch")"
    if [ -d "$dir" ]; then echo "$dir"; exit 0; fi
    mkdir -p "$BASE"
    git -C "$ROOT" fetch -q origin
    if git -C "$ROOT" show-ref -q --verify "refs/heads/$branch"; then
      git -C "$ROOT" worktree add -q "$dir" "$branch"
    elif git -C "$ROOT" show-ref -q --verify "refs/remotes/origin/$branch"; then
      git -C "$ROOT" worktree add -q --track -b "$branch" "$dir" "origin/$branch"
    else
      git -C "$ROOT" worktree add -q --no-track -b "$branch" "$dir" origin/main
    fi
    echo "$dir"
    ;;
  path)
    need_branch
    dir="$(dir_for "$branch")"
    [ -d "$dir" ] && echo "$dir" || { echo "no worktree for $branch" >&2; exit 1; }
    ;;
  done)
    need_branch
    dir="$(dir_for "$branch")"
    [ -d "$dir" ] || { echo "no worktree for $branch" >&2; exit 1; }
    if [ -n "$(git -C "$dir" status --porcelain)" ]; then
      echo "refusing: $dir has uncommitted changes" >&2; exit 1
    fi
    git -C "$ROOT" worktree remove "$dir"
    # Delete the local branch only once its PR is merged (squash merges hide it from git branch --merged)
    if [ "$(gh pr view "$branch" --json state -q .state 2>/dev/null || true)" = "MERGED" ]; then
      git -C "$ROOT" branch -D "$branch" >/dev/null && echo "removed worktree and merged branch $branch"
    else
      echo "removed worktree; kept branch $branch (PR not merged)"
    fi
    ;;
  list)
    git -C "$ROOT" worktree list
    ;;
  *)
    sed -n '2,10p' "$0"; exit 2
    ;;
esac
