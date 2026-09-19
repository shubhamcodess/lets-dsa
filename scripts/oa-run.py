#!/usr/bin/env python3
"""
oa-run.py — compile and run a learner's OA submission against real tests.

Generates everything it needs, per problem, at the moment it is asked. Nothing is
pre-built and nothing per-problem is stored in the repo: the harness, the binaries and
the scratch files live in a temp directory and are thrown away.

The learner writes only what LeetCode's own stub contains -- no imports, no main, no
test plumbing. This script supplies all of that around their code.

    python3 scripts/oa-run.py --slug two-sum --lang java --file sol.java
    python3 scripts/oa-run.py --slug two-sum --lang cpp --file sol.cpp --tests t.json

--tests is a JSON list of {"input": ["[2,7,11,15]", "9"], "expected": "[0,1]"}.
Without it, the problem's own example inputs are run and the outputs are reported
without a verdict (there is nothing to compare against).

Supported types: scalars and their arrays/matrices. ListNode, TreeNode and design
problems are refused explicitly rather than mis-harnessed.
"""

import argparse
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122 Safari/537.36"
GQL = "https://leetcode.com/graphql"
LANGS = ("java", "cpp", "typescript", "python3")

SCALARS = {"integer", "string", "boolean", "double", "character", "long"}
UNSUPPORTED_NODES = {"ListNode", "TreeNode", "Node", "NestedInteger"}

_CTX = None


def ssl_ctx():
    """Verifying context that still works behind a corporate TLS proxy.
    Same approach as build-curriculum.py: relax only VERIFY_X509_STRICT."""
    global _CTX
    if _CTX:
        return _CTX
    ctx = ssl.create_default_context()
    try:
        urllib.request.urlopen(
            urllib.request.Request("https://leetcode.com/robots.txt",
                                   headers={"User-Agent": UA}), timeout=20, context=ctx)
        _CTX = ctx
        return ctx
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            _CTX = ctx
            return ctx
    roots = os.path.join(ROOT, "curriculum", "sources", "_system-roots.pem")
    if not os.path.exists(roots) or os.path.getsize(roots) == 0:
        os.makedirs(os.path.dirname(roots), exist_ok=True)
        with open(roots, "w") as f:
            for kc in ("/System/Library/Keychains/SystemRootCertificates.keychain",
                       "/Library/Keychains/System.keychain"):
                try:
                    f.write(subprocess.run(["security", "find-certificate", "-a", "-p", kc],
                                           capture_output=True, text=True, timeout=60).stdout)
                except Exception:
                    pass
    ctx = ssl.create_default_context(cafile=roots)
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    _CTX = ctx
    return ctx


PROBLEM_Q = """query q($t: String!) {
  question(titleSlug: $t) {
    questionFrontendId title difficulty metaData exampleTestcases
    codeSnippets { langSlug code }
  }
}"""


def fetch_problem(slug):
    req = urllib.request.Request(
        GQL, data=json.dumps({"query": PROBLEM_Q, "variables": {"t": slug}}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA,
                 "Referer": "https://leetcode.com"})
    body = json.loads(urllib.request.urlopen(req, timeout=25, context=ssl_ctx()).read())
    q = (body.get("data") or {}).get("question")
    if not q:
        raise SystemExit(f"slug {slug!r} did not resolve on leetcode.com")
    q["meta"] = json.loads(q["metaData"])
    q["snippets"] = {c["langSlug"]: c["code"] for c in q.get("codeSnippets") or []}
    return q


def check_supported(meta):
    """Refuse loudly rather than generating a harness that quietly does the wrong thing."""
    if "classname" in {k.lower() for k in meta}:
        return (f"'{meta.get('classname')}' is a DESIGN problem (constructor + operation "
                "sequence). OA mode cannot harness these yet — solve it on leetcode.com.")
    types = [p["type"] for p in meta.get("params", [])] + [meta.get("return", {}).get("type", "")]
    for t in types:
        base = t.replace("[]", "").replace("list<", "").replace(">", "").strip()
        if base in UNSUPPORTED_NODES:
            return (f"This problem uses {base}, which needs a node deserializer OA mode "
                    "does not generate yet. Scalars, strings and their arrays are supported.")
        if base and base not in SCALARS:
            return f"Unsupported parameter type {t!r}. Supported: {sorted(SCALARS)} and arrays."
    return None


