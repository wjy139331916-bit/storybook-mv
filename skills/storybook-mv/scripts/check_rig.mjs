#!/usr/bin/env node
// Audit the actual pose coordinates exported by a drawing project.
import {readFileSync} from 'node:fs';
const args=process.argv.slice(2);
if(!args[0]) { console.error('Usage: node check_rig.mjs poses.json [--tolerance=0.08] [--min-heads=chosen-model] [--max-heads=chosen-model]'); process.exit(2); }
const opt=Object.fromEntries(args.slice(1).map(x=>x.replace(/^--/,'').split('=')));
const tolerance=Number(opt.tolerance??0.08), minHeads=Number(opt['min-heads']??Number.EPSILON), maxHeads=Number(opt['max-heads']??Number.POSITIVE_INFINITY);
const errors=[];let characters=0,segments=0;
const point=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
try {
  if(!(tolerance>=0&&tolerance<1&&minHeads>0&&maxHeads>=minHeads))throw Error('invalid options');
  const data=JSON.parse(readFileSync(args[0],'utf8'));
  if(!Array.isArray(data.frames)||!data.frames.length)throw Error('nonempty frames array required');
  for(const frame of data.frames){
    if(!Number.isFinite(frame.t)||!Array.isArray(frame.characters)||!frame.characters.length){errors.push('invalid/empty frame');continue;}
    for(const c of frame.characters){
      characters++;const tag=`t=${frame.t} ${c.id??'actor'}`;
      if(![c.head_px,c.height_px,c.heads].every(Number.isFinite)||c.head_px<=0||c.height_px<=0||c.heads<minHeads||c.heads>maxHeads){errors.push(tag+': invalid head/height or style ratio');}
      else if(Math.abs(c.height_px/c.head_px-c.heads)/c.heads>0.12)errors.push(tag+': figure height and head size disagree');
      if(!Array.isArray(c.limbs)||!c.limbs.length){errors.push(tag+': no measured segments');continue;}
      for(const limb of c.limbs){
        segments++;
        if(!point(limb.a)||!point(limb.b)||!Number.isFinite(limb.length_px)||limb.length_px<=0){errors.push(tag+': malformed segment');continue;}
        const actual=Math.hypot(limb.b[0]-limb.a[0],limb.b[1]-limb.a[1]);
        if(Math.abs(actual-limb.length_px)/limb.length_px>tolerance)errors.push(tag+' '+limb.name+': stretched/compressed segment');
      }
    }
  }
}catch(e){errors.push(e.message);}
console.log(JSON.stringify({ok:!errors.length,characters,segments,errors,scope:'exported pose metadata only; drawing and motion still require visual review'},null,2));
process.exitCode=errors.length?2:0;
