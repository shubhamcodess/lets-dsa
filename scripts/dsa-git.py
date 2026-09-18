#!/usr/bin/env python3
"""
dsa-git.py — keep your learning data and the open-source framework in separate places.

Two modes, one repository:

  framework mode   branch `main`          -> remote `origin`    (public, open source)
                   The tool itself: skills, scripts, curriculum data, pattern briefs,
                   visuals. No personal data exists here.

  personal mode    branch `personal-main` -> remote `personal`  (private)
                   Everything above PLUS your profile, progress, notes and solved
                   problems. Never pushed to `origin`.

Why the learner keeps the main working tree, and contribution gets a worktree:
switching branches deletes files the target branch does not track. If your notes lived
on a branch you switch away from, `git switch main` would empty questions/ in front of
you. So the common case -- learning -- stays put on `personal-main`, and the rare case
-- contributing a framework fix -- gets an isolated worktree at .contrib/.

Commands:
    status            what mode you are in, which remotes, what is protected
    init-personal     create personal-main, wire the private remote, start tracking data
    contrib           open .contrib/ (a worktree on main) for framework work
    save "msg"        commit to the branch you are on, with the right prefix guard
    sync              bring framework changes from main into personal-main
    check             dry-run the leak guards against your working tree
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_BRANCH = "main"
PERSONAL_BRANCH = "personal-main"
CONTRIB_DIR = ".contrib"
HOOKS = ".githooks"


def git(*args, check=True, capture=True):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=capture, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{(r.stderr or r.stdout).strip()}")
    return (r.stdout or "").strip()


def matches_personal(path, pat):
    """Directory entries (trailing /) match by prefix; file entries match exactly.
    Without this, the rule `.env` would also catch `.env.example`."""
    return path.startswith(pat) if pat.endswith("/") else path == pat


def is_structural(path):
    """.gitkeep holds an empty directory open. Structure, not data."""
    return os.path.basename(path) == ".gitkeep"


def personal_paths():
    path = os.path.join(ROOT, HOOKS, "personal-paths")
    out = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def branch():
    return git("rev-parse", "--abbrev-ref", "HEAD", check=False)


def remotes():
    out = {}
    for line in git("remote", "-v", check=False).splitlines():
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def mode():
    env = os.path.join(ROOT, ".env")
    if os.path.exists(env):
        for line in open(env):
            if line.strip().startswith("MODE="):
                return line.strip().split("=", 1)[1].strip() or None
    return None


# ---------------------------------------------------------------- status

def cmd_status(_):
    b, rs, m = branch(), remotes(), mode()
    declared = m or "(unset)"
    actual = "personal" if b == PERSONAL_BRANCH else "framework"

    print(f"branch          {b}")
    print(f"mode (.env)     {declared}")
    print(f"mode (actual)   {actual}   <- the branch is what actually decides")
    if m and m != actual:
        print(f"  ! .env says {m!r} but you are on {b}. The branch wins; fix .env.")
    print()
    print("remotes")
    for name in ("origin", "personal"):
        url = rs.get(name)
        tag = "public  " if name == "origin" else "private "
        print(f"  {name:10s} {tag} {url or '(not set)'}")
    for name, url in rs.items():
        if name not in ("origin", "personal"):
            print(f"  {name:10s}          {url}")
    print()
    up = git("config", f"branch.{b}.remote", check=False)
    print(f"`git push` on this branch goes to: {up or '(unset — pass a remote explicitly)'}")
    print()
    hp = git("config", "core.hooksPath", check=False)
    print(f"leak guards     {'ACTIVE via ' + hp if hp == HOOKS else 'NOT INSTALLED — run init-personal'}")
    print()
    print("protected paths (never reach origin):")
    for p in personal_paths():
        exists = os.path.exists(os.path.join(ROOT, p.rstrip("/")))
        listed = [f for f in git("ls-files", "--", p, check=False).splitlines()
                  if not is_structural(f)]
        tracked = bool(listed)
        state = "tracked" if tracked else ("on disk, untracked" if exists else "absent")
        print(f"  {p:26s} {state}")
    wt = git("worktree", "list", check=False)
    if CONTRIB_DIR in wt:
        print(f"\ncontrib worktree active at {CONTRIB_DIR}/ — framework work goes there")
    return 0


# ---------------------------------------------------------------- init

def cmd_init_personal(args):
    git("config", "core.hooksPath", HOOKS)
    print(f"leak guards installed (core.hooksPath={HOOKS})")

    url = args.remote
    if not url:
        print("\nYou need a PRIVATE repository for your learning data.")
        print("Create an empty private repo, then re-run:")
        print("    python3 scripts/dsa-git.py init-personal --remote git@github.com:you/lets-dsa-private.git")
        print("\nNothing else changed. No data has been pushed anywhere.")
        return 1

    rs = remotes()
    if rs.get("personal") and rs["personal"] != url:
        print(f"remote 'personal' already points at {rs['personal']}")
        print(f"  updating to {url}")
        git("remote", "set-url", "personal", url)
    elif not rs.get("personal"):
        git("remote", "add", "personal", url)
    print(f"remote personal -> {url}")

    existing = git("branch", "--list", PERSONAL_BRANCH, check=False)
    if not existing:
        git("switch", "-c", PERSONAL_BRANCH)
        print(f"created branch {PERSONAL_BRANCH}")
    elif branch() != PERSONAL_BRANCH:
        git("switch", PERSONAL_BRANCH)
        print(f"switched to {PERSONAL_BRANCH}")

    # Bind each branch to its own remote so a bare `git push` can never cross over.
    git("config", f"branch.{PERSONAL_BRANCH}.remote", "personal")
    git("config", f"branch.{PERSONAL_BRANCH}.merge", f"refs/heads/{PERSONAL_BRANCH}")
    git("config", f"branch.{PUBLIC_BRANCH}.remote", "origin")
    git("config", f"branch.{PUBLIC_BRANCH}.merge", f"refs/heads/{PUBLIC_BRANCH}")
    print(f"push routing: {PERSONAL_BRANCH} -> personal, {PUBLIC_BRANCH} -> origin")

    # Personal paths stay in .gitignore so they can never be added by accident on main.
    # Here we force-add them once; after that git tracks them and .gitignore is moot,
    # but ONLY on this branch, because main has no such commits.
    added = []
    for p in personal_paths():
        full = os.path.join(ROOT, p.rstrip("/"))
        if os.path.exists(full) and p != ".env":
            git("add", "-f", "--", p, check=False)
            added.append(p)
    if added:
        print(f"now tracked on {PERSONAL_BRANCH}: {', '.join(added)}")
    print("  (.env is never tracked on any branch — it can hold your LeetCode cookie)")

    env = os.path.join(ROOT, ".env")
    lines, seen = [], False
    if os.path.exists(env):
        for line in open(env):
            if line.strip().startswith("MODE="):
                lines.append("MODE=personal\n"); seen = True
            else:
                lines.append(line)
    if not seen:
        lines.append("MODE=personal\n")
    open(env, "w").writelines(lines)
    print("wrote MODE=personal to .env")

    print("\nDone. You are in personal mode.")
    print("  Learn here. `git push` goes to your private repo.")
    print("  To work on the framework itself: python3 scripts/dsa-git.py contrib")
    return 0


# ---------------------------------------------------------------- contrib

def cmd_contrib(_):
    path = os.path.join(ROOT, CONTRIB_DIR)
    if os.path.exists(path):
        print(f"contrib worktree already at {CONTRIB_DIR}/")
    else:
        git("worktree", "add", CONTRIB_DIR, PUBLIC_BRANCH)
        print(f"created worktree {CONTRIB_DIR}/ on branch {PUBLIC_BRANCH}")
    print(f"""