def split_examples(raw, arity):
    """exampleTestcases is newline-separated with `arity` lines per case."""
    lines = [l for l in (raw or "").split("\n") if l.strip() != ""]
    if arity <= 0:
        return []
    return [{"input": lines[i:i + arity], "expected": None}
            for i in range(0, len(lines) - arity + 1, arity)]


# ---------------------------------------------------------------- harnesses

JAVA_HELPERS = r"""
    static String[] splitTop(String s){
        java.util.List<String> out=new java.util.ArrayList<>();
        int d=0,st=0; boolean q=false;
        for(int i=0;i<s.length();i++){ char c=s.charAt(i);
            if(c=='"') q=!q;
            else if(!q&&(c=='['||c=='{')) d++;
            else if(!q&&(c==']'||c=='}')) d--;
            else if(!q&&c==','&&d==0){ out.add(s.substring(st,i)); st=i+1; } }
        if(st<s.length()) out.add(s.substring(st));
        return out.toArray(new String[0]);
    }
    static String inner(String s){ s=s.trim();
        if(s.startsWith("[")&&s.endsWith("]")) s=s.substring(1,s.length()-1);
        return s.trim(); }
    static String unq(String s){ s=s.trim();
        if(s.length()>1&&s.startsWith("\"")&&s.endsWith("\"")) s=s.substring(1,s.length()-1);
        return s; }
    static int[] pInts(String s){ String b=inner(s); if(b.isEmpty()) return new int[0];
        String[] p=splitTop(b); int[] r=new int[p.length];
        for(int i=0;i<p.length;i++) r[i]=Integer.parseInt(p[i].trim()); return r; }
    static int[][] pInts2(String s){ String b=inner(s); if(b.isEmpty()) return new int[0][];
        String[] p=splitTop(b); int[][] r=new int[p.length][];
        for(int i=0;i<p.length;i++) r[i]=pInts(p[i]); return r; }
    static String[] pStrs(String s){ String b=inner(s); if(b.isEmpty()) return new String[0];
        String[] p=splitTop(b); String[] r=new String[p.length];
        for(int i=0;i<p.length;i++) r[i]=unq(p[i]); return r; }
    static java.util.List<Integer> pIntList(String s){ int[] a=pInts(s);
        java.util.List<Integer> r=new java.util.ArrayList<>(); for(int x:a) r.add(x); return r; }
    static java.util.List<String> pStrList(String s){ String[] a=pStrs(s);
        return new java.util.ArrayList<>(java.util.Arrays.asList(a)); }
    static char[] pChars(String s){ String[] a=pStrs(s); char[] r=new char[a.length];
        for(int i=0;i<a.length;i++) r[i]=a[i].charAt(0); return r; }
    static char[][] pChars2(String s){ String b=inner(s); if(b.isEmpty()) return new char[0][];
        String[] p=splitTop(b); char[][] r=new char[p.length][];
        for(int i=0;i<p.length;i++) r[i]=pChars(p[i]); return r; }
    static String ser(Object o){
        if(o==null) return "null";
        if(o instanceof String) return "\"" + o + "\"";
        if(o instanceof Character) return "\"" + o + "\"";
        if(o instanceof Boolean) return o.toString();
        if(o instanceof int[]){ int[] a=(int[])o; StringBuilder sb=new StringBuilder("[");
            for(int i=0;i<a.length;i++){ if(i>0) sb.append(","); sb.append(a[i]); }
            return sb.append("]").toString(); }
        if(o instanceof char[]){ char[] a=(char[])o; StringBuilder sb=new StringBuilder("[");
            for(int i=0;i<a.length;i++){ if(i>0) sb.append(","); sb.append("\"").append(a[i]).append("\""); }
            return sb.append("]").toString(); }
        if(o instanceof double[]){ double[] a=(double[])o; StringBuilder sb=new StringBuilder("[");
            for(int i=0;i<a.length;i++){ if(i>0) sb.append(","); sb.append(a[i]); }
            return sb.append("]").toString(); }
        if(o instanceof Object[]){ Object[] a=(Object[])o; StringBuilder sb=new StringBuilder("[");
            for(int i=0;i<a.length;i++){ if(i>0) sb.append(","); sb.append(ser(a[i])); }
            return sb.append("]").toString(); }
        if(o instanceof java.util.List){ java.util.List<?> a=(java.util.List<?>)o;
            StringBuilder sb=new StringBuilder("[");
            for(int i=0;i<a.size();i++){ if(i>0) sb.append(","); sb.append(ser(a.get(i))); }
            return sb.append("]").toString(); }
        return o.toString();
    }
"""

