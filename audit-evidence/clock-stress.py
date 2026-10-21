import sys,json,zipfile
sys.path.insert(0,'tools')
from validate_sb3 import Scratch3VMInterpreter
with zipfile.ZipFile('NEXUS-BLOCKS-ENDLESS.sb3') as z:v=Scratch3VMInterpreter(json.loads(z.read('project.json')))
v.vars['Modo_Juego']='CHAOS';v.call_proc('Iniciar_Partida');v.sounds_played.clear();scrubs=0
for n in range(1,6001):
 # Explicit artificial survival aid: clear fixed cells every second, no gameplay claim.
 if n%10==0:v.lists['Tablero']=[0]*200;v.call_proc('Actualizar_Fantasma');scrubs+=1
 v.sim_timer=n/10;v.call_proc('Tick');assert v.vars['Estado_Juego']=='JUGANDO';assert len(v.lists['Tablero'])==200
assert v.vars['Tiempo_Juego']>599.99
print(json.dumps({'logicalSeconds':v.vars['Tiempo_Juego'],'ticks':6000,'boardScrubs':scrubs,'events':v.vars['Eventos'],'garbageWarningDispatches':v.sounds_played.count('11_chaos_warning'),'speed':v.vars['Velocidad_Caida'],'note':'Artificial clock fixture; board cleared every second; no real uninterrupted survival claim'},indent=2))
