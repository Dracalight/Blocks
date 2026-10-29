// Official Scratch VM with keyboard events and state fixtures; no renderer/audio.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const VM = require('scratch-vm');
const {ScratchStorage} = require('scratch-storage');
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  const vm = new VM(); vm.attachStorage(new ScratchStorage());
  await vm.loadProject(fs.readFileSync('NEXUS-BLOCKS-ENDLESS.sb3'));
  const stage = vm.runtime.getTargetForStage();
  const v = name => Object.values(stage.variables).find(item => item.name === name);
  const get = name => v(name).value;
  const set = (name, value) => { v(name).value = value; };
  const key = async name => { vm.postIOData('keyboard',{key:name,isDown:true}); await wait(100); vm.postIOData('keyboard',{key:name,isDown:false}); await wait(100); };
  try {
    vm.start(); vm.greenFlag(); await wait(200); await key('4'); await key('Enter'); await wait(1100);
    assert.equal(get('Estado_Juego'),'JUGANDO');
    set('NM_Event','TRIPLE'); set('NM_Rows',3); set('NM_Warning',1); set('NM_Progress',0); set('NM_Cancelable',1);
    await key(' ');
    assert.equal(get('NM_Event'),'NONE');
    assert.equal(get('Tablero').slice(-30).filter(x=>Number(x)===8).length,27);
    for (let i=0;i<3;i++) assert.equal(get('Tablero').slice(-30+i*10,-20+i*10 || undefined).filter(x=>Number(x)===0).length,1);
    set('NM_BurstNext', Number(get('Tiempo_Juego'))+.1); await wait(350);
    assert.equal(Number(get('NM_Burst')),1); assert.ok(Number(get('Velocidad_Caida')) < .13);
    await key('p'); const t=get('Tiempo_Juego'); await wait(250); assert.equal(get('Tiempo_Juego'),t);
    await key('p'); set('NM_BurstEnd',Number(get('Tiempo_Juego'))+.1); await wait(350);
    assert.equal(Number(get('NM_Burst')),0); assert.ok(Number(get('Velocidad_Caida'))>.20);
    // Exercise actual scheduler and real block scripts using state fixtures.
    set('Estado_Juego','GLITCH_PLAY'); set('G_Time',.7); set('G_PrevPhase',0);
    set('G_X',0); set('G_Y',0); set('G_HP',3); set('G_Invuln',0); await wait(90);
    assert.equal(Number(get('G_HP')),2); await wait(150); assert.equal(Number(get('G_HP')),2);
    set('G_Time',.7); set('G_Invuln',0); await wait(90); assert.equal(Number(get('G_HP')),1);
    set('G_Time',.7); set('G_Invuln',0); await wait(90); assert.equal(get('Estado_Juego'),'GLITCH_RESULT');
    assert.equal(Number(get('G_HP')),0); assert.equal(Number(get('G_Success')),0);
    await wait(1800); assert.equal(get('Estado_Juego'),'JUGANDO');
    assert.equal(get('NM_Event'),'DOUBLE'); assert.equal(Number(get('NM_Rows')),2);
    console.log('PASS: Triple 3 rows; Nightmare burst activation, pause and recovery; Glitch damage, invulnerability and failure scheduling (official VM, no renderer).');
  } finally { vm.quit(); }
})().then(()=>process.exit(0)).catch(e=>{console.error(e);process.exit(1)});