JAVA_PARSE = {
    "integer": "Integer.parseInt(A[{i}].trim())",
    "long": "Long.parseLong(A[{i}].trim())",
    "double": "Double.parseDouble(A[{i}].trim())",
    "boolean": "Boolean.parseBoolean(A[{i}].trim())",
    "string": "unq(A[{i}])",
    "character": "unq(A[{i}]).charAt(0)",
    "integer[]": "pInts(A[{i}])", "integer[][]": "pInts2(A[{i}])",
    "string[]": "pStrs(A[{i}])", "character[]": "pChars(A[{i}])",
    "character[][]": "pChars2(A[{i}])",
    "list<integer>": "pIntList(A[{i}])", "list<string>": "pStrList(A[{i}])",
}

CPP_HELPERS = r"""
static string trimS(string s){size_t a=s.find_first_not_of(" \t\r\n");
  if(a==string::npos) return ""; size_t b=s.find_last_not_of(" \t\r\n"); return s.substr(a,b-a+1);}
static vector<string> splitTop(const string& s){vector<string> o;int d=0;bool q=false;size_t st=0;
  for(size_t i=0;i<s.size();i++){char c=s[i];
    if(c=='"') q=!q; else if(!q&&(c=='['||c=='{')) d++; else if(!q&&(c==']'||c=='}')) d--;
    else if(!q&&c==','&&d==0){o.push_back(s.substr(st,i-st)); st=i+1;}}
  if(st<s.size()) o.push_back(s.substr(st)); return o;}
static string innerS(string s){s=trimS(s);
  if(s.size()>=2&&s.front()=='['&&s.back()==']') s=s.substr(1,s.size()-2); return trimS(s);}
static string unq(string s){s=trimS(s);
  if(s.size()>=2&&s.front()=='"'&&s.back()=='"') s=s.substr(1,s.size()-2); return s;}
static vector<int> pInts(const string& s){string b=innerS(s); vector<int> r;
  if(b.empty()) return r; for(auto& p:splitTop(b)) r.push_back(stoi(trimS(p))); return r;}
static vector<vector<int>> pInts2(const string& s){string b=innerS(s); vector<vector<int>> r;
  if(b.empty()) return r; for(auto& p:splitTop(b)) r.push_back(pInts(p)); return r;}
static vector<string> pStrs(const string& s){string b=innerS(s); vector<string> r;
  if(b.empty()) return r; for(auto& p:splitTop(b)) r.push_back(unq(p)); return r;}
static vector<char> pChars(const string& s){vector<char> r; for(auto& x:pStrs(s)) r.push_back(x[0]); return r;}
static vector<vector<char>> pChars2(const string& s){string b=innerS(s); vector<vector<char>> r;
  if(b.empty()) return r; for(auto& p:splitTop(b)) r.push_back(pChars(p)); return r;}
static string ser(int v){return to_string(v);} 
static string ser(long long v){return to_string(v);} 
static string ser(bool v){return v?"true":"false";}
static string ser(double v){ostringstream o;o<<v;return o.str();}
static string ser(char v){return string("\"")+v+"\"";}
static string ser(const string& v){return "\""+v+"\"";}
template<class T> static string ser(const vector<T>& v){string o="[";
  for(size_t i=0;i<v.size();i++){if(i) o+=","; o+=ser(v[i]);} return o+"]";}
"""

CPP_PARSE = {
    "integer": "stoi(trimS(A[{i}]))", "long": "stoll(trimS(A[{i}]))",
    "double": "stod(trimS(A[{i}]))", "boolean": "(trimS(A[{i}])==\"true\")",
    "string": "unq(A[{i}])", "character": "unq(A[{i}])[0]",
    "integer[]": "pInts(A[{i}])", "integer[][]": "pInts2(A[{i}])",
    "string[]": "pStrs(A[{i}])", "character[]": "pChars(A[{i}])",
    "character[][]": "pChars2(A[{i}])",
    "list<integer>": "pInts(A[{i}])", "list<string>": "pStrs(A[{i}])",
}