Framework work happens in {CONTRIB_DIR}/ so your notes here are never touched.

    cd {CONTRIB_DIR}
    git switch -c fix/whatever
    ... edit skills, scripts, docs ...
    git push origin fix/whatever

Your personal data does not exist in that tree — {PUBLIC_BRANCH} never tracked it.
When you are finished:  git worktree remove {CONTRIB_DIR}""")
    return 0


# ---------------------------------------------------------------- save

PREFIXES = ("stage:", "solve:", "hint:", "visual:", "pattern:", "park:", "downgrade:",
            "curriculum:", "stats:", "setup:", "topic:", "docs:", "fix:", "feat:")


def cmd_save(args):
    msg = args.message
    if not msg.startswith(PREFIXES):
        print(f"! message should start with one of: {', '.join(PREFIXES)}")
        return 1
    staged = git("diff", "--cached", "--name-only", check=False)
    if not staged:
        print("nothing staged")
        return 1
    b = branch()
    leaking = [f for f in staged.splitlines()
               if any(matches_personal(f, p) for p in personal_paths())
               and not is_structural(f)]
    if b != PERSONAL_BRANCH and leaking:
        print(f"BLOCKED — personal paths staged on '{b}':")
        for f in leaking:
            print(f"    {f}")
        print(f"\nSwitch to {PERSONAL_BRANCH} first, or unstage them.")
        return 1
    git("commit", "-m", msg, capture=False)
    print(f"committed on {b}")
    return 0


# ---------------------------------------------------------------- sync

def cmd_sync(_):
    if branch() != PERSONAL_BRANCH:
        print(f"! run this from {PERSONAL_BRANCH} (you are on {branch()})")
        return 1
    if git("status", "--porcelain", check=False):
        print("! working tree is dirty — commit or stash first")
        return 1
    print(f"merging {PUBLIC_BRANCH} into {PERSONAL_BRANCH} (framework updates only)")
    r = subprocess.run(["git", "-C", ROOT, "merge", "--no-edit", PUBLIC_BRANCH],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        print("\nResolve the conflict, then: git merge --continue")
        print("Your data is not at risk — main never tracked it, so it cannot conflict.")
    return r.returncode


# ---------------------------------------------------------------- check

def cmd_check(_):
    print("Dry-running the leak guards.\n")
    b = branch()
    tracked_on_main = []
    for p in personal_paths():
        out = git("ls-tree", "-r", "--name-only", PUBLIC_BRANCH, "--", p, check=False)
        if out:
            tracked_on_main += [f for f in out.splitlines() if not is_structural(f)]
    if tracked_on_main:
        print(f"LEAK: these personal paths are committed on '{PUBLIC_BRANCH}':")
        for f in tracked_on_main:
            print(f"    {f}")
        print(f"\n    Fix: git switch {PUBLIC_BRANCH} && git rm --cached <path> && commit")
        return 1
    print(f"clean — no personal path is tracked on '{PUBLIC_BRANCH}'")
    hp = git("config", "core.hooksPath", check=False)
    print(f"hooks: {'ACTIVE' if hp == HOOKS else 'NOT INSTALLED — run init-personal'}")
    print(f"branch: {b}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status").set_defaults(fn=cmd_status)
    ip = sub.add_parser("init-personal")
    ip.add_argument("--remote", help="git URL of your PRIVATE repository")
    ip.set_defaults(fn=cmd_init_personal)
    sub.add_parser("contrib").set_defaults(fn=cmd_contrib)
    sv = sub.add_parser("save")
    sv.add_argument("message")
    sv.set_defaults(fn=cmd_save)
    sub.add_parser("sync").set_defaults(fn=cmd_sync)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    args = ap.parse_args()
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
