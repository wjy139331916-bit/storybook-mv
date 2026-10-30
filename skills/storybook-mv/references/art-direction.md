# Art direction through visible comparisons

## Contents
1. Recover references and taste decisions
2. Establish reproducible design baselines
3. Reuse the selected art assets
4. Inspect the whole visual progression
5. Repair specific defects and retain scoped lessons

Apply this method within the existing direction → design/script → pilot → whole-scope rough → production reviews. Reuse accepted evidence. Do not add an approval ceremony for each image or require the user to complete a technical form. Let the agent prepare comparisons and records; ask only about unresolved material choices. Keep the chosen style, asset policy, subject and authorized scope.

Treat runtime/test success, observed visual defects and actual user taste acceptance as separate evidence. More workbenches, a new renderer, high resolution, several agreeing AI reviewers or a numerical beauty score do not establish a successful design. Do not claim that these instructions train the model or guarantee better art.

## 1. Recover references and taste decisions

Reuse the user's actual positive examples, rejected examples and prior explanations before requesting more. When taste is unclear, invite a small coherent set, such as 2–3 liked examples and 1–2 counterexamples; these counts are suggestions, not prerequisites. A reference may contain both useful and unwanted features. If no examples are available, propose clearly labelled alternatives instead of inventing a user preference or blocking work only because a reference quota is empty.

Inspect the actual supplied image/sequence. Translate broad adjectives into visible dimensions: silhouette/age cues when relevant, line and edge construction, foreground/background hierarchy, subject scale, empty space, palette roles, text placement, texture and motion cadence. Separate what is observed, what the user explicitly likes/rejects, and what the agent proposes. Record deliberate differences from the reference. Do not infer that rejection of one face means rejection of its entire medium.

Store reference IDs, actual source paths/URLs, inspected time/crop and the associated user statement in the `references` array of project-local `plan/art-direction.json`. Label missing or inaccessible sources uninspected. Keep private references and derived source pixels out of portable skill exports. A reference's visual mechanism may inform original work; do not transplant its cast, footage or story.

## 2. Establish reproducible design baselines

After confirmed content/direction, make actual static design frames with the selected production assets and renderer. For a character story, a useful starting set is a character close view, a two-person/action composition and an environmental wide view. For typography, abstract, scenic or spatial work select equivalent representative views: type hierarchy, the hardest graphic state, material/light and a complete composition. Use fewer frames for a smaller authorized scope or reuse an already accepted equivalent; three frames are a planning aid, not a universal gate or a request for characters.

When a material design choice remains unresolved, offer 2–3 controlled versions of the same content. Vary the named dimension while holding unrelated variables stable. Do not produce three unrelated concepts or repeat a comparison already settled by the user. Put the chosen result into the existing complete design/script presentation, with the other relevant baselines and known limits. A liked option alone does not accept that complete package.

For an all-code project, render the design through the actual code route and save the reusable source. A generated illustration or external mockup cannot stand in for proof of that renderer. Under a different authorized asset policy, use the actual intended assets and verify their integration. Record baseline ID, role, artifact `{path,sha256}`, renderer/source references and the real design-package/decision reference when it exists in its `baselines` array. New images remain drafts until the existing user review supplies acceptance; never prefill approval.

Inspect at delivery size and small-screen size: identity/readability, focal point, overlap, text, edges and material. Compare later output with the selected baseline at matching content/scale and explain intentional changes. Correct a weak static design before expanding its animation. After design acceptance, use the existing bounded pilot to prove hard acting/effects/joins; a still does not establish natural motion. Reuse the accepted interval rather than imposing a new fixed ten-second sample.

## 3. Reuse the selected art assets

Treat bundled humanoids and neutral shapes as construction aids. Develop or obtain project-appropriate art within the authorized policy before treating them as a finished cast or scene. Preserve character views, expressions, clothes, prop attachments and recurring environments when relevant; for no-character work preserve type, graphic forms, materials, layout and motion primitives instead.

Record logical asset ID, source files, version/hash, baseline IDs, usage/affected shots and the actual approval reference in its `assets` array. Keep source/working versions separate from historical accepted versions. Reuse the same selected assets in design frames and production; do not regenerate their identity for every shot. Shared changes require reinspection of every affected use. An asset registry records provenance and reuse, not a new acceptance boolean.