CPP_TYPE = {
    "integer": "int", "long": "long long", "double": "double", "boolean": "bool",
    "string": "string", "character": "char", "integer[]": "vector<int>",
    "integer[][]": "vector<vector<int>>", "string[]": "vector<string>",
    "character[]": "vector<char>", "character[][]": "vector<vector<char>>",
    "list<integer>": "vector<int>", "list<string>": "vector<string>",
}


def gen_java(meta, user_code):
    name = meta["name"]
    args = []
    for i, p in enumerate(meta["params"]):
        tmpl = JAVA_PARSE.get(p["type"])
        if not tmpl:
            raise SystemExit(f"java: no parser for type {p['type']!r}")
        args.append(tmpl.format(i=i))
    return f"""import java.util.*;
import java.io.*;

{user_code}

public class Main {{
{JAVA_HELPERS}
    public static void main(String[] argv) throws Exception {{
        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
        List<String> L=new ArrayList<>(); String ln;
        while((ln=br.readLine())!=null) L.add(ln);
        int ar={len(meta['params'])};
        for(int c=0;c+ar<=L.size();c+=ar){{
            String[] A=new String[ar];
            for(int k=0;k<ar;k++) A[k]=L.get(c+k);
            Object out = new Solution().{name}({', '.join(args)});
            System.out.println(ser(out));
        }}
    }}
}}
"""


def gen_cpp(meta, user_code):
    name = meta["name"]
    args = []
    for i, p in enumerate(meta["params"]):
        tmpl = CPP_PARSE.get(p["type"])
        if not tmpl:
            raise SystemExit(f"cpp: no parser for type {p['type']!r}")
        args.append(tmpl.format(i=i))
    # LeetCode's C++ signatures take non-const references (vector<int>& nums), which
    # cannot bind to the temporary a parser returns. Materialize each argument into a
    # named local first.
    decls = "\n".join(f"        auto __a{i} = {e};" for i, e in enumerate(args))
    names = ", ".join(f"__a{i}" for i in range(len(args)))
    call = f"        cout << ser(s.{name}({names})) << \"\\n\";"
    return f"""#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <climits>
#include <cmath>
#include <numeric>
#include <functional>
using namespace std;

{CPP_HELPERS}

{user_code}

int main(){{
    vector<string> L; string ln;
    while(getline(cin, ln)) L.push_back(ln);
    size_t ar={len(meta['params'])};
    for(size_t c=0; c+ar<=L.size(); c+=ar){{
        vector<string> A(L.begin()+c, L.begin()+c+ar);
        Solution s;
{decls}
{call}
    }}
    return 0;
}}
"""


def gen_ts(meta, user_code):
    name = meta["name"]
    args = [f"JSON.parse(A[{i}])" for i in range(len(meta["params"]))]
    return f"""{user_code}

const __lines: string[] = require('fs').readFileSync(0, 'utf8')
  .split('\\n').filter((l: string) => l.trim() !== '');
const __ar = {len(meta['params'])};
for (let c = 0; c + __ar <= __lines.length; c += __ar) {{
  const A = __lines.slice(c, c + __ar);
  const out = ({name} as any)({', '.join(args)});
  console.log(JSON.stringify(out));
}}
"""


def gen_py(meta, user_code):
    name = meta["name"]
    args = [f"json.loads(A[{i}])" for i in range(len(meta["params"]))]
    body = "\n".join("    " + l if l.strip() else l for l in user_code.split("\n"))
    return f"""import json, sys

{user_code}

def __main():
    lines = [l for l in sys.stdin.read().split("\\n") if l.strip() != ""]
    ar = {len(meta['params'])}
    c = 0
    while c + ar <= len(lines):
        A = lines[c:c+ar]
        out = Solution().{name}({', '.join(args)})
        print(json.dumps(out, separators=(",", ":")))
        c += ar

__main()
"""


# ---------------------------------------------------------------- run

