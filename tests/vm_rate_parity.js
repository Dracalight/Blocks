'use strict';
const fs=require('fs');
const assert=require('assert');
const VM=require('scratch-vm');
const {ScratchStorage}=require('scratch-storage');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function run(compatibilityMode) {
  const vm=new VM();vm.attachStorage(new ScratchStorage());
  await vm.loadProject(fs.readFileSync('dist/Geometry-Dash-SubZero-NEXUS-V1.sb3'));
  vm.setCompatibilityMode(compatibilityMode);
  vm.start();vm.greenFlag();await wait(100);
  vm.postIOData('keyboard',{key:' ',isDown:true});await wait(45);vm.postIOData('keyboard',{key:' ',isDown:false});
  const stage=vm.runtime.getTargetForStage();
  const startDistance=Number(stage.lookupVariableById('distance').value);
  const startTime=vm.runtime.ioDevices.clock.projectTimer();
  await wait(1000);
  const endTime=vm.runtime.ioDevices.clock.projectTimer();
  const endDistance=Number(stage.lookupVariableById('distance').value);
  const player=vm.runtime.targets.find(t=>t.sprite.name==='Player');
  const result={mode:compatibilityMode?'30fps-compatible':'default',elapsed:endTime-startTime,
    distance:endDistance-startDistance,speed:(endDistance-startDistance)/(endTime-startTime),y:player.y,
    state:stage.lookupVariableById('state').value};
  vm.quit();return result;
}
(async()=>{
  const thirty=await run(true),sixty=await run(false);
  assert.strictEqual(thirty.state,'PLAYING');assert.strictEqual(sixty.state,'PLAYING');
  assert(Math.abs(thirty.y-sixty.y)<0.05,'ground position should match across VM cadence settings');
  assert(Math.abs(thirty.speed-sixty.speed)<12,`normalized speed mismatch 30/60: ${thirty.speed} vs ${sixty.speed}`);
  const report={status:'PASS',test:'Scratch VM 30/60 cadence parity',toleranceUnitsPerSecond:12,thirty,sixty,
    speedDifferenceUnitsPerSecond:Math.abs(thirty.speed-sixty.speed),fpsMeasured:false};
  fs.mkdirSync('reports',{recursive:true});
  fs.writeFileSync('reports/r2-rate-parity.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
