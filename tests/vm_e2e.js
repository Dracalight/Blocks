'use strict';
const fs = require('fs');
const assert = require('assert');
const VirtualMachine = require('scratch-vm');
const {ScratchStorage} = require('scratch-storage');
const artifact = 'dist/Geometry-Dash-SubZero-NEXUS-V1.sb3';
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
const testStart=Date.now();

async function main() {
  const vm = new VirtualMachine();
  const storage = new ScratchStorage();
  vm.attachStorage(storage);
  const errors = [];
  vm.on('runtimeerror', error => errors.push(String(error)));
  await vm.loadProject(fs.readFileSync(artifact));
  const stage = vm.runtime.getTargetForStage();
  const player = vm.runtime.targets.find(target => target.sprite.name === 'Player');
  assert(stage && player, 'Scratch VM must create stage and player targets');
  assert.strictEqual(vm.runtime.targets.length, 9);
  for (const target of vm.runtime.targets) {
    for (const costume of target.sprite.costumes) assert(costume.asset, `${target.sprite.name} costume asset loaded`);
  }
  vm.start();
  vm.greenFlag();
  await wait(100);
  const get = name => stage.lookupVariableById(name).value;
  const key = async (name, hold=45) => {
    vm.postIOData('keyboard', {key:name, isDown:true});
    await wait(hold);
    vm.postIOData('keyboard', {key:name, isDown:false});
    await wait(25);
  };
  assert.strictEqual(get('state'),'MENU','green flag initializes MENU');
  await key(' ');
  assert.strictEqual(get('state'),'PLAYING','space starts actual Scratch VM project');
  assert.strictEqual(get('attempts'),1);
  await wait(180);
  assert(get('distance')>10,'world advances from simulated time');
  assert(Number.isFinite(player.y),'player position is finite');
  const spike=vm.runtime.targets.find(t=>t.sprite.name==='Spike 01');
  assert(Math.abs(spike.x - (320-get('distance'))) < 8,'camera maps world obstacle into screen coordinates');
  await key(' ');
  await wait(150);
  assert(player.y > -40,'jump produces observable upward movement');
  await wait(900);
  assert(player.y <= -60 || (player.y > 30 && player.y < 40),'jump lands on floor or test platform');
  assert(String(get('grounded')).toLowerCase()==='true','landing restores grounded state');
  await key('p');
  assert.strictEqual(get('state'),'PAUSED','P pauses');
  const pausedDistance=get('distance');
  await wait(180);
  assert(Math.abs(get('distance')-pausedDistance)<0.01,'distance is frozen while paused');
  await key('p');
  assert.strictEqual(get('state'),'PLAYING','P resumes');
  const deathDeadline=Date.now()+2500;
  while(get('state')==='PLAYING' && Date.now()<deathDeadline) await wait(25);
  assert.strictEqual(get('state'),'DEAD','unavoided spike causes death');
  const attemptsBefore=get('attempts');
  await key('r');
  assert.strictEqual(get('state'),'PLAYING','R restarts from death');
  assert.strictEqual(get('attempts'),attemptsBefore+1);
  assert(get('distance')<50,'restart resets progress');
  await wait(120);
  assert.strictEqual(get('state'),'PLAYING','old collision state does not cause a ghost death');

  // Complete a fresh genuine run by jumping before each authored spike interval.
  const spikeCenters=[440,770,1160,1510,1890,2290];
  let next=0, jumped=false, platformLandingObserved=false;
  const finishDeadline=Date.now()+19000;
  while(get('state')==='PLAYING' && Date.now()<finishDeadline) {
    const d=Number(get('distance'));
    if(d>800 && d<980 && player.y>35 && player.y<38 && String(get('grounded')).toLowerCase()==='true') {
      platformLandingObserved=true;
    }
    if(next<spikeCenters.length && !jumped && d >= spikeCenters[next]-70) {
      await key(' ');
      jumped=true;
    }
    if(next<spikeCenters.length && d > spikeCenters[next]+100) { next++; jumped=false; }
    await wait(15);
  }
  assert.strictEqual(next,spikeCenters.length,'input driver attempted all six distinct hazards');
  assert.strictEqual(get('state'),'COMPLETE','the native Scratch VM playthrough reaches the authored goal');
  assert(platformLandingObserved,`player lands on the elevated authored platform (d=${get('distance')}, y=${player.y}, grounded=${get('grounded')})`);
  const completionDistance=Number(get('distance'));
  const completionAttempts=Number(get('attempts'));

  // Practice keeps its mode while paused and rewinds after an unavoided first hazard.
  vm.greenFlag();
  await wait(100);
  await key('v');
  assert.strictEqual(get('state'),'PRACTICE','V starts practice from MENU');
  await key('p');
  assert.strictEqual(get('state'),'PAUSED','P pauses practice');
  await key('p');
  assert.strictEqual(get('state'),'PRACTICE','resume restores practice mode');
  const practiceSpikes=[440,770,1160];
  let practiceNext=0, practiceJumped=false, practicePrevious=0, practiceReset=false;
  const practiceDeadline=Date.now()+9000;
  while(Date.now()<practiceDeadline) {
    const d=Number(get('distance'));
    if(practicePrevious>1400 && d>850 && d<1120) { practiceReset=true; break; }
    if(practiceNext<practiceSpikes.length && !practiceJumped && d>=practiceSpikes[practiceNext]-70) {
      await key(' ');
      practiceJumped=true;
    }
    if(practiceNext<practiceSpikes.length && d>practiceSpikes[practiceNext]+100) {
      practiceNext++;
      practiceJumped=false;
    }
    practicePrevious=d;
    if(get('state')!=='PRACTICE') break;
    await wait(20);
  }
  assert.strictEqual(practiceNext,practiceSpikes.length,'practice play passes the first three hazards');
  assert(practiceReset,'practice collision after the platform returns to its saved checkpoint');
  assert(Math.abs(Number(get('distance'))-980)<130,'practice rewind uses the platform checkpoint');
  assert.strictEqual(get('state'),'PRACTICE');
  assert.strictEqual(errors.length,0,'no critical runtime exceptions: '+errors.join('; '));
  const report={status:'PASS',scratchVm:'5.0.300',scratchStorage:'4.0.0',targets:vm.runtime.targets.length,
    scenarios:['load','assets','start','movement','camera-coordinates','jump','landing','elevated-platform-landing','pause','resume','death','restart','six-spike-playthrough','complete','practice-checkpoint','practice-pause-resume'],
    completedDistance:completionDistance,completionAttempts,practiceResetDistance:Number(get('distance')),
    runtimeErrors:errors.length,rendering:'headless; no renderer attached',
    turboWarp:'unverified',ipadTouch:'unverified',elapsedWallMs:Date.now()-testStart};
  fs.mkdirSync('reports',{recursive:true});
  fs.writeFileSync('reports/r2-runtime-test.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
  vm.quit();
}
main().catch(error => { console.error(error); process.exitCode=1; });
