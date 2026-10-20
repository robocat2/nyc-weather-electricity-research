import {cp,rm,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
await rm(root+'dist',{recursive:true,force:true});
await mkdir(root+'dist',{recursive:true});
await cp(root+'site',root+'dist',{recursive:true});
console.log('Static site built: dist/ (no dependency installation required).');
