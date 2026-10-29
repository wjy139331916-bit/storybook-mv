// One authoritative Python contract for CLI and rendering hosts. No shell execution.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const checker=path.join(path.dirname(fileURLToPath(import.meta.url)),'check_brief.py');
function contract(action,brief,options={}){
  const candidates=process.env.MV_PYTHON?[process.env.MV_PYTHON]:['python3','python'];
  for(const python of candidates){
    const r=spawnSync(python,[checker,'--bridge',action],{input:JSON.stringify({brief,options}),encoding:'utf8',maxBuffer:8*1024*1024});
    if(r.error?.code==='ENOENT')continue;
    if(r.error||r.status!==0)throw Error('Brief contract failed: '+(r.stderr||r.error?.message||'unknown error'));
    return JSON.parse(r.stdout);
  }
  throw Error('Python 3 is required for the shared MV contract; select MV_PYTHON if needed.');
}
export function contentDigest(brief){return contract('digest',brief);}
export function songReadingErrors(brief,options={}){return contract('song',brief,options);}
export function gateErrors(brief,options={}){return contract('gate',brief,options);}
export function assertProduction(project,options={}){
  const root=path.resolve(project),file=path.join(root,'brief.json');
  if(!fs.existsSync(file))throw Error('Production blocked: brief.json with confirmed content and scoped authorization is required.');
  const brief=JSON.parse(fs.readFileSync(file,'utf8')),errors=contract('entry',brief,{...options,project:root});
  if(errors.length)throw Error('Production blocked: '+errors.join('; '));return brief;
}
