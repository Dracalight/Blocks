/* Regresiones sobre el planificador oficial; sin emular bloques ni teclado. */
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const VM=require('scratch-vm');const {ScratchStorage}=require('scratch-storage');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 const vm=new VM(); vm.attachStorage(new ScratchStorage());
 await vm.loadProject(fs.readFileSync(process.argv[2]||path.join(__dirname,'../NEXUS-BLOCKS-ENDLESS.sb3')));
 const stage=vm.runtime.getTargetForStage();
 const variable=name=>Object.values(stage.variables).find(v=>v.name===name);
 const get=name=>variable(name).value;const set=(name,value)=>{variable(name).value=value};
 const key=async(name,ms=100)=>{vm.postIOData('keyboard',{key:name,isDown:true});await delay(ms);vm.postIOData('keyboard',{key:name,isDown:false});await delay(100)};
 vm.start();vm.greenFlag();await delay(200);
 try {
  const results={};
  for(const [selection,mode,expected] of [['1','NORMAL',.65],['2','HARD',.30],['3','CHAOS',.23]]) {
   vm.greenFlag();await delay(150);await key(selection);await key('Enter');
   assert.equal(get('Estado_Juego'),'JUGANDO');assert.equal(get('Modo_Juego'),mode);
   assert.ok(Math.abs(get('Velocidad_Caida')-expected)<.002);
   const intervals=[];let row=get('Pieza_Fila'),last=null;let locks=0;let previous=0;
   const start=Date.now();
   while(Date.now()-start<20100){await delay(10);const next=get('Pieza_Fila');const occupied=get('Tablero').filter(v=>Number(v)>0).length;
    if(occupied>previous)locks++;previous=occupied;
    if(next===row+1){const now=Date.now();if(last!==null)intervals.push((now-last)/1000);last=now;}else if(next<row)last=null;
    row=next;
   }
   assert.ok(locks>=1,mode+' fija piezas sin teclado');assert.equal(Number(get('Puntuacion')),0,'la gravedad no puntúa como soft drop');assert.ok(intervals.length>=10);
   const first=intervals.slice(0,10).sort((a,b)=>a-b);const median=first[Math.floor(first.length/2)];
   assert.ok(Math.abs(median-expected)<.08,`${mode}: ${median}`);
   results[mode]={configured:expected,observedMedian:median,locks,wallSeconds:20.1};
  }
  await key('r');await key('p');assert.equal(get('Estado_Juego'),'PAUSA');
  const frozen=get('Tiempo_Juego');const row=get('Pieza_Fila');await delay(1100);assert.equal(get('Tiempo_Juego'),frozen);assert.equal(get('Pieza_Fila'),row);
  await key('p');assert.equal(get('Estado_Juego'),'JUGANDO');await delay(350);assert.ok(get('Tiempo_Juego')>frozen);
  await key('r');await key('p');await key('1');await key('r');
  const column=get('Pieza_Col');await key('ArrowLeft');assert.ok(get('Pieza_Col')<column);
  await key('ArrowRight');await key('ArrowUp');assert.equal(Number(get('Pieza_Rotacion')),1);
  await key('c',550);assert.equal(Number(get('Puede_Guardar')),0);assert.ok(get('Pieza_Guardada')>0);
  await key(' ',550);assert.equal(get('Tablero').filter(v=>Number(v)>0).length,4,'hard drop sostenido no fija dos piezas');
  await key('ArrowDown',300);assert.ok(get('Puntuacion')>0);
  await key('p');await key('3');await key('r');
  set('Proximo_Evento',get('Tiempo_Juego')+.05);await delay(200);assert.equal(get('Evento_Caos'),'DIFFICULT PIECES');
  set('Proximo_Evento',get('Tiempo_Juego')+.05);await delay(200);assert.equal(get('Evento_Caos'),'SPEED BURST');assert.ok(get('Velocidad_Caida')<.13);
  set('Proximo_Ataque',get('Tiempo_Juego')+1);await delay(100);assert.equal(get('Evento_Caos'),'GARBAGE INCOMING');await delay(1100);
  assert.equal(get('Tablero').slice(-10).filter(v=>Number(v)===8).length,9);
  await key('p');await key('4');assert.equal(get('Modo_Juego'),'NIGHTMARE');assert.equal(get('Estado_Juego'),'MENU');
  await key('Enter');assert.equal(get('Estado_Juego'),'NIGHTMARE_INTRO');
  await key('p');assert.equal(get('Estado_Juego'),'PAUSA');
  const intro=get('Nightmare_Intro');await delay(250);assert.equal(get('Nightmare_Intro'),intro);
  await key('p');await delay(950);assert.equal(get('Estado_Juego'),'JUGANDO');
  assert.ok(get('Velocidad_Caida')>=.07 && get('Velocidad_Caida')<=.23);
  set('NM_Event','DOUBLE');set('NM_Warning',1);set('NM_Rows',2);set('NM_Progress',0);
  await key(' ');assert.equal(get('NM_Event'),'NONE');
  assert.equal(get('Tablero').slice(-20).filter(v=>Number(v)===8).length,18);
  set('Tiempo_Juego',121);set('NM_Sequence',3);set('NM_Cooldown',5);
  await key(' ');assert.equal(Number(get('NM_Chain')),1);assert.equal(get('NM_Event'),'DOUBLE');assert.equal(Number(get('NM_Warning')),4);
  await key('p');const chainWarning=get('NM_Warning');await delay(250);assert.equal(get('NM_Warning'),chainWarning);
  await key('p');set('NM_Warning',1);await key(' ');
  assert.equal(get('NM_Event'),'CHAIN_JAM');assert.equal(Number(get('NM_Warning')),2);
  console.log(JSON.stringify({pass:true,results,interaction:'pause/resume, arrows, rotate, hold, hard/soft drop, restart, modes, chaos events, garbage'},null,2));
 }finally{vm.quit()}
})().then(()=>process.exit(0)).catch(error=>{console.error(error);process.exit(1)});
