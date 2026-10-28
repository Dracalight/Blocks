"""Adversarial fixtures against Scratch blocks; not full gameplay runs."""
import json
import unittest
import zipfile
from simulate_board import SB3, Scratch3VMInterpreter
from simulate_trials import protocol


class Adversarial(unittest.TestCase):
    def setUp(self):
        with zipfile.ZipFile(SB3) as z: project=json.loads(z.read('project.json'))
        self.vm=Scratch3VMInterpreter(project)
        self.vm.vars.update(Modo_Juego='NIGHTMARE',NM_Submode='TRIALS')
        self.vm.call_proc('Iniciar_Partida')

    def test_core_failed_protocol_penalty_retry_and_single_reward(self):
        v=self.vm; v.vars['Trial_Wave']=5  # explicit fixture, not a playthrough
        v.call_proc('Glitch_Begin'); frozen=(v.vars['Tiempo_Juego'],v.vars['Reloj_Caida'],v.vars['Bloqueo'])
        board=v.lists['Tablero'].copy(); score=v.vars['Puntuacion']
        self.assertEqual(protocol(v,False),0)
        self.assertEqual(v.vars['Trial_GlitchDone'],0)
        self.assertEqual((v.vars['NM_Event'],v.vars['NM_Rows'],v.vars['NM_Warning']),('DOUBLE',2,2))
        self.assertEqual(v.lists['Tablero'],board)
        self.assertEqual((v.vars['Tiempo_Juego'],v.vars['Reloj_Caida'],v.vars['Bloqueo']),frozen)
        for _ in range(2): v.call_proc('Nightmare_OnLock')
        self.assertEqual(v.vars['NM_Event'],'NONE')
        self.assertEqual(sum(c==8 for c in v.lists['Tablero']),18)
        self.assertEqual(v.vars['Estado_Juego'],'JUGANDO')
        v.call_proc('Glitch_Begin'); self.assertEqual(protocol(v,True),1)
        self.assertEqual(v.vars['Trial_GlitchDone'],1)
        self.assertEqual(v.vars['Puntuacion'],score+100)
        for _ in range(5): v.sim_timer+=.01;v.call_proc('Tick')
        self.assertEqual(v.vars['Puntuacion'],score+100)

    def test_double_garbage_topout_stops_second_row(self):
        v=self.vm; v.lists['Tablero'][0]=8
        v.vars.update(NM_Event='DOUBLE',NM_Warning=1,NM_Rows=2,NM_Cancelable=0,Lineas_Turno=0)
        v.call_proc('Nightmare_OnLock')
        self.assertEqual(v.vars['Estado_Juego'],'GAMEOVER')
        self.assertEqual(sum(c==8 for c in v.lists['Tablero']),9)

    def test_damaged_full_armor_resolves_without_hole(self):
        v=self.vm;v.lists['Tablero'][-20:]=[9]*20
        v.call_proc('Revisar_Y_Eliminar_Lineas')
        self.assertEqual(v.lists['Tablero'][-20:],[10]*20)
        v.call_proc('Revisar_Y_Eliminar_Lineas')
        self.assertEqual(v.vars['Armor_Broken'],2)
        self.assertFalse(any(v.lists['Tablero']))

if __name__=='__main__': unittest.main()
