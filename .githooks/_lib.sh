#!/bin/sh
# Shared helpers for the lets-dsa git guards.

HOOKDIR=$(dirname "$0")
PERSONAL_LIST="$HOOKDIR/personal-paths"
PUBLIC_BRANCH="main"
PERSONAL_BRANCH="personal-main"

# Is $1 one of the personal paths?
is_personal() {
  [ -f "$PERSONAL_LIST" ] || return 1
  # .gitkeep holds an empty directory open. It is structure, not your data.
  case "$1" in */.gitkeep|.gitkeep) return 1 ;; esac
  while IFS= read -r pat; do
    case "$pat" in ''|'#'*) continue ;; esac
    case "$1" in $pat*) return 0 ;; esac
  done < "$PERSONAL_LIST"
  return 1
}

# Print every personal path found in the newline-separated list on stdin.
filter_personal() {
  while IFS= read -r f; do
    [ -n "$f" ] && is_personal "$f" && echo "$f"
  done
}

# Does this remote look like the public one?
is_public_remote() {
  [ "$1" = "origin" ]
}

die_leak() {
  echo ""
  echo "BLOCKED — this would put your personal data in the public repository."
  echo ""
  echo "$1"
  echo ""
  echo "Offending paths:"
  echo "$2" | sed 's/^/    /'
  echo ""
  echo "What to do:"
  echo "    Your data belongs on '$PERSONAL_BRANCH' -> remote 'personal'."
  echo "    Framework changes belong on '$PUBLIC_BRANCH' -> remote 'origin'."
  echo "    See docs/MODES.md, or run: python3 scripts/dsa-git.py status"
  echo ""
  echo "If you are certain this is wrong, bypass with --no-verify — but read the"
  echo "list above first. This hook exists because a leak cannot be undone."
  echo ""
}
