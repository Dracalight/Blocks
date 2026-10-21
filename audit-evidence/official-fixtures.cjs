// Audit fixtures on official scheduler; sounds traced at primitive dispatch, not listened to.
const fs=require('fs'),assert=require('assert/strict'),VM=require('scratch-vm'),{ScratchStorage}=require('scratch-storage');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const vm=new VM();vm.attachStorage(new ScratchStorage());await vm.loadProject(fs.readFileSync(process.argv[2]||'NEXUS-BLOCKS-ENDLESS.sb3'));
const stage=vm.runtime.getTargetForStage(),motor=vm.runtime.targets.find(t=>t.getName()==='Motor_Juego');
const variable=n=>Object.values(stage.variables).find(v=>v.name===n),get=n=>variable(n).value,set=(n,x)=>variable(n).value=x;
const blocks=motor.blocks._blocks;const proc=n=>Object.values(blocks).find(b=>b.opcode==='procedures_definition'&&blocks[b.inputs.custom_block.block].mutation.proccode===n);
const sounds=[];const original=vm.runtime._primitives.sound_play;vm.runtime._primitives.sound_play=(args,util)=>{sounds.push(args.SOUND_MENU);return original(args,util)};
vm.start();
async function run(n){const b=proc(n);assert.ok(b,n);const thread=vm.runtime._pushThread(b.next,motor,{stackClick:true});thread.warpTimer=null;const start=Date.now();while(vm.runtime.threads.includes(thread)){await wait(10);assert.ok(Date.now()-start<5000,n+' timed out')}}
const logs={};
try{
 await run('Iniciar_Partida');
 for(let n=1;n<=4;n++){await run('Iniciar_Partida');set('Tablero',Array(200-n*10).fill(0).concat(Array(n*10).fill(3)));sounds.length=0;await run('Revisar_Y_Eliminar_Lineas');assert.deepEqual(sounds,[[null,'07_line_clear_1','08_line_clear_2','09_line_clear_3','10_tetris_4'][n]]);assert.equal(get('Lineas'),n);logs['clear'+n]=sounds.slice()}
 for(const prior of [9,19,29,99]){await run('Iniciar_Partida');set('Lineas',prior);set('Nivel',1+Math.floor(prior/10));set('Tablero',Array(190).fill(0).concat(Array(10).fill(2)));sounds.length=0;await run('Revisar_Y_Eliminar_Lineas');await run('Revisar_Y_Eliminar_Lineas');assert.equal(sounds.filter(n=>n==='12_level_up').length,1)}logs.levelBoundaries=[10,20,30,100];
 await run('Iniciar_Partida');set('Siguiente_Pieza',2);set('Pieza_Fila',10);get('Tablero')[14]=3;sounds.length=0;await run('Guardar_Hold');assert.equal(get('Estado_Juego'),'GAMEOVER');assert.equal(sounds.filter(n=>n==='Sonido_GameOver').length,2);logs['NB-AUDIT-001']=sounds.slice();
 await run('Iniciar_Partida');set('Modo_Juego','CHAOS');set('Tiempo_Juego',23.1);set('Ultimo_Tick',vm.runtime.ioDevices.clock.projectTimer());set('Proximo_Ataque',25);set('Proximo_Evento',100);set('Evento_Caos','SPEED BURST');set('Evento_Fin',30);await run('Actualizar_Velocidad_Y_Caos');const speed=get('Velocidad_Caida');sounds.length=0;await run('Tick');assert.equal(get('Evento_Caos'),'GARBAGE INCOMING');assert.ok(get('Velocidad_Caida')>speed*1.9);await run('Tick');assert.equal(sounds.filter(n=>n==='11_chaos_warning').length,1);logs['NB-AUDIT-002']={before:speed,after:get('Velocidad_Caida'),sounds:sounds.slice()};
 await run('Iniciar_Partida');set('Modo_Juego','NORMAL');set('Pieza_Guardada',2);set('Pieza_Fila',10);set('Tiempo_Juego',10);set('Reloj_Caida',9.34);await run('Guardar_Hold');assert.equal(Number(get('Pieza_Fila')),2);set('Ultimo_Tick',vm.runtime.ioDevices.clock.projectTimer());await run('Tick');assert.equal(Number(get('Pieza_Fila')),3);logs['NB-AUDIT-003']={rowAfterTick:get('Pieza_Fila')};
 await run('Iniciar_Partida');get('Tablero')[0]=3;sounds.length=0;await run('Garbage_Attack');assert.equal(get('Estado_Juego'),'GAMEOVER');assert.ok(!sounds.includes('Sonido_GameOver'));logs['NB-AUDIT-004']=sounds.slice();
 // Real key sensors, no green-flag forever thread: dispatch Leer_Teclado per input fixture.
 await run('Iniciar_Partida');set('Estado_Juego','MENU');sounds.length=0;
 vm.postIOData('keyboard',{key:'Enter',isDown:true});await run('Leer_Teclado');await run('Leer_Teclado');vm.postIOData('keyboard',{key:'Enter',isDown:false});await run('Leer_Teclado');assert.equal(sounds.filter(n=>n==='13_game_start').length,1);logs.startSound=sounds.slice();
 const keyboardCounts={};for(const [key,latch] of [['ArrowLeft','left'],['ArrowRight','right'],['ArrowDown','down'],['ArrowUp','up'],['c','c'],[' ','space'],['p','p'],['r','r']]){for(let i=0;i<20;i++){vm.postIOData('keyboard',{key,isDown:true});await run('Leer_Teclado');await run('Leer_Teclado');vm.postIOData('keyboard',{key,isDown:false});await run('Leer_Teclado');assert.equal(Number(get('key_'+latch)),0)}keyboardCounts[key]=20}logs.keyboardPressReleaseCycles=keyboardCounts;
 console.log('AUDIT_RESULT '+JSON.stringify({pass:true,logs},null,2));
}finally{vm.quit()}})().then(()=>process.exit(0)).catch(e=>{console.error(e);process.exit(1)});
