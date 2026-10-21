import sys,random,json
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
from validate_sb3 import Scratch3VMInterpreter
import zipfile
with zipfile.ZipFile('NEXUS-BLOCKS-ENDLESS.sb3') as z:p=json.loads(z.read('project.json'))
random.seed(9191);v=Scratch3VMInterpreter(p);logs={}
for mode in ('NORMAL','HARD','CHAOS'):
 v.vars['Modo_Juego']=mode;v.call_proc('Iniciar_Partida');restarts=0;actions=[]
 for n in range(1,1801):
  v.sim_timer=n/10;v.call_proc('Tick')
  if v.vars['Estado_Juego']=='GAMEOVER':restarts+=1;v.call_proc('Iniciar_Partida');actions.append([n,'restart'])
  if n%8==0:
   d=random.choice((-1,1));v.call_proc('Mover_Horizontal %s',d);actions.append([n,'move',d])
  if n%13==0:v.call_proc('Rotar_Pieza');actions.append([n,'rotate'])
  if n%19==0:v.call_proc('Caida_Instantanea');actions.append([n,'hard'])
  assert len(v.lists['Tablero'])==200 and all(0<=c<=8 for c in v.lists['Tablero'])
  assert v.vars['Velocidad_Caida']>=.07
 logs[mode]={'simulatedSeconds':180,'ticks':1800,'topOutRestarts':restarts,'inputs':actions}
# Freeze lock and gravity with pause, then land and lock after resuming.
v.vars['Modo_Juego']='NORMAL';v.call_proc('Iniciar_Partida');v.vars.update(Pieza_Actual=2,Pieza_Rotacion=0,Pieza_Col=5,Pieza_Fila=19);v.call_proc('Actualizar_Fantasma')
v.sim_timer+=.1;v.call_proc('Tick');v.call_proc('Alternar_Pausa');t=v.vars['Tiempo_Juego'];lock=v.vars['Bloqueo']
for _ in range(100):v.sim_timer+=.1;v.call_proc('Tick')
assert v.vars['Tiempo_Juego']==t and v.vars['Bloqueo']==lock and not any(v.lists['Tablero'])
v.call_proc('Alternar_Pausa')
for _ in range(5):v.sim_timer+=.1;v.call_proc('Tick')
assert sum(int(c)>0 for c in v.lists['Tablero'])==4
logs['pauseLock']='PASS 10 simulated seconds paused; lock after resume'
# Near-full attack with deterministic holes, including top-out.
for i in range(100):
 v.call_proc('Iniciar_Partida');v.vars.update(Pieza_Actual=2,Pieza_Col=5,Pieza_Fila=2,Pieza_Rotacion=0)
 for row in range(4,21):
  for col in range(1,11):v.lists['Tablero'][(row-1)*10+col-1]=0 if col==(row%10+1) else 8
 if i%2==0:v.lists['Tablero'][0]=8
 v.call_proc('Garbage_Attack');assert len(v.lists['Tablero'])==200
 assert v.vars['Estado_Juego']==('GAMEOVER' if i%2==0 else 'JUGANDO')
logs['nearFullGarbage']='PASS 100 attacks; 50 expected top-outs'
Path('audit-evidence/long-stress-inputs.json').write_text(json.dumps(logs,indent=2))
for mode,result in logs.items():print(mode,{k:v for k,v in result.items() if k!='inputs'} if isinstance(result,dict) else result)