def build_and_run(lang, src, stdin_text, work):
    """Returns (compiled, stdout, stderr, compile_error)."""
    if lang == "java":
        p = os.path.join(work, "Main.java")
        open(p, "w").write(src)
        c = subprocess.run(["javac", "-d", work, p], capture_output=True, text=True, timeout=120)
        if c.returncode:
            return False, "", "", c.stderr.strip()
        r = subprocess.run(["java", "-cp", work, "Main"], input=stdin_text,
                           capture_output=True, text=True, timeout=30)
        return True, r.stdout, r.stderr, None
    if lang == "cpp":
        p = os.path.join(work, "main.cpp")
        open(p, "w").write(src)
        exe = os.path.join(work, "a.out")
        c = subprocess.run(["clang++", "-std=c++17", "-O1", "-o", exe, p],
                           capture_output=True, text=True, timeout=180)
        if c.returncode:
            return False, "", "", c.stderr.strip()
        r = subprocess.run([exe], input=stdin_text, capture_output=True, text=True, timeout=30)
        return True, r.stdout, r.stderr, None
    if lang == "typescript":
        p = os.path.join(work, "main.ts")
        open(p, "w").write(src)
        r = subprocess.run(["npx", "-y", "tsx", p], input=stdin_text,
                           capture_output=True, text=True, timeout=180, cwd=work)
        if r.returncode and not r.stdout.strip():
            return False, "", "", (r.stderr or "").strip()
        return True, r.stdout, r.stderr, None
    if lang == "python3":
        p = os.path.join(work, "main.py")
        open(p, "w").write(src)
        c = subprocess.run(["python3", "-m", "py_compile", p], capture_output=True, text=True)
        if c.returncode:
            return False, "", "", c.stderr.strip()
        r = subprocess.run(["python3", p], input=stdin_text, capture_output=True,
                           text=True, timeout=30)
        if r.returncode and not r.stdout.strip():
            return True, r.stdout, r.stderr, None
        return True, r.stdout, r.stderr, None
    raise SystemExit(f"unknown lang {lang}")


def norm(s):
    """Structural comparison so [0,1] and [0, 1] match."""
    s = (s or "").strip()
    try:
        return json.dumps(json.loads(s), sort_keys=False, separators=(",", ":"))
    except Exception:
        return s


GENERATORS = {"java": gen_java, "cpp": gen_cpp, "typescript": gen_ts, "python3": gen_py}

_ERR_LINE = re.compile(r"(?:^|[\s(])(/[^\s:\"]+?\.(?:java|cpp|ts|py))[:\"]?(?:,\s*line\s+|:)(\d+)")


def remap_errors(text, offset):
    """Compile errors point into the GENERATED file. The learner never saw it, so a
    raw 'Main.java:7' is not just unhelpful -- it implies they wrote something they
    did not. Rewrite every file:line to their own line numbering, and drop the path."""
    if not text:
        return text
    out = []
    for line in text.split("\n"):
        def sub(m):
            n = int(m.group(2)) - offset
            return (f" your code line {n}" if n >= 1
                    else " [test harness, not your code]")
        line = _ERR_LINE.sub(sub, line)
        # compilers echo the source with a line-number gutter ("  52 | return nums").
        # That number is the harness's; shift it to the learner's file.
        g = re.match(r"^(\s*)(\d+)(\s*\|)", line)
        if g:
            n = int(g.group(2)) - offset
            line = f"{g.group(1)}{n if n >= 1 else '?'}{g.group(3)}" + line[g.end():]
        out.append(line)
    return "\n".join(out)


LEDGER = os.path.join(ROOT, "state", "oa-attempts.json")


