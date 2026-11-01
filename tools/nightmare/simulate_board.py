"""Reproducible persistent-board bots driving the generated Scratch blocks.

This is an AST-interpreter test, not the official scheduler or a human game.
Placement planning uses a small Python heuristic; moves, rotation, collision,
hard drop, line clears, events, garbage and top-out execute in Scratch blocks.
Game clock advances a fixed 3 s per lock: it does not model gravity or latency.
"""
import argparse
import json
import random
import sys
import zipfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_sb3 import Scratch3VMInterpreter

SB3 = Path(__file__).resolve().parents[2] / 'NEXUS-BLOCKS-ENDLESS.sb3'


def cells(vm, piece, rot, col, row):
    i = (piece - 1) * 16 + rot * 4
    return [(col + int(vm.lists['Offset_X'][i+j]), row + int(vm.lists['Offset_Y'][i+j])) for j in range(4)]


def blocked(board, squares):
    return any(x < 1 or x > 10 or y < 1 or y > 20 or board[(y-1)*10+x-1] for x,y in squares)


def stats(board):
    heights=[]; holes=0
    for x in range(10):
        seen=False; height=0
        for y in range(20):
            if board[y*10+x]:
                if not seen: height=20-y
                seen=True
            elif seen: holes+=1
        heights.append(height)
    return max(heights),holes,sum(heights),sum(abs(a-b) for a,b in zip(heights,heights[1:]))


def choices(vm):
    board=vm.lists['Tablero']; p=int(vm.vars['Pieza_Actual']); x=int(vm.vars['Pieza_Col']); y=int(vm.vars['Pieza_Fila'])
    output=[]
    for rot in range(4):
        # Only rotations possible without kick at spawn, hence executable.
        if any(blocked(board,cells(vm,p,r,x,y)) for r in range(1,rot+1)): continue
        for target in range(1,11):
            step=1 if target>x else -1
            if any(blocked(board,cells(vm,p,rot,c,y)) for c in range(x,target+step,step)): continue
            row=y
            while not blocked(board,cells(vm,p,rot,target,row+1)): row+=1
            trial=board.copy()
            for cx,cy in cells(vm,p,rot,target,row): trial[(cy-1)*10+cx-1]=p
            full=sum(all(trial[r*10:(r+1)*10]) for r in range(20))
            h,holes,total,bump=stats(trial)
            output.append((rot,target,8*holes+0.55*total+0.8*bump+2*h-12*full))
    return output


def glitch(vm):
    # Reproduces a no-input player. Timed blocks and real collision rules still
    # run; this is not a proof of human fairness.
    while vm.vars['Estado_Juego'] in ('GLITCH_INTRO','GLITCH_PLAY','GLITCH_RESULT'):
        vm.sim_timer += .05
        vm.call_proc('Tick')


def run(data, seed, policy, limit):
    random.seed(seed); rng=random.Random(seed+10000)
    vm=Scratch3VMInterpreter(data); vm.vars.update(Modo_Juego='NIGHTMARE',NM_Submode='ENDLESS')
    vm.call_proc('Iniciar_Partida'); maximum=0; events=Counter(); garbage_rows=0; armor_hits=0; glitch_count=0; glitch_wins=0; chains=0; jam_locks=0; completed=0
    for lock in range(limit):
        if vm.vars['Estado_Juego']=='GLITCH_INTRO':
            glitch_count+=1; glitch(vm); glitch_wins += int(vm.vars['G_Success'])
        if vm.vars['Estado_Juego']!='JUGANDO': break
        jam_locks += int(vm.vars['NM_Jam'] > 0)
        if lock % 7 == 3: vm.call_proc('Guardar_Hold')
        if vm.vars['Estado_Juego'] != 'JUGANDO': break
        board=vm.lists['Tablero']; maximum=max(maximum,stats(board)[0]); available=choices(vm)
        if not available: break
        rot,target,_ = rng.choice(available) if policy=='basic' else min(available,key=lambda a:(a[2],a[0],a[1]))
        for _ in range(rot): vm.call_proc('Rotar_Pieza')
        while vm.vars['Pieza_Col'] != target:
            before=vm.vars['Pieza_Col']; vm.call_proc('Mover_Horizontal %s',1 if target>before else -1)
            assert vm.vars['Pieza_Col'] != before, 'planned horizontal path is blocked'
        vm.vars['Tiempo_Juego'] += 3
        previous_seq=vm.vars['NM_Sequence']; before_armor=sum(v==9 for v in board)
        vm.call_proc('Caida_Instantanea'); completed += 1
        if vm.vars['NM_Sequence']!=previous_seq:
            events[vm.vars['NM_Event']]+=1; chains += int(vm.vars['NM_Chain'] > 0)
        armor_hits += int(vm.vars['Armor_Hit'])
        # Every all-garbage bottom row represents one newly inserted row here.
        if vm.vars['NM_EventStart'] in ('DOUBLE','ARMOR_WARNING') and vm.vars['NM_Warning']==0:
            garbage_rows += int(sum(v in (8,9) for v in vm.lists['Tablero'][-10:])==9)
    h,holes,_,_=stats(vm.lists['Tablero'])
    return dict(seed=seed,policy=policy,locks=completed,lines=vm.vars['Lineas'],max_height=max(maximum,h),holes=holes,
                end=vm.vars['Estado_Juego'],events=dict(sorted(events.items())),
                garbage_rows_lower_bound=garbage_rows,armor_hits=armor_hits,chains=chains,jam_locks=jam_locks,glitches=glitch_count,glitch_wins=glitch_wins)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=80);args=parser.parse_args()
    with zipfile.ZipFile(SB3) as z: data=json.loads(z.read('project.json'))
    for policy in ('basic','heuristic'):
        for seed in (11,23,37): print(json.dumps(run(data,seed,policy,args.limit),sort_keys=True),flush=True)

if __name__=='__main__': main()
