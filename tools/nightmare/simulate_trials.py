"""Persistent Trials simulation using Scratch AST blocks and logical ticks.
No board or objective state is overwritten during a run. Input timing is an
idealized bot and is not a keyboard/scheduler or human playtest.
"""
import argparse
import json
import random
import zipfile
from collections import Counter
from simulate_board import SB3, Scratch3VMInterpreter, choices, stats


class MeasuredVM(Scratch3VMInterpreter):
    def __init__(self, project):
        super().__init__(project)
        self.garbage_attacks = 0
        self.garbage_start = self.blocks[self.procs['Garbage_Attack'][0]]['next']

    def exec_chain(self, blocks, start_id, arg_env):
        if blocks is self.blocks and start_id == self.garbage_start:
            self.garbage_attacks += 1
        return super().exec_chain(blocks, start_id, arg_env)


def tick(vm, dt=.1):
    vm.sim_timer += dt
    vm.call_proc('Tick')


def protocol(vm, active):
    ticks=0
    while vm.vars['Estado_Juego'] in ('GLITCH_INTRO','GLITCH_PLAY','GLITCH_RESULT'):
        if vm.vars['Estado_Juego']=='GLITCH_PLAY' and active:
            phase=int(vm.vars['G_Time']); inner=vm.vars['G_Time']-phase
            if phase==1 and .05 < inner < .45 and vm.vars['G_X'] < 30:
                vm.call_proc('Glitch_Move %s %s',6,0)
            elif phase==3 and .05 < inner < .55 and vm.vars['G_Y'] < -3:
                vm.call_proc('Glitch_Move %s %s',0,6)
        tick(vm,.05); ticks+=1
        if ticks>160: raise RuntimeError('Glitch did not terminate')
    return int(vm.vars['G_Success'])


def run(data, seed, policy, limit):
    random.seed(seed); rng=random.Random(seed+10000)
    vm=MeasuredVM(data)
    vm.vars.update(Modo_Juego='NIGHTMARE',NM_Submode='TRIALS')
    vm.call_proc('Comenzar_Modo')
    ticks=0
    while vm.vars['Estado_Juego']=='NIGHTMARE_INTRO': tick(vm);ticks+=1
    locks=0; high=0; wins=0; fails=0; events=Counter(); waves=[]; stalls=0
    while locks < limit:
        state=vm.vars['Estado_Juego']
        if state=='TRIAL_CLEAR' or state=='GAMEOVER': break
        if state=='TRIAL_INTERMISSION':
            previous=vm.vars['Trial_Wave']
            for _ in range(40):
                tick(vm); ticks+=1
                if vm.vars['Estado_Juego']!='TRIAL_INTERMISSION': break
            if vm.vars['Estado_Juego']=='TRIAL_INTERMISSION': raise RuntimeError('wave transition stalled')
            waves.append(previous); continue
        if state=='GLITCH_INTRO':
            outcome=protocol(vm,policy!='basic'); wins+=outcome;fails+=1-outcome;continue
        if state!='JUGANDO': raise RuntimeError('unexpected state '+state)
        if locks % 7 == 3: vm.call_proc('Guardar_Hold')
        if vm.vars['Estado_Juego']!='JUGANDO': break
        high=max(high,stats(vm.lists['Tablero'])[0]); available=choices(vm)
        if not available: stalls+=1; break
        rot,col,_ = rng.choice(available) if policy=='basic' else min(available,key=lambda a:(a[2],a[0],a[1]))
        for _ in range(rot): vm.call_proc('Rotar_Pieza')
        while vm.vars['Pieza_Col']!=col:
            before=vm.vars['Pieza_Col']; vm.call_proc('Mover_Horizontal %s',1 if col>before else -1)
            if vm.vars['Pieza_Col']==before: raise RuntimeError('illegal horizontal path')
        before=vm.vars['Trial_Event']; wave=vm.vars['Trial_Wave']
        vm.call_proc('Caida_Instantanea'); locks+=1
        if vm.vars['Trial_Event']>before: events[str(wave)+':'+str(vm.vars['NM_Event'])]+=1
        # Let the real clock/gravity run for 0.1 s, no progress variables set.
        if vm.vars['Estado_Juego']=='JUGANDO': tick(vm);ticks+=1
    if vm.vars['Estado_Juego']=='TRIAL_CLEAR': waves.append(5)
    h,holes,_,_=stats(vm.lists['Tablero'])
    return dict(seed=seed,policy=policy,locks=locks,lines=vm.vars['Lineas'],waves=waves,
                wave=vm.vars['Trial_Wave'],state=vm.vars['Estado_Juego'],max_height=max(high,h),
                holes=holes,events=dict(events),glitch_wins=wins,glitch_fails=fails,
                game_seconds=round(vm.vars['Tiempo_Juego'],2),stalls=stalls,
                garbage_rows=vm.garbage_attacks,top_out=int(vm.vars['Estado_Juego']=='GAMEOVER'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=300);args=parser.parse_args()
    with zipfile.ZipFile(SB3) as z: data=json.loads(z.read('project.json'))
    for policy in ('basic','heuristic'):
        for seed in (11,23,37): print(json.dumps(run(data,seed,policy,args.limit),sort_keys=True),flush=True)

if __name__=='__main__': main()
