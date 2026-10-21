"""Audit-only fixtures; never imported by the generator. Run from repo root."""
import sys,json,random,zipfile,hashlib,copy
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
from validate_sb3 import Scratch3VMInterpreter
random.seed(20261021)
def load(p):
 with zipfile.ZipFile(p) as z:return json.loads(z.read('project.json'))
p=load('NEXUS-BLOCKS-ENDLESS.sb3'); before=load('audit-evidence/before.sb3')
stripped=copy.deepcopy(p)
stripped['targets'][0]['costumes']=before['targets'][0]['costumes']
assert stripped==before,'Unexpected change outside backdrop metadata'
with zipfile.ZipFile('audit-evidence/before.sb3') as a,zipfile.ZipFile('NEXUS-BLOCKS-ENDLESS.sb3') as b:
 changed={c['md5ext'] for c in before['targets'][0]['costumes']}
 for n in a.namelist():
  if n!='project.json' and n not in changed:assert a.read(n)==b.read(n),n
print('PASS: project.json identical except Stage costume hashes; all other packed assets byte-identical')
v=Scratch3VMInterpreter(p); v.call_proc('Iniciar_Partida')
# Independent occupied-cell oracle, evaluating all orientations, borders, ceilings, floors.
x=v.lists['Offset_X'];y=v.lists['Offset_Y'];cases=0
for trial in range(3):
 board=[random.randint(1,8) if random.random()<.16 and trial else 0 for _ in range(200)];v.lists['Tablero']=board[:]
 for pid in range(1,8):
  for rot in range(4):
   idx=(pid-1)*16+rot*4; offsets=list(zip(x[idx:idx+4],y[idx:idx+4]));assert len(set(offsets))==4
   for col in range(-1,13):
    for row in range(-1,23):
     hit=any(not(1<=col+dx<=10 and 1<=row+dy<=20) or board[(row+dy-1)*10+col+dx-1]>0 for dx,dy in offsets)
     v.call_proc('Comprobar_Colision %s %s %s %s',pid,col,row,rot)
     assert bool(v.vars['Colision_Detectada'])==hit,(pid,col,row,rot)
     cases+=1
print('PASS collision oracle',cases)
# All 7 pieces: repeated rotation with floor/wall obstacles, every resulting successful placement valid.
rotations=0
for pid in range(1,8):
 for column in (2,5,8):
  v.call_proc('Iniciar_Partida');v.vars.update(Pieza_Actual=pid,Pieza_Col=column,Pieza_Fila=17,Pieza_Rotacion=0)
  for _ in range(100):
   v.call_proc('Rotar_Pieza');v.call_proc('Comprobar_Colision %s %s %s %s',pid,v.vars['Pieza_Col'],v.vars['Pieza_Fila'],v.vars['Pieza_Rotacion']);assert v.vars['Colision_Detectada']==0;rotations+=1
print('PASS consecutive rotations',rotations)
v.lists['Bolsa_7'].clear()
for _ in range(100):
 bag=[]
 for j in range(7):v.call_proc('Extraer_De_Bolsa');bag.append(v.vars['temp_pieza'])
 assert sorted(bag)==list(range(1,8))
print('PASS 700 draws / 100 bags')
# Continuous actions on actual board; restart at top-out only. This is a simulated bot, not visual play.
games=0;locks=0
for mode in ('NORMAL','HARD','CHAOS'):
 v.vars['Modo_Juego']=mode;v.call_proc('Iniciar_Partida')
 for n in range(300):
  if v.vars['Estado_Juego']!='JUGANDO':games+=1;v.call_proc('Iniciar_Partida')
  if n%4==0:v.call_proc('Guardar_Hold')
  for _ in range(random.randrange(4)):v.call_proc('Rotar_Pieza')
  for _ in range(random.randrange(5)):v.call_proc('Mover_Horizontal %s',random.choice((-1,1)))
  if v.vars['Estado_Juego']=='JUGANDO':v.call_proc('Caida_Instantanea');locks+=1
  assert len(v.lists['Tablero'])==200 and all(0<=i<=8 for i in v.lists['Tablero'])