def record(entry):
    """Append to the attempt ledger. Holds the learner's own code, so it is gitignored
    and lives only in the private vault -- see .githooks/personal-paths."""
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    data = {"schema": 1, "attempts": []}
    if os.path.exists(LEDGER):
        try:
            data = json.load(open(LEDGER))
        except (json.JSONDecodeError, OSError):
            data = {"schema": 1, "attempts": [], "_note": "previous file was unreadable"}
    prior = [a for a in data["attempts"] if a["problem"] == entry["problem"]]
    entry["attempt"] = len(prior) + 1
    data["attempts"].append(entry)
    with open(LEDGER, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    return entry["attempt"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--lang", required=True, choices=LANGS)
    ap.add_argument("--file", required=True, help="the learner's code (LeetCode stub, filled in)")
    ap.add_argument("--tests", help="JSON list of {input:[...], expected:...}")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep the scratch dir (debugging)")
    ap.add_argument("--record", action="store_true",
                    help="append this attempt to state/oa-attempts.json (gitignored)")
    ap.add_argument("--elapsed", type=int, help="seconds the learner spent, from the editor")
    a = ap.parse_args()

    user_code = open(a.file).read()
    q = fetch_problem(a.slug)
    meta = q["meta"]

    bad = check_supported(meta)
    if bad:
        out = {"ok": False, "unsupported": bad, "slug": a.slug}
        print(json.dumps(out, indent=1) if a.json else f"UNSUPPORTED\n  {bad}")
        return 2

    if a.tests:
        cases = json.load(open(a.tests))
    else:
        cases = split_examples(q["exampleTestcases"], len(meta["params"]))

    src = GENERATORS[a.lang](meta, user_code)
    # user_code is inserted verbatim exactly once, so this is exact.
    user_offset = src[:src.index(user_code)].count("\n")
    stdin_text = "\n".join("\n".join(c["input"]) for c in cases) + "\n"

    work = tempfile.mkdtemp(prefix=f"oa-{a.slug}-")
    t0 = time.time()
    try:
        compiled, out, err, cerr = build_and_run(a.lang, src, stdin_text, work)
    finally:
        if a.keep:
            print(f"(scratch kept at {work})", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
    elapsed = round(time.time() - t0, 2)

    cerr = remap_errors(cerr, user_offset)
    err = remap_errors(err, user_offset)

    if not compiled:
        res = {"ok": False, "compiled": False, "compile_error": cerr, "slug": a.slug,
               "lang": a.lang, "elapsed_s": elapsed}
        if a.record:
            res["attempt"] = record({
                "problem": a.slug, "lang": a.lang, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "elapsed_s": a.elapsed, "compiled": False, "verdict": "compile-error",
                "compile_error": (cerr or "")[:600], "passed": 0, "gradable": 0,
                "failed_on": [], "code": user_code})
        if a.json:
            print(json.dumps(res, indent=1))
        else:
            print("COMPILED          no\n\nCOMPILE ERROR")
            print("\n".join("  " + l for l in (cerr or "").split("\n")[:25]))
        return 1

    got = [l for l in out.split("\n") if l.strip() != ""]
    results, passed, gradable = [], 0, 0
    for i, c in enumerate(cases):
        actual = got[i] if i < len(got) else None
        exp = c.get("expected")
        if exp is None:
            results.append({"input": c["input"], "actual": actual, "expected": None,
                            "pass": None})
        else:
            gradable += 1
            ok = actual is not None and norm(actual) == norm(str(exp))
            passed += 1 if ok else 0
            results.append({"input": c["input"], "actual": actual, "expected": exp,
                            "pass": ok})

    verdict = ("no-expected-outputs" if gradable == 0
               else "accepted" if passed == gradable else "wrong-answer")
    res = {"ok": True, "compiled": True, "slug": a.slug, "lang": a.lang,
           "verdict": verdict, "passed": passed, "gradable": gradable,
           "total_cases": len(cases), "elapsed_s": elapsed,
           "stderr": (err or "").strip()[:800] or None, "results": results}

    if a.record:
        res["attempt"] = record({
            "problem": a.slug, "lang": a.lang, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_s": a.elapsed, "compiled": True, "verdict": verdict,
            "compile_error": None, "passed": passed, "gradable": gradable,
            "failed_on": [" | ".join(r["input"]) for r in results if r["pass"] is False],
            "code": user_code})

    if a.json:
        print(json.dumps(res, indent=1))
        return 0 if verdict in ("accepted", "no-expected-outputs") else 1

    print(f"COMPILED          yes")
    if gradable:
        print(f"TESTS             {passed}/{gradable} passed")
    else:
        print(f"TESTS             {len(cases)} run (no expected outputs supplied)")
    for r in results:
        mark = {True: "pass", False: "FAIL", None: " run"}[r["pass"]]
        print(f"  {mark}  input: {' | '.join(r['input'])[:56]:58s} -> {str(r['actual'])[:26]}"
              + (f"   expected: {r['expected']}" if r["pass"] is False else ""))
    if res["stderr"]:
        print("\nSTDERR\n" + "\n".join("  " + l for l in res["stderr"].split("\n")[:10]))
    print(f"\nVERDICT           {verdict}   ({elapsed}s)")
    return 0 if verdict in ("accepted", "no-expected-outputs") else 1


if __name__ == "__main__":
    sys.exit(main())
