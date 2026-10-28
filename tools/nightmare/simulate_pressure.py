"""Seeded isolated scheduler stress, not a gameplay or balance estimate."""
import json
import random
import sys
import zipfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_sb3 import Scratch3VMInterpreter

project = Path(__file__).resolve().parents[2] / 'NEXUS-BLOCKS-ENDLESS.sb3'
with zipfile.ZipFile(project) as z:
    data = json.loads(z.read('project.json'))

for seed in (11, 23, 37, 41, 53, 67):
    random.seed(seed)
    rng = random.Random(seed + 900)
    vm = Scratch3VMInterpreter(data)
    vm.vars.update(Modo_Juego='NIGHTMARE', NM_Submode='ENDLESS')
    vm.call_proc('Iniciar_Partida')
    counts = Counter()
    for lock in range(100):
        # Empty-board fixture deliberately avoids top-out and player skill.
        vm.lists['Tablero'] = [0] * 200
        vm.vars['Tiempo_Juego'] = 21 + lock * 3
        vm.vars['Lineas_Turno'] = rng.choice((0, 0, 1, 2, 4))
        before = (vm.vars['NM_Event'], vm.vars['NM_Sequence'])
        vm.call_proc('Nightmare_OnLock')
        event = vm.vars['NM_Event']
        if vm.vars['NM_Sequence'] != before[1]: counts[event] += 1
        assert vm.vars['NM_Warning'] >= 0
        assert 0 <= vm.vars['NM_Rows'] <= 2
        assert 0 <= vm.vars['NM_Jam'] <= 7
        assert len(vm.lists['Tablero']) == 200
        assert vm.vars['Estado_Juego'] == 'JUGANDO'
    print(json.dumps({'seed':seed,'locks':100,'scheduled':dict(sorted(counts.items())),
                      'ending_event':vm.vars['NM_Event'],'rows':vm.vars['NM_Rows'],'jam':vm.vars['NM_Jam']},sort_keys=True))