print('PASS bot stress locks',locks,'top-out restarts',games)
# Every boundary through 100 lines, 1-4 clears, no duplicate level sound on empty recheck.
for prior in range(100):
 for count in range(1,5):
  v.call_proc('Iniciar_Partida');v.vars.update(Lineas=prior,Nivel=1+prior//10)
  v.lists['Tablero']=[0]*(200-count*10)+[3]*(count*10);v.sounds_played.clear()
  v.call_proc('Revisar_Y_Eliminar_Lineas');v.call_proc('Revisar_Y_Eliminar_Lineas')
  assert v.vars['Nivel']==1+(prior+count)//10
  assert v.sounds_played.count('12_level_up')==int((prior+count)//10>prior//10)
print('PASS 400 level-boundary/clear/sound fixtures')
# Confirmed defect fixtures, log observed behavior without repairing.
findings={}
v.call_proc('Iniciar_Partida');v.vars.update(Pieza_Guardada=0,Siguiente_Pieza=2,Pieza_Fila=10)
v.lists['Tablero'][14]=3;v.sounds_played.clear();v.call_proc('Guardar_Hold')
assert v.vars['Estado_Juego']=='GAMEOVER' and v.sounds_played.count('Sonido_GameOver')==2
findings['NB-AUDIT-001']={'empty_hold_blocked_spawn_sounds':v.sounds_played[:]}
v.call_proc('Iniciar_Partida');v.vars.update(Modo_Juego='CHAOS',Tiempo_Juego=23.1,Ultimo_Tick=0,Proximo_Ataque=25,Proximo_Evento=100,Evento_Caos='SPEED BURST',Evento_Fin=30)
v.sim_timer=.01;v.call_proc('Actualizar_Velocidad_Y_Caos');speed=v.vars['Velocidad_Caida'];v.call_proc('Tick')
assert v.vars['Evento_Caos']=='GARBAGE INCOMING' and v.vars['Velocidad_Caida']>speed*1.9
findings['NB-AUDIT-002']={'before_speed':speed,'after_speed':v.vars['Velocidad_Caida'],'event_end':30,'current_time':v.vars['Tiempo_Juego']}
v.call_proc('Iniciar_Partida');v.vars.update(Pieza_Guardada=2,Pieza_Fila=10,Tiempo_Juego=10,Reloj_Caida=9.36,Ultimo_Tick=0,Modo_Juego='NORMAL');v.call_proc('Guardar_Hold');v.sim_timer=.02;v.call_proc('Tick')
assert v.vars['Pieza_Fila']==3
findings['NB-AUDIT-003']={'swapped_piece_row_after_20ms':v.vars['Pieza_Fila'],'gravity':.65}
v.call_proc('Iniciar_Partida');v.lists['Tablero'][0]=3;v.sounds_played.clear();v.call_proc('Garbage_Attack')
assert v.vars['Estado_Juego']=='GAMEOVER' and 'Sonido_GameOver' not in v.sounds_played
findings['NB-AUDIT-004']={'garbage_gameover_sounds':v.sounds_played[:]}
print(json.dumps(findings,indent=2));Path('audit-evidence/findings.json').write_text(json.dumps(findings,indent=2))
# Graph reachability: traverse from actual event hats, expanding procedure calls.
for t in p['targets']:
 blocks=t['blocks'];defs={blocks[b['inputs']['custom_block'][1]]['mutation']['proccode']:bid for bid,b in blocks.items() if b['opcode']=='procedures_definition'}
 seen=set(); todo=[bid for bid,b in blocks.items() if b['opcode'].startswith('event_when')]
 while todo:
  bid=todo.pop()
  if bid in seen:continue
  seen.add(bid);b=blocks[bid]
  if b['next']:todo.append(b['next'])
  for inp in b['inputs'].values():
   for value in inp[1:]:
    if isinstance(value,str) and value in blocks:todo.append(value)
  if b['opcode']=='procedures_call':todo.append(defs[b['mutation']['proccode']])
 assert seen==set(blocks),(t['name'],set(blocks)-seen)
print('PASS all blocks reachable from event hats via calls (broadcast hats treated as roots)')
