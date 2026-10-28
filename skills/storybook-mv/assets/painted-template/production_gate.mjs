// Recorded content/scope gate. This cannot authenticate an agent's alleged user evidence.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
function canonical(value){if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';return JSON.stringify(value??null);}
export function contentDigest(brief){const value={};for(const k of ['content','structure','characters'])value[k]=brief[k]??null;value.lyrics_mode=brief.lyrics?.mode??null;value.song_basis={};for(const k of ['title','artist','version','kind'])value.song_basis[k]=brief.music?.[k]??null;value.song_meaning={};for(const k of ['central_meaning','intent_basis','selected_direction','lyrics_source'])value.song_meaning[k]=brief.song_reading?.[k]??null;return createHash('sha256').update(canonical(value)).digest('hex');}
export function songReadingErrors(brief){
  const m=brief.music||{},r=brief.song_reading||{},errors=[],text=v=>typeof v==='string'&&v.trim().length>0;
  if(!['lyrical','instrumental','none'].includes(m.kind))return ['song kind/lyric applicability is not established; no visible lyrics does not mean an instrumental'];
  if(m.kind!=='lyrical'){if(r.status!=='not_applicable'||!text(r.reason))errors.push('record why lyric interpretation is not applicable');return errors;}
  if(r.status!=='clarified')errors.push('SONG_MEANING_UNRESOLVED: verify lyrics, explain evidence and let the user select material ambiguities');
  for(const k of ['recording_basis','lyrics_source','central_meaning'])if(!text(r[k]))errors.push('song reading needs '+k+'; do not reconstruct missing lyrics or intent from memory');
  if(!['provided','verified'].includes(r.lyrics_status))errors.push('lyrics are missing/unverified; do not guess their words or meaning');
  if(!Array.isArray(r.evidence)||!r.evidence.length)errors.push('song meaning needs actual lyric/recording evidence, using cue IDs and paraphrases');
  if(!['documented_artist_intent','text_interpretation','user_adaptation'].includes(r.intent_basis))errors.push('separate documented artist intent, textual interpretation and user adaptation');
  if(r.intent_basis==='documented_artist_intent'&&!r.sources?.length)errors.push('an artist-intent claim requires a checked attributable source');
  const options=r.options||[];
  if(r.needs_user_selection===true||options.length>1){if(!r.selected_direction||!text(r.user_selection_evidence))errors.push('materially different song interpretations require the user selection, not an agent guess');else if(options.length&&!options.some(o=>o.id===r.selected_direction))errors.push('selected song interpretation is not among the recorded options');}
  if((r.uncertainties||[]).some(o=>o?.selection_required&&!o.resolved))errors.push('material song-meaning uncertainty is still unresolved');return errors;
}
export function gateErrors(brief,{purpose='prototype',duration}={}){
  const x=brief.execution||{},errors=[],text=v=>typeof v==='string'&&v.trim().length>0;
  if(x.context==='tool-self-test'){
    if(brief.tool_self_test?.source!=='storybook-mv'||brief.tool_self_test?.purpose!=='isolated-tool-verification')errors.push('invalid isolated tool self-test marker');
    if(![null,undefined,'none','original-code'].includes(brief.music?.source))errors.push('tool self-tests cannot use a user recording or impersonate a commissioned MV');
    if(purpose==='production')errors.push('tool self-test is not authorization for a full user MV');
    if(duration!==undefined&&(!Number.isFinite(duration)||duration<=0||duration>60))errors.push('isolated tool self-tests are limited to 60 seconds');
    return errors;
  }
  errors.push(...songReadingErrors(brief));
  const c=brief.content||{},confirmation=brief.content_confirmation||{};
  for(const key of ['subject','core_idea'])if(!text(c[key]))errors.push('content.'+key+' is not established through discovery');
  if(!Array.isArray(c.key_moments)||c.key_moments.length<2||c.key_moments.some(v=>!v||!text(v.description)||!text(v.purpose)))errors.push('content.key_moments needs concrete visible moments and their purpose');
  if(confirmation.status!=='confirmed')errors.push('CONTENT_NOT_CONFIRMED: ask content questions, recap the intended video and wait for user confirmation');
  for(const key of ['summary','user_evidence'])if(!text(confirmation[key]))errors.push('content confirmation needs '+key+'; the agent cannot invent user acceptance');
  if(confirmation.content_sha256!==contentDigest(brief))errors.push('content confirmation is missing/stale after a content change');
  if(x.production_authorized!==true)errors.push('production is not authorized');
  if(!['study','prototype','full'].includes(x.authorized_scope)||(purpose==='production'&&x.authorized_scope!=='full'))errors.push('requested production exceeds the explicitly authorized scope');
  if(!text(x.authorization_evidence))errors.push('record the user authorization for this production scope');
  if(!Number.isFinite(x.authorized_duration)||x.authorized_duration<=0)errors.push('record the authorized prototype/full duration bound');
  else if(duration!==undefined&&(!Number.isFinite(duration)||duration<=0||duration>x.authorized_duration+.125))errors.push('render duration exceeds the authorized duration');
  if(purpose==='production'&&Array.isArray(c.key_moments)&&c.key_moments.length<3)errors.push('full video needs an established beginning, development and ending/loop behavior');
  return errors;
}
export function assertProduction(project,options={}){
  const file=path.resolve(project,'brief.json');if(!fs.existsSync(file))throw Error('Production blocked: brief.json with confirmed content and scoped authorization is required.');
  const brief=JSON.parse(fs.readFileSync(file,'utf8')),effective={...options,purpose:options.purpose??(brief.execution?.authorized_scope==='full'?'production':'prototype')},errors=gateErrors(brief,effective);if(errors.length)throw Error('Production blocked: '+errors.join('; '));return brief;
}
