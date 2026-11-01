// Official Scratch VM, real key events; no renderer or audio.
const fs=require('node:fs'),assert=require('node:assert/strict');
const VM=require('scratch-vm'),{ScratchStorage}=require('scratch-storage');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const vm=new VM(); vm.attachStorage(new ScratchStorage());
  await vm.loadProject(fs.readFileSync('qa-output/NEXUS-BLOCKS-NIGHTMARE-QA-ONLY.sb3'));
  const stage=vm.runtime.getTargetForStage();
  const get=n=>Object.values(stage.variables).find(v=>v.name===n).value;
  const key=async k=>{vm.postIOData('keyboard',{key:k,isDown:true});await wait(120);vm.postIOData('keyboard',{key:k,isDown:false});await wait(120)};
  try {
    vm.start();vm.greenFlag();await wait(200);await key('4');await key('Enter');await wait(1000);
    assert.equal(get('Estado_Juego'),'JUGANDO');await key('6');assert.equal(get('NM_Event'),'TRIPLE');assert.equal(Number(get('NM_Rows')),3);assert.equal(Number(get('NM_Warning')),5);
    await key('r');await wait(1000);await key('7');await wait(2450);assert.equal(Number(get('NM_Burst')),1);
    await key('r');await wait(1000);await key('5');assert.equal(get('Estado_Juego'),'GLITCH_INTRO');
    console.log('PASS: QA-only keyboard shortcuts 5 Glitch, 6 Triple and 7 Burst (VM without renderer/audio)');
  } finally {vm.quit()}
})().then(()=>process.exit(0)).catch(e=>{console.error(e);process.exit(1)});
