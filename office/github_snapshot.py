#!/usr/bin/env python3
"""Build the Agent Company HQ snapshot from GitHub.

Reads the repo's issues, PRs, recent activity, docs status and releases with the
`gh` CLI (your existing login) and prints one JSON object. The HQ page renders it
after the snapshot is written to the page's database (see office/README.md).

Usage: python3 office/github_snapshot.py [owner/repo] > /tmp/hq-state.json
"""
import base64
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROLE_LABELS = {
    "role:pm": "pm", "role:ux": "ux", "role:architect": "arch",
    "role:backend": "be", "role:frontend": "fe", "role:qa": "qa",
    "role:devops": "devops", "role:security": "sec", "role:sre": "sre",
    "role:docs": "docs",
}


def gh(*args, check=True):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and out.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout if out.returncode == 0 else None


def gh_json(*args, check=True):
    raw = gh(*args, check=check)
    return json.loads(raw) if raw else None


def role_of(labels, fallback=None):
    for name in labels:
        if name in ROLE_LABELS:
            return ROLE_LABELS[name]
    return fallback


def doc_status(repo, path):
    """'missing' | 'template' | 'draft' | 'approved' for a doc on the default branch."""
    data = gh_json("api", f"repos/{repo}/contents/{path}", check=False)
    if not data or "content" not in data:
        return "missing"
    text = base64.b64decode(data["content"]).decode("utf-8", "replace")
    if re.search(r"^>?\s*.*Status:\s*Approved\b", text, re.M | re.I):
        return "approved"
    body = [l for l in text.splitlines()
            if l.strip() and not l.lstrip().startswith(("#", ">", "|"))]
    return "template" if len(body) < 3 else "draft"


def checks_state(rollup):
    if not rollup:
        return "none"
    states = [(c.get("conclusion") or c.get("state") or c.get("status") or "").upper() for c in rollup]
    if any(s in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT") for s in states):
        return "fail"
    if any(s in ("", "PENDING", "IN_PROGRESS", "QUEUED", "EXPECTED") for s in states):
        return "pending"
    return "pass"


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
    since = datetime.now(timezone.utc) - timedelta(days=14)

    raw_issues = gh_json("issue", "list", "-R", repo, "--state", "all", "--limit", "100",
                         "--json", "number,title,state,labels,updatedAt,closedAt,createdAt")
    issues = []
    for i in raw_issues:
        labels = [l["name"] for l in i["labels"]]
        if i["state"] == "CLOSED" and i["closedAt"] and datetime.fromisoformat(i["closedAt"].replace("Z", "+00:00")) < since:
            continue
        issues.append({"number": i["number"], "title": i["title"][:90], "state": i["state"],
                       "labels": labels, "role": role_of(labels), "updatedAt": i["updatedAt"],
                       "closedAt": i["closedAt"]})
    issue_roles = {i["number"]: i["role"] for i in issues}

    raw_prs = gh_json("pr", "list", "-R", repo, "--state", "all", "--limit", "50",
                      "--json", "number,title,state,isDraft,reviewDecision,labels,headRefName,"
                                "updatedAt,mergedAt,statusCheckRollup,closingIssuesReferences")
    prs = []
    for p in raw_prs:
        labels = [l["name"] for l in p["labels"]]
        closes = [c["number"] for c in (p.get("closingIssuesReferences") or [])]
        if p["state"] != "OPEN" and (p["mergedAt"] or p["updatedAt"]) < since.isoformat():
            continue
        role = role_of(labels) or next((issue_roles.get(n) for n in closes if issue_roles.get(n)), None)
        prs.append({"number": p["number"], "title": p["title"][:90], "state": p["state"],
                    "isDraft": p["isDraft"], "reviewDecision": p["reviewDecision"] or "",
                    "labels": labels, "branch": p["headRefName"], "role": role or "be",
                    "checks": checks_state(p.get("statusCheckRollup")), "closes": closes,
                    "updatedAt": p["updatedAt"], "mergedAt": p["mergedAt"]})
    pr_roles = {p["number"]: p["role"] for p in prs}
    pr_titles = {p["number"]: p["title"][:60] for p in raw_prs}

    events = []
    for e in gh_json("api", f"repos/{repo}/events?per_page=40", check=False) or []:
        # GitHub can trim event payloads; skip an event we can't read instead of failing the sync.
        try:
            t, pl, who, text = e["type"], e.get("payload", {}), "orch", None
            if t == "IssuesEvent":
                n = pl["issue"]["number"]
                labels = [l["name"] for l in pl["issue"].get("labels", [])]
                who = "lead" if pl["action"] == "opened" and "type:bug" not in labels else (issue_roles.get(n) or "qa")
                text = f"Issue #{n} {pl['action']}: {pl['issue'].get('title', '')[:60]}"
            elif t == "PullRequestEvent":
                # The events API sends a slim pull_request (number, base, head; no title or merged flag)
                pr = pl.get("pull_request") or {}
                n = pl.get("number") or pr.get("number")
                action = "merged" if pl.get("action") == "closed" and pr.get("merged") else pl.get("action", "updated")
                who = "ceo" if action == "merged" else pr_roles.get(n, "be")
                title = pr.get("title") or pr_titles.get(n, "")
                text = f"PR #{n} {action}" + (f": {title[:60]}" if title else "")
            elif t == "PullRequestReviewEvent":
                n = pl["pull_request"]["number"]
                state = (pl.get("review") or {}).get("state", "submitted")
                who, text = "rev", f"Review on PR #{n}: {state.lower().replace('_', ' ')}"
            elif t == "IssueCommentEvent":
                n = pl["issue"]["number"]
                who, text = issue_roles.get(n) or pr_roles.get(n) or "orch", f"Comment on #{n}"
            elif t == "PushEvent":
                ref = pl.get("ref", "").replace("refs/heads/", "")
                count = pl.get("size", len(pl.get("commits", [])))
                who = "devops" if ref == "main" else "be"
                text = f"Pushed {count} commit(s) to {ref}"
            elif t == "CreateEvent" and pl.get("ref_type") == "branch":
                who, text = "orch", f"Branch created: {pl['ref']}"
            elif t == "ReleaseEvent":
                who, text = "devops", f"Release {pl['release']['tag_name']} {pl.get('action', '')}".strip()
        except (KeyError, TypeError, AttributeError) as err:
            print(f"skipped {e.get('type')} event {e.get('id')}: missing {err}", file=sys.stderr)
            continue
        if text and pl.get("action") not in ("labeled", "unlabeled"):
            events.append({"id": e["id"], "at": e["created_at"], "who": who, "type": t, "text": text})

    release = gh_json("api", f"repos/{repo}/releases/latest", check=False)
    snapshot = {
        "repo": repo,
        "url": f"https://github.com/{repo}",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "docs": {
            "prd": doc_status(repo, "docs/PRD.md"),
            "ux": doc_status(repo, "docs/ux.md"),
            "architecture": doc_status(repo, "docs/architecture.md"),
        },
        "issues": issues,
        "prs": prs,
        "events": events,
        "release": {"tag": release["tag_name"], "at": release["published_at"]} if release and "tag_name" in release else None,
    }
    json.dump(snapshot, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
