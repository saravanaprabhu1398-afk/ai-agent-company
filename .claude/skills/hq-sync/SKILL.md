---
name: hq-sync
description: Refresh the Agent Company HQ office page with live GitHub data. Use when the CEO says "sync HQ", "refresh HQ" or "update the office", and at the end of every orchestrator phase.
---
# Sync HQ

The HQ page (https://claude.ai/artifact/BkdvrmKFBFGDyuHBerFpHy) reads one database document, `hq/state`,
built from this repo's GitHub data.

1. Build the snapshot (uses your `gh` login):
   ```bash
   python3 office/github_snapshot.py > "$TMPDIR/hq-state.json"
   ```
2. Read the current document to get its version: ArtifactData `get`, url above, collection `hq`, doc_id `state`.
3. Replace it: ArtifactData `set`, collection `hq`, doc_id `state`, `file_path` = the JSON file,
   `if_version` = the version from step 2 (omit it only if the document doesn't exist yet).
4. Reply with one line: phase, open issues, open PRs, and anything waiting on the CEO.

The page updates by itself for anyone who has it open. If the script fails, report the error; don't write partial data.
