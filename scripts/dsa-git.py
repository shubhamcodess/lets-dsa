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
WORKTREE_DIR = ".personal-worktree"
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


def env_val(key):
    env = os.path.join(ROOT, ".env")
    if os.path.exists(env):
        for line in open(env):
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip() or None
    return None


def mode():
    return "personal" if (env_val("PERSONALIZE") or "").lower() == "true" else "framework"


# ---------------------------------------------------------------- status

def cmd_status(_):
    b, rs, m = branch(), remotes(), mode()

    print(f"branch          {b}")
    print(f"mode (.env)     {m}   (PERSONALIZE={env_val('PERSONALIZE')})")
    if b != PUBLIC_BRANCH:
        print(f"  ! the working tree should stay on '{PUBLIC_BRANCH}'. "
              f"'{PERSONAL_BRANCH}' is worktree-only — see .claude/CLAUDE.md")
    print()

    local_email = git("config", "--local", "user.email", check=False)
    global_email = git("config", "--global", "user.email", check=False)
    print("identity")
    if local_email:
        print(f"  local     {git('config','--local','user.name',check=False)} <{local_email}>")
    else:
        print("  local     NOT SET — commits would fall back to the global identity")
    print(f"  global    <{global_email or 'unset'}>   (must never be used here)")
    if not local_email:
        print("\n  Fix before committing:")
        print('    git config --local user.name "Shubham Prakash"')
        print('    git config --local user.email "prakashshubham36@gmail.com"')
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
    print()
    print(f"private repo    {env_val('PRIVATE_REPO_URL') or '(PRIVATE_REPO_URL unset in .env)'}")
    wt = git("worktree", "list", check=False)
    if WORKTREE_DIR in wt:
        print(f"vault worktree  {WORKTREE_DIR}/ (branch {PERSONAL_BRANCH}) — "
              f"written only by scripts/sync-vault.sh")
    else:
        print(f"vault worktree  not created yet — first sync-vault.sh run makes it")
    print()
    print("push routing")
    print(f"  framework ->  git push origin {PUBLIC_BRANCH}")
    print(f"  learning  ->  bash scripts/sync-vault.sh -m \"...\"   (never git push personal)")
    return 0


# ---------------------------------------------------------------- init

def cmd_init_personal(args):
    git("config", "core.hooksPath", HOOKS)
    print(f"leak guards installed (core.hooksPath={HOOKS})")

    git("config", "--local", "user.name", "Shubham Prakash")
    git("config", "--local", "user.email", "prakashshubham36@gmail.com")
    print("local identity set (global config untouched)")

    url = args.remote or env_val("PRIVATE_REPO_URL")
    if not url:
        print("\nNeed the PRIVATE repo URL. Re-run with:")
        print("    python3 scripts/dsa-git.py init-personal --remote "
              "git@github-lets-dsa:shubhamcodess/lets-dsa.git")
        return 1
    if "@github.com:" in url:
        print(f"\n! {url} uses plain github.com, which is DENIED on this machine.")
        print("  Use the alias: git@github-lets-dsa:...  (see .claude/CLAUDE.md)")
        return 1

    rs = remotes()
    if rs.get("personal") != url:
        git("remote", "set-url" if rs.get("personal") else "add", "personal", url)
    print(f"remote personal -> {url}")

    git("config", f"branch.{PUBLIC_BRANCH}.remote", "origin")
    git("config", f"branch.{PUBLIC_BRANCH}.merge", f"refs/heads/{PUBLIC_BRANCH}")

    env = os.path.join(ROOT, ".env")
    lines = open(env).readlines() if os.path.exists(env) else []
    def upsert(key, val):
        for i, l in enumerate(lines):
            if l.strip().startswith(key + "="):
                lines[i] = f"{key}={val}\n"
                return
        lines.append(f"{key}={val}\n")
    upsert("PERSONALIZE", "true")
    upsert("PRIVATE_REPO_URL", url)
    open(env, "w").writelines(lines)
    os.chmod(env, 0o600)
    print("wrote PERSONALIZE=true and PRIVATE_REPO_URL to .env")

    print("\nDone. Personal mode.")
    print(f"  Stay on branch '{PUBLIC_BRANCH}'. Your data is gitignored here and backed up with:")
    print('    bash scripts/sync-vault.sh -m "what changed"')
    return 0


# ---------------------------------------------------------------- sync

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

def cmd_sync(args):
    """The only correct path to the `personal` remote."""
    script = os.path.join(ROOT, "scripts", "sync-vault.sh")
    msg = getattr(args, "message", None)
    cmd = ["bash", script] + (["-m", msg] if msg else [])
    if not msg:
        print("! pass -m with a real message — the timestamp default is useless later")
        return 1
    return subprocess.run(cmd, cwd=ROOT).returncode


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

    sv = sub.add_parser("save")
    sv.add_argument("message")
    sv.set_defaults(fn=cmd_save)
    sy = sub.add_parser("sync")
    sy.add_argument("-m", "--message", help="what changed (required)")
    sy.set_defaults(fn=cmd_sync)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    args = ap.parse_args()
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
