# Evidence, stages and expansion (3.3)

Read before scaffolding or rendering a user video. Use schema 5 and the user-stage-review reference linked directly from SKILL.md. These records are an agent's working files, not extra technical questions for the user. Recover real earlier replies and inputs; never ask the user to calculate hashes or populate JSON. A record is auditable evidence, not authentication of a fabricated message or a proof of aesthetic quality.

## One contract at every entry

`check_brief.py` is the authority. The Python scaffold and JavaScript renderers invoke it; both bundled projects contain the same checker and helpers. Python 3 is required alongside the selected renderer. Set `MV_PYTHON` to a real interpreter path when the host has no `python3`/`python` command. Do not silently disable the gate if Python or evidence is unavailable.

Use `request_mode:"plan-only"` for a planning task. `phase:"discover"`, `"proposal"` and `"awaiting-confirmation"` cannot produce a user video even when an old production boolean is true. After actual direction acceptance enter `"design"` for static designs and the complete script. Only after the user accepts that package enter `"study"`/`"prototype"` for a bounded sample; after sample acceptance enter `"animatic"` for the whole-scope rough cut, then await its acceptance before full production. `prototype.duration` is a separate bound, including when the user already authorized an eventual full MV. Full/repair rendering needs `phase:"full"` or `"repair"`, full scope, all three artifact-specific user stage decisions and the separate technical pilot receipt below. Do not switch stages to evade a missing decision.

## Bind actual inputs

Hash bytes with SHA-256. Store local inputs as `{path,sha256}` records; the scaffold verifies and copies explicitly referenced inputs into the new project's assets. Moving identical bytes does not change content acceptance. Audio is `music.audio` plus `music.audio_sha256`; the renderers use that selected recording automatically and reject a different `--audio` value. Missing declared audio blocks the entry. A genuinely provisional silent study must be stated as such rather than naming a nonexistent recording.

For a lyrical song, `song_reading.lyrics_document` points to the actual canonical JSON, with nonempty `lines` or `cues`, each containing a unique `id` and the actual `text`. Preserve repeated sung occurrences with separate IDs. Import a supplied SRT/LRC or use:

```bash
python3 <skill>/scripts/prepare_lyrics.py <provided-lyrics.txt> --out <project>/data/canonical.json
```

This creates IDs, not timing or a claim of independently verified lyrics. `song_reading.evidence` contains `{cue_ids:[...],observation:"..."}` and must cite existing IDs. Null entries, empty observations and nonexistent lines fail. Meaning still needs thoughtful reading of the complete text and recording.

Sources are structured `{id,url,kind,attribution,checked_at,summary,snapshot:{path,sha256}}`. For a claim of documented artist intent use `kind:"artist_primary"`, the checked primary URL and a local snapshot of the material actually read. Prefer a short relevant extract/paraphrase within host quotation limits; do not store a whole copyrighted article unnecessarily. A fan interpretation is not an artist statement. `lyrics_status:"verified"` needs checked source evidence; supplied text is `"provided"`. The script does not browse, endorse a source or judge whether an interpretation follows from it.

## Bind the user's actual acceptance

After the real reply to the concrete recap, create a small record with `origin:"user-message"`, `message_id`, `user_reply`, `recap_id` and `accepted_content_sha256`. Use the actual host message reference or a clear conversation timestamp when IDs are unavailable. Preserve the actual reply, not an agent-written substitute. Link it from `content_confirmation.record:{path,sha256}`. Keep `summary`, `user_evidence` and `content_sha256` consistent. An unrelated “go ahead” cannot become acceptance by being placed in this file.

Digest version 2 uses typed binary64 number normalization so `160` and `160.0`, exponents and negative zero agree across Python and JavaScript. Use strings for large identifiers that are not exactly representable in binary64. The digest binds canonical lyric/audio identities and selected meaning in addition to content/cast/progression. Change of recording, lyric text or content invalidates old acceptance; routine implementation/palette choices do not trigger another content interview.

For an unchanged accepted 3.1 brief, `migrate_confirmation.py <old-brief> --out <new-brief>` verifies the legacy digest and converts its format. It preserves authorization and refuses stale/missing consent. It does not invent new source, message, audio, stage or pilot evidence. Recover those from actual existing work; if unavailable, leave the relevant gate pending.

## Verify a representative sample before expanding

Select a sample containing the project's hard requirements: reaction/contact/turn for relevant character work; explicit word-to-object construction and joins for semantic typography; material or spatial behavior for other styles. Use the actual selected assets and fonts. Inspect encoded consecutive frames and the soundtrack. Record concrete timestamped observations, not a universal taste score.

The project initializes relevant checks: text for visible lyrics, glyphs for Chinese text, meaning for lyrical work, story for narrative progression, and acting for a cast. Add relevant contact/transition/identity checks. Explain a valid not-applicable case; never use it to hide an unmet selected requirement. Review callbacks and emotional information as well as technical artifacts.

```bash
python3 <skill>/scripts/project_contracts.py check --project <project> --stage prototype
python3 <skill>/scripts/project_contracts.py promote --project <project>
```

`promote` requires the observed prototype review, actual encoded target, runtime receipt and current source/design fingerprint. It saves a versioned `prototype-pass` receipt and immutable review copies. It grants no user authorization and cannot promote a tool self-test. This evidence alone never opens full production. Only after actual design/script, sample and whole-scope animatic acceptance and full scope may the full stage open. New source/design requires a representative recheck; a short range of the full timeline can be the sample. Previous receipts and clips remain intact. Reuse actual acceptance of unchanged artifacts; routine in-scope fixes need technical rechecks. Never omit the required later user-stage stop or turn a technical pass into user taste acceptance.

## Full lyrics and actual glyphs

For `lyrics.mode:"full"`/`"full-lines"`, `lyrics.display_document:{path,sha256}` contains ordered `cues` with canonical `line_id` (or `id`), identical text, start and end. Missing/duplicated/reordered lines, changed text, overlaps and empty cue sets fail. Full production requires `alignment_status:"ear_checked"` and truthful `alignment_evidence`. Supplied timing is not automatically checked singing alignment. The renderers load this accepted cue document into the overlay; a stale generated JavaScript cue file is not the text authority.

For Chinese full lyrics select `lyrics.font:{path,sha256,family}`, then:

```bash
python3 <skill>/scripts/font_check.py --font <font-file> --lyrics <canonical.json> --out <glyph-report.json>
```

Bind the result as `lyrics.glyph_review`. This checks the font's actual cmap against the current text, not merely a font-family name. The native adapter registers the selected local font. Keep its license in the project. Still inspect rendered glyph shapes, wrapping, contrast, face/hand occlusion and reading time; successful coverage is not visual acceptance.

## Honest validation scope

The original samples and synthetic regressions verify specific behavior. A Chinese instrumental-caption test is not a Chinese singing-alignment test. A 30-second scenic example is not evidence of a complete real-song relationship MV. Windows/browser/p5/other engines need their own execution evidence. Keep those states in `assets/capability-matrix.json`; do not upgrade an untested capability because another test passed.
