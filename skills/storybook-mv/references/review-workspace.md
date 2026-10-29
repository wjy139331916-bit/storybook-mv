# One review workspace, existing user stops

Use `scripts/review_workspace.py` to organize actual artifacts and derive the current stage. It removes routine JSON/hash work; it does not decide whether a real user accepted the result. Keep the direction → design/script → sample → whole rough cut → fine production workflow. Do not ask the user about package fields.

## Present the design

After direction acceptance, create the actual design images under the selected asset policy, a complete-scope script and visual specification. Then run:

```bash
python3 <skill>/scripts/review_workspace.py --project <project> present --stage design --revision design-r1 --proposal PROPOSAL.md --script plan/script.json --visual-spec visual-spec.json --frame out/design/key-01.png --frame out/design/key-02.png --pilot-range 48:60 --objective "Inspect the selected hard transition and action" --limit "Timing is provisional until checked against the chosen recording."
```

Use the actual planned interval, objectives and limitations; the numbers are examples, not defaults. `--frame` and `--limit` may repeat. The helper validates artifacts, retains a revisioned package, writes an offline `review.html` and updates `plan/STATUS.md` plus machine-readable `plan/status.json`. It never fills later acceptance or starts rendering. Existing revisions are preserved.

The page contains readable full-scope script, actual design frames, revision, known limits and the immediate next step. Images/video are embedded with no external requests (default 64 MiB budget, explicitly adjustable with `--max-embed-mb`). For a long review use the agreed lightweight export, not a finished high-resolution master. Respect the host's persistence and preview policy. If HTML is not previewable, display its actual images/video and readable script directly; record the real message where the whole package was shown. A page path, inaccessible link or source JSON is not a completed presentation.

End the turn and wait for the actual user. Do not make later shots in the background.

## Present the actual sample or rough cut

Use the native renderer's actual report, or inspect another engine's actual video while retaining the source interval from its render command:

```bash
python3 <skill>/scripts/review_workspace.py --project <project> inspect-video --stage prototype --video out/pilot/clip.mp4 --range 48:60 --out out/pilot/inspection-r1.json
python3 <skill>/scripts/review_workspace.py --project <project> present --stage prototype --revision pilot-r1 --video out/pilot/clip.mp4 --render-report out/pilot/inspection-r1.json --review out/pilot/observed-review.json --limit "State the actual remaining limitations."
```

The report requires a real encoded clip, checks complete decode and duration, retains the source range and selected audio digest, and measures the optional audio comparison. Ambiguous periodic/silent audio is not certified; listen to the relevant anchors. Never manufacture an audio-start or production-stage value for an unrelated clip. The presentation gate independently compares sample duration/range with the complete accepted pilot interval and checks the actual aspect. Partial repair exports are not a replacement for presenting the complete planned pilot.

For a preview host without MP4/H.264 playback, add `--webm-preview` to `present`. It creates and decodes a same-dimension/timeline WebM alternative, binds its original-video digest and retains the master for download. Account for extra encoding time and embedded size; this is a codec preview, not a new creative revision or a substitute for checking the original encoded output. Verify loaded frames and actual playback in the destination browser, not merely the existence of a `<video>` element. Chinese UI needs a Chinese-capable environment font; the tool does not bundle a font binary.

For animatic use `--stage animatic`, an actual whole-scope rough video and its report/review. Retain the actual recording, source range `[0, target duration]`, selected aspect and rough fidelity. The page's timepoint feedback export is bound to the video/package revision and is feedback only; it does not become user acceptance. For substantive design/style changes, show the affected revision at the existing review point.

The export uses the existing viewer-note schema accepted by `scripts/review_notes.py`. Import into a new review revision, preserve prior issues and triage the user's observations; exported point notes start as minor observations, not automatic decisions about severity or acceptance.

## Record the real decision

After reading the actual user reply, save its exact text in a local project file. Identify its real message and the message presenting the complete package. Use:

```bash
python3 <skill>/scripts/review_workspace.py --project <project> accept --stage design --reply-file plan/replies/design-r1.txt --message-id <actual-reply-reference> --presented-message-id <actual-presentation-reference> --advance
```

The helper fills only mechanical fields from the current package and validates the artifact-specific decision. `--advance` changes only to the immediate next phase; it does not execute that phase or accept unseen work. Without that flag the phase stays unchanged. Do not call this command for a question, revision request, partial-image preference or missing reply. Technical records cannot authenticate a fabricated message or infer what the user meant.

An explicit named review waiver uses `--decision waived --waiver-review <actual-self-review.json>` and retains the user's limited delegation. The file contains a named `reviewer` and actual `observations`; no bare skip flag is sufficient. Never propose extra waivers just to speed up a normal project.

## Resume and hand off

```bash
python3 <skill>/scripts/review_workspace.py --project <project> status
python3 <skill>/scripts/review_workspace.py --project <project> handoff
```

`status` derives the highest user-authorized stage from current artifact identities and actual recorded decisions; execution problems remain separate. `handoff` also refreshes the concise status card with phase, revisions, pending issues and known limits. These commands never manufacture acceptance. Transfer the complete skill/project decisions, actual packages and inputs under the host's authorized scope. A receiving agent reads the status card and verifies its underlying records rather than restarting the interview or trusting a stale “approved” label.