If repeated visible attempts still miss the chosen requirement, show the remaining evidence and offer concrete options: revise the design, simplify an agreed action, choose another feasible treatment, or obtain a limited human art review of a model sheet/representative scene. Explain the affected scope and cost uncertainty. Do not contact an artist, buy assets, use image generation or change the selected style without the user's authorization. In all-code work, any supplied design still needs an actual reproducible code adaptation and comparison.

## 4. Inspect the whole visual progression

During design, arrange key rendered compositions into a static sheet across the authorized timeline. Use the full confirmed song scope only when that scope exists; a short excerpt needs only its own progression. Link each entry to its actual section/shot, frame, intended focal point, palette/light and visible change or purposeful hold in its `visual_sequence` array. Keep provisional timing labelled. Use the existing shot map for music/lyric/section facts rather than duplicating a different timeline.

Inspect repeated framing, subject scale, color/light, density, text placement, foreground/background relationships and motifs across the sheet. Explain a chorus's development or an intentional repetition. Preserve coherent repetition and quiet holds where they serve the agreed language; do not require every shot to move, every chorus to change, or every lyric to have its own illustration. A coherent frame sequence should serve the story or graphic progression, not be a collection of individually attractive images.

Present this sheet with the existing design/script package. Later inspect the actual whole-scope rough cut with the selected soundtrack after pilot acceptance. A static color/composition sheet cannot replace the animated rough cut or prove pacing/sync. Pixar's colorscript explanation and Disney's thumbnail-to-refined-storyboard process are useful production references, not evidence that this toolkit produces their artistic quality:

- https://www.pixar.com/toy-story-2 (Colorscripts)
- https://disneyanimation.com/process/story/

## 5. Repair specific defects and retain scoped lessons

Compare the actual current output with its selected baseline and prior revision. State the observable discrepancy before diagnosing code or issuing instructions. Examples: a silhouette merges with its background; glasses hide the eyes; a prop separates before contact; the caption masks an expression. Convert “more refined” into a concrete proposed change and inspect its effect; do not apply a universal palette, head count or camera rule.

Prioritize the three most consequential issues per ordinary review round, adapting for a smaller task or urgent safety/technical failures. Retain the full backlog, blockers and unaffected accepted shots; three is a focus budget, not permission to discard other defects. Keep stable issue IDs in `review.json`. Record current revision, focused issue IDs, matched before/after evidence, the change and remaining observations in its `review_rounds` array, with status still pending where user review has not occurred.

Fix the shared cause once where appropriate, render the affected region with neighboring joins, then inspect the replacement. Separate a technical fix from a changed aesthetic choice; use the existing affected-stage review when a visible design/story changes. Never mark an issue resolved only because a script ran or a score rose.

Retain explicit user likes/dislikes and selected before/after examples in its `taste_notes` array, scoped to this project/style/asset and their actual source statements. Recover them on handoff without repeating the interview. Do not turn one project's warm palette, proportion or rejection into global defaults, populate approval from an AI judgment, or export private media into the reusable skill. Promote only sanitized, evidenced reusable lessons under authorized maintenance, as described in `learning-and-validation.md`.

Use `assets/contracts/art-direction.template.json` as an optional working record at the project’s `plan/art-direction.json`; fill it from actual artifacts/statements and leave irrelevant arrays empty with a short reason. Keep selected design rules and actual rendered evidence in the existing `visual-spec.json`, source files and design package. Treat existing package hashes and `workflow.approvals` as authoritative; a draft flag or decision reference in working notes supplies no approval.

Preserve already presented/accepted files byte-for-byte when appending review history or user taste notes. Store these observations and external approval references in the working record, not by rewriting a hash-bound visual specification or old package. A visible design/source change still needs its appropriate new revision and affected-stage review. Keep working notes out of render input digests; actual design/source changes must remain detectable. Transfer the working record with the project and omit it and private reference media from generic skill exports.

Existing validators check general records/identities; they do not mechanically enforce every item here or evaluate taste. Apply these behavioral instructions and show the real work.
