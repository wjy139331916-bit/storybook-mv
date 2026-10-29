# Understand the song before inventing its pictures

Use the actual chosen recording and supplied/verified lyric text. A song title or model memory is not enough to assert its words, story, speaker or authorial intention. Instrumental music and explicitly non-lyrical tasks still need their actual musical progression understood, but do not invent lyrics to analyze.

## Establish what can be known

1. Confirm artist, title and relevant version (studio/live/cover/edit). Preserve the source/file identity. Do not assign another version's duration or lyric timing.
2. Read the complete available lyrics from the user's file or a checked attributable source. Mark supplied text as supplied; mark independent verification only when performed. Keep canonical text separate from recognition/alignment drafts. Do not reconstruct missing lines from memory.
3. Read across verses/choruses, pronouns, turning points, repeated images and the ending. Record cue/line IDs and paraphrases supporting the proposed theme. Do not interpret every line in isolation or infer a plot solely from the title.
4. When making factual claims about the song's creation or an artist's stated intent, check primary material where available: the artist's own interview/explanation, official release notes or attributable original material. A fan comment, search snippet or repeated blog claim is not the artist's statement. Do not force a quota of “mainstream interpretations.”

If factual evidence is missing, say what is unknown and obtain the missing version/text or continue only with a clearly labelled provisional discussion. Voting among guesses does not establish a fact. Keep retrieved lyric quotations within applicable host limits; prefer cue IDs and paraphrases. Store authorized lyric/audio files in the project, not the reusable skill/public examples.

## Separate three kinds of meaning

| Kind | How to present it |
|---|---|
| Documented artist intent | Attribute the checked statement and link/source; explain its relevance without inventing missing intent |
| Textual interpretation | “Based on these recurring images/changes, one supported reading is…”; keep inference and confidence explicit |
| User adaptation | “For this MV we can use this personal/fictional viewpoint…”; it is a creative choice, not proof of the artist's original purpose |

A song can support more than one defensible reading. Do not promise to discover one objectively unique meaning when no such evidence exists. A minor uncertainty need not stop all discussion; an uncertainty that changes the relationship, emotional arc, subject or ending must be resolved with the user before production.

## Offer directions when meaning is material and uncertain

Present 2–3 distinct, supported choices. For each: a concise reading, the lyric/recording evidence, what remains uncertain, and how it would change the film's key moments and ending. Label speculative parts. Recommend one only with reasons from the brief/evidence; do not select silently.

Ask which interpretation this MV should adopt, or whether the user wants a stated adaptation/combination. The user chooses the creative viewpoint, not the factual truth of an unverifiable artist claim. Record the selected direction and actual user evidence. Resolve required uncertainties, then include that reading in the content recap; combine this with the existing content checkpoint rather than inventing repeated approvals.

## Project records and production gate

Use `brief.music.kind` (`lyrical`, `instrumental`, `none`) and `brief.song_reading`. Visible lyric policy is separate: a film with no subtitles may still be based on a lyrical song.

For a lyrical song record `recording_basis`, `lyrics_status` (`provided` or `verified`), `lyrics_source`, `central_meaning`, `intent_basis`, actual `evidence`, checked `sources`, `uncertainties` and any `options`. Use `intent_basis` as `documented_artist_intent`, `text_interpretation` or `user_adaptation`; documented intent requires an attributable checked source.

If materially different choices exist, set `needs_user_selection:true`, preserve options with stable IDs, and record `selected_direction` plus `user_selection_evidence` only after selection. An unresolved uncertainty with `selection_required:true` blocks production. Set `status:"clarified"` only when this reading is supported and material uncertainty is resolved. User acceptance of a proposed whole film can also select its clearly stated reading when that was explicit.

For a verified/supplied instrumental or no-song task, use `status:"not_applicable"` and a truthful reason. Do not mark a song instrumental because no lyrics were supplied or because the user wants no text on screen. Unknown applicability remains pending.

The content digest includes the song identity and selected meaning. Changing them invalidates old content acceptance. The brief validator and bundled production entrypoints block missing/unsupported reading records; they cannot authenticate a fabricated citation or user reply. An agent must actually inspect the evidence and preserve uncertainty.

Schema 4 execution checks the canonical lyric document, actual cited line IDs and structured checked-source snapshots. Follow execution-gates.md. These checks reject empty or missing evidence; they cannot establish the truth of an agent-invented source or interpretation. Preserve uncertainty and inspect the actual retrieved material.
