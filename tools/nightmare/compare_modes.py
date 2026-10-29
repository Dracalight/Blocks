"""Paired seeded, persistent-board comparison using generated Scratch blocks.

Both modes get the same seeds, initial board, decisions and input cadence. Each Scratch random block has an independent seeded stream, so unrelated events
do not change the seven-bag stream; CHAOS can still replace a drawn piece. This
is an idealized bot, not a measurement of human perception or rendering.
"""
import argparse, json, random, zipfile
from collections import Counter
from simulate_board import SB3, choices, stats
from simulate_trials import MeasuredVM, tick, protocol


class CompareVM(MeasuredVM):
    def __init__(self, project, seed):
        super().__init__(project)
        self.seed=seed
        self.random_streams={}
        self.total_locks=0
        self.lock_start=self.blocks[self.procs['Fijar_Y_Procesar_Pieza'][0]]['next']

    def eval_reporter(self, blocks, bid, arg_env):
        blk=blocks[bid]
        if blk['opcode']=='operator_random':
            low=int(round(self._to_num(self.eval_input(blocks,blk,'FROM',arg_env))))
            high=int(round(self._to_num(self.eval_input(blocks,blk,'TO',arg_env))))
            rng=self.random_streams.setdefault(bid,random.Random(f'{self.seed}:{bid}'))
            return rng.randint(min(low,high),max(low,high))
        return super().eval_reporter(blocks,bid,arg_env)

    def exec_chain(self, blocks, start_id, arg_env):
        if blocks is self.blocks and start_id==self.lock_start:
            self.total_locks += 1
        return super().exec_chain(blocks,start_id,arg_env)


def run(project, mode, seed, policy, limit, seconds_per_lock):
    random.seed(seed)
    rng=random.Random(seed+20000)
    vm=CompareVM(project,seed)
    vm.vars.update(Modo_Juego=mode,NM_Submode='ENDLESS')
    vm.call_proc('Comenzar_Modo')
    while vm.vars['Estado_Juego']=='NIGHTMARE_INTRO': tick(vm,.1)
    locks=0; events=Counter(); glitch_wins=glitch_fails=0; burst_ticks=0
    prior_event='NONE'; prior_burst=0; max_height=0; ticks=0
    while locks<limit and ticks<limit*30:
        state=vm.vars['Estado_Juego']
        if state=='GLITCH_INTRO':
            win=protocol(vm,policy=='heuristic'); glitch_wins+=win;glitch_fails+=1-win
            continue
        if state!='JUGANDO': break
        # Both policies receive identical time to move between placements.
        for _ in range(round(seconds_per_lock*10)):
            tick(vm,.1);ticks+=1
            if vm.vars['Estado_Juego']!='JUGANDO': break
            burst=int(vm.vars['NM_Burst']==1) if mode=='NIGHTMARE' else int(vm.vars['Evento_Caos']=='SPEED BURST')
            burst_ticks+=burst
            if burst and not prior_burst: events['BURST_START']+=1
            prior_burst=burst
            event=vm.vars['NM_Event'] if mode=='NIGHTMARE' else vm.vars['Evento_Caos']
            if event!=prior_event and event!='NONE': events[str(event)]+=1
            prior_event=event
        if vm.vars['Estado_Juego']!='JUGANDO': continue
        avail=choices(vm)
        if not avail: break
        rot,col,_=rng.choice(avail) if policy=='basic' else min(avail,key=lambda x:(x[2],x[0],x[1]))
        for _ in range(rot): vm.call_proc('Rotar_Pieza')
        while vm.vars['Pieza_Col']!=col:
            before=vm.vars['Pieza_Col'];vm.call_proc('Mover_Horizontal %s',1 if col>before else -1)
            if before==vm.vars['Pieza_Col']: raise RuntimeError('move blocked')
        vm.call_proc('Caida_Instantanea');locks+=1
        max_height=max(max_height,stats(vm.lists['Tablero'])[0])
    return dict(mode=mode,seed=seed,policy=policy,locks=vm.total_locks,hard_drops=locks,lines=vm.vars['Lineas'],
                seconds=round(vm.vars['Tiempo_Juego'],2),state=vm.vars['Estado_Juego'],
                topout=int(vm.vars['Estado_Juego']=='GAMEOVER'),garbage_rows=vm.garbage_attacks,
                burst_seconds=round(burst_ticks*.1,1),events=dict(events),max_height=max_height,
                glitch_wins=glitch_wins,glitch_fails=glitch_fails)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=120);ap.add_argument('--cadence',type=float,default=1.0)
    args=ap.parse_args()
    with zipfile.ZipFile(SB3) as z: project=json.loads(z.read('project.json'))
    for policy in ('basic','heuristic'):
        for seed in (11,23,37,41,53,67):
            for mode in ('CHAOS','NIGHTMARE'):
                print(json.dumps(run(project,mode,seed,policy,args.limit,args.cadence),sort_keys=True),flush=True)
if __name__=='__main__':main()
