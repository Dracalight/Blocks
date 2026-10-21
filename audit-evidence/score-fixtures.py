import sys,json,zipfile
sys.path.insert(0,'tools')
from validate_sb3 import Scratch3VMInterpreter
with zipfile.ZipFile('NEXUS-BLOCKS-ENDLESS.sb3') as z:v=Scratch3VMInterpreter(json.loads(z.read('project.json')))
v.call_proc('Iniciar_Partida')
for expected in [100,250,450]:
 v.lists['Tablero']=[0]*190+[2]*10;v.call_proc('Revisar_Y_Eliminar_Lineas');assert v.vars['Puntuacion']==expected
v.call_proc('Revisar_Y_Eliminar_Lineas');assert v.vars['Combo']==-1
v.lists['Tablero']=[0]*190+[2]*10;v.call_proc('Revisar_Y_Eliminar_Lineas');assert v.vars['Puntuacion']==550
print('PASS combos: cumulative 100,250,450; empty clear resets; next single gives 550')
v.call_proc('Iniciar_Partida');v.vars.update(Multiplicador_Caos=2);v.lists['Tablero']=[0]*190+[2]*10;v.call_proc('Revisar_Y_Eliminar_Lineas');assert v.vars['Puntuacion']==200
v.lists['Tablero']=[0]*190+[2]*10;v.call_proc('Revisar_Y_Eliminar_Lineas');assert v.vars['Puntuacion']==450
print('PASS injected multiplier2: base score doubled; combo bonus retains existing formula (50, not doubled)')
