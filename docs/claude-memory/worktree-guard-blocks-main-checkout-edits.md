---
name: worktree-guard-blocks-main-checkout-edits
description: "A worktree session's Edit tool refuses files in the main checkout and nothing in the app lifts it; tell the user and ask before writing there through the shell"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6511c3df-78a7-4bba-89a6-b9c3e7df41f4
  modified: 2026-10-31T19:28:03.325Z
---

From a session that starts in a worktree (2026-10-31), the Edit tool refuses every file
in the main checkout, saying the edit "may corrupt the user's primary working copy".
`change_directory` is refused too. `request_directory` grants the folder and says to
edit at that path, but Edit still refuses. The environment even reported the session had
moved to the main checkout, and Edit refused anyway. Shell commands aren't blocked.

**Why:** the user approved the beneath fix in the main checkout, but had not been told
about the guard, so that approval didn't cover going around it. Told plainly, they chose
"use the shell" for that job.

**How to apply:** this project often has to land work there, because the songs and the
uncommitted `.beats` support live only in the main checkout (see
[[check-a-songs-grid-before-choreographing]] and [[shipped-grid-audit-2026-10-30]]). Say
up front that the change will hit the guard, and ask whether to use the shell or a
session started in the main checkout. A yes covers that one job, not the next one.
Other sessions may be writing there too, so check `ps` before an offline build or test
run, and run the last build after they stop.
