# Hard gate: understand and confirm content before production

Apply this to every user MV, independent of style, engine and length. Basic logistics do not establish creative intent. Do not start building because the first three answers contain a song, whole-song length and 16:9, or a palette and a visual adjective.

## Establish the content through adaptive questions

Recover existing answers and accepted decisions. Ask 1–3 useful questions per round, normally two, based on the largest remaining uncertainty. At minimum know:

1. The subject and core idea: what the viewer actually sees and should understand/feel.
2. The progression mechanism: story/action, lyric imagery, typography, musical/abstract development or a chosen combination.
3. Concrete key moments and how they change. A full film needs an opening, development and ending/loop behavior. Non-narrative work needs changing graphic states, not a forced romance.
4. Material boundaries: unwanted content, factual/fictional status and important relationship or meaning assumptions.
5. For a lyrical song, the evidenced interpretation and the user's selection where ambiguity changes the film. Use the song-understanding reference linked from SKILL.md.

Do not ask every possible detail. Do not force a fixed number of rounds: continue because content remains unclear, and stop once it is specific and accepted. Font/prop implementation can remain a labelled routine choice. The engine is not the content.

## Recap and wait when acceptance is missing

Present a short, concrete content recap: the chosen reading/theme, subject, what happens at the beginning, what changes, 2–3 representative moments, ending/loop, important exclusions, and the next proposed production scope. Distinguish user decisions from the agent's proposals.

Ask whether this is the content the user wants, with a focused change option. End the turn and wait if this is unresolved. Do not combine the question with “I am now rendering the full video.” The answer to a song/version or aspect-ratio question is not a content-confirmation response.

Reuse actual prior acceptance. A detailed direct request for an exact concept can provide confirmation when the content is already unambiguous and explicitly requested; preserve that user evidence. A generic “make it,” “full length,” “looks good” about a palette, or missing chat history cannot substitute. If the user explicitly delegates creative choices, record precisely what was delegated and its limits; do not fabricate that delegation.

## Record the gate without inventing consent

`assets/brief.template.json` starts pending. Fill `content.subject`, `content.core_idea`, and `content.key_moments` as objects with `description` and `purpose`. Keep `structure`, cast/subject rules, song basis and selected reading consistent.

Only after the real user acceptance: record `content_confirmation.status:"confirmed"`, the accepted `summary`, and `user_evidence` identifying the actual reply/decision. Use the current digest from:

```bash
python3 <skill>/scripts/check_brief.py <brief.json> --content-digest
```

Copy that value into `content_confirmation.content_sha256` only after reconciling the accepted content. Calculating a digest does not confirm anything. A material change to content, selected song/reading, progression, cast/relationship or lyric mode invalidates the previous digest; obtain acceptance of that change. Routine color/font/implementation changes need no new content interview when within accepted design constraints.

Separately record `execution.production_authorized`, `authorized_scope` (`study`, `prototype`, `full`), `authorized_duration` and `authorization_evidence`. A prototype's bound is its authorized clip length, not the whole recording length. An earlier whole-song request can combine with later acceptance of that exact full-song content; a new redundant permission question is unnecessary. Acceptance of an explicitly limited prototype never expands to a whole song.

```bash
python3 <skill>/scripts/check_brief.py <brief.json> --for prototype
python3 <skill>/scripts/check_brief.py <brief.json> --for production
```

Scaffolding and bundled CLI renderers check these records and duration bounds. Records are not an authentication system: the agent must ground acceptance in real user messages, never fill consent fields to make a validator pass. Other/custom engines must apply the same gate before running production commands.

## Legacy work and isolated verification

For old projects without the new fields, recover actual accepted content from the conversation/decision files. If missing, recap and ask before further production; do not default old `production_authorized:true` to approval. Preserve existing artifacts and code during migration.

`--tool-self-test` is only for runtime checks, regression fixtures or the bundled original implementation examples during authorized toolkit evaluation/maintenance. It creates a clearly marked isolated project, uses original synthetic/no audio, and is limited to 60 seconds. It is not a user MV, cannot pass a full user-production contract and must never be used to evade an unresolved interview. Use the normal confirmed brief for all commissioned production.

## Failure to prevent

User answers: song name, full song, warm 16:9. Incorrect next action: invent two lovers, scaffold 240 seconds and render. Correct next action: ask what the film should show and which evidenced song reading to use; explore the progression, recap the chosen content, wait for confirmation, then enter the authorized next stage.

Schema 4 also requires a hash-bound user-reply/recap record at execution, and binds actual canonical lyric/audio bytes. Follow execution-gates.md for format and legacy migration; a format conversion cannot supply missing acceptance.
