#!/usr/bin/env python3
"""Actions stats for the repos in config.js: volume, queue wait, saturation.

usage: ci-stats.py [--since 6h|2026-10-23T18:00:00Z] [--slots 20] [--repos owner/a owner/b]
"""
import argparse, base64, json, re, statistics as st, subprocess, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone


def gh(*args):
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else ""


def lines(out):
    return [json.loads(l) for l in out.splitlines() if l.strip()]


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def since_arg(v):
    m = re.fullmatch(r"(\d+)([hd])", v)
    if not m:
        return v
    delta = timedelta(**{"hours" if m[2] == "h" else "days": int(m[1])})
    return (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def allowlist():
    out = gh("api", "repos/bradfordwagner/renovate/contents/config.js", "-q", ".content")
    return re.findall(r'"(bradfordwagner/[^"]+)"', base64.b64decode(out).decode())


def repo_jobs(repo, since):
    runs = lines(gh("api", "--paginate", f"repos/{repo}/actions/runs?created=>={since}&per_page=100",
                    "-q", ".workflow_runs[]|{id,name,event,conclusion}"))
    jobs = []
    for r in runs:
        for j in lines(gh("api", "--paginate", f"repos/{repo}/actions/runs/{r['id']}/jobs?per_page=100&filter=latest",
                          "-q", ".jobs[]|{name,conclusion,created_at,started_at,completed_at}")):
            if j["started_at"] and j["completed_at"] and j["conclusion"] != "skipped":
                jobs.append(dict(name=j["name"], conclusion=j["conclusion"], arm="arm64" in j["name"],
                                 c=ts(j["created_at"]), s=ts(j["started_at"]), e=ts(j["completed_at"])))
    return repo, runs, jobs


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))]


def summ(label, v):
    if v:
        print(f"{label}: n={len(v)} median={st.median(v)/60:.1f}m mean={st.mean(v)/60:.1f}m "
              f"p90={pct(v, .9)/60:.1f}m max={max(v)/60:.1f}m")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="6h")
    ap.add_argument("--slots", type=int, default=20, help="concurrent job cap (Free plan: 20)")
    ap.add_argument("--repos", nargs="*")
    a = ap.parse_args()
    since = since_arg(a.since)
    repos = a.repos or allowlist()
    if not repos:
        sys.exit("no repos: could not read config.js")

    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda r: repo_jobs(r, since), repos))
    runs = [r for _, rs, _ in results for r in rs]
    jobs = [j for _, _, js in results for j in js]
    if not jobs:
        sys.exit(f"no Actions jobs since {since}")

    merged = [l.strip().strip('"') for l in gh("search", "prs", "--author", "app/bradfordwagner-renovate", "--owner", "bradfordwagner",
                      "--state", "closed", "--merged", "--merged-at", f">={since}", "--limit", "200",
                      "--json", "repository", "-q", ".[]|.repository.nameWithOwner").splitlines()]
    merged = [m for m in merged if m in repos]
    print(f"since {since}; {len(repos)} repos")
    print(f"runs {len(runs)}, jobs {len(jobs)}, renovate PRs merged {len(merged)}"
          + (f", {len(runs)/len(merged):.1f} runs per merge" if merged else ""))
    print("runs by workflow:", dict(Counter(r["name"] for r in runs)))
    print("runs by event:", dict(Counter(r["event"] for r in runs)))
    print("run conclusions:", dict(Counter(r["conclusion"] for r in runs)))
    print("job conclusions:", dict(Counter(j["conclusion"] for j in jobs)))
    print("runs per repo:", dict(Counter(r.split("/")[1] for r, rs, _ in results for _ in rs).most_common()))

    q = [j["s"] - j["c"] for j in jobs]
    d = [j["e"] - j["s"] for j in jobs]
    summ("queue wait, all jobs", q)
    summ("queue wait, arm64", [j["s"] - j["c"] for j in jobs if j["arm"]])
    summ("queue wait, amd64", [j["s"] - j["c"] for j in jobs if not j["arm"]])
    summ("job duration", d)
    print(f"job-minutes run {sum(d)/60:.0f}, queued {sum(q)/60:.0f}, queued:run {sum(q)/sum(d):.1f}x")

    ev = sorted([(j["s"], 1) for j in jobs] + [(j["e"], -1) for j in jobs])
    cur = peak = 0
    for _, x in ev:
        cur += x
        peak = max(peak, cur)
    span = max(j["e"] for j in jobs) - min(j["c"] for j in jobs)
    print(f"peak concurrent jobs {peak} of {a.slots}; window {span/3600:.1f}h; "
          f"slot utilisation {sum(d)/(span*a.slots)*100:.0f}%; floor at full use {sum(d)/a.slots/3600:.1f}h")


if __name__ == "__main__":
    main()
