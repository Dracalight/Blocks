"""Exercise generated Scratch blocks at visible rectangle edges, not a mirror model."""
import json
import unittest
import zipfile
from simulate_board import SB3, Scratch3VMInterpreter


class GlitchEdges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(SB3) as z:
            cls.project = json.loads(z.read('project.json'))

    def hit(self, phase, x, y, inner=.8):
        vm = Scratch3VMInterpreter(self.project)
        vm.vars.update(Estado_Juego='GLITCH_PLAY', G_Time=phase+inner,
                       G_PrevPhase=phase, G_TargetX=0, G_TargetY=0,
                       G_X=x, G_Y=y, G_HP=3, G_Invuln=0, Delta=0,
                       G_SoundedPhase=phase)
        vm.call_proc('Glitch_Advance')
        return vm.vars['G_HP'] == 2

    def test_charge_is_safe_for_every_attack(self):
        for phase in range(5):
            self.assertFalse(self.hit(phase, 0, 0, .5), phase)

    def test_beam_edges(self):
        self.assertTrue(self.hit(0, 0, 11))
        self.assertFalse(self.hit(0, 0, 12))

    def test_target_corner_and_edge(self):
        self.assertTrue(self.hit(1, 20, 15))
        self.assertFalse(self.hit(1, 20, 20))
        self.assertFalse(self.hit(1, 21, 0))

    def test_wall_gap_and_corner(self):
        self.assertTrue(self.hit(3, 0, 12))
        self.assertFalse(self.hit(3, 0, 10))
        self.assertFalse(self.hit(3, 19, 12))

    def test_fragment_corner_and_edge(self):
        self.assertTrue(self.hit(4, 19, 39))
        self.assertFalse(self.hit(4, 19, 44))
        self.assertFalse(self.hit(4, 20, 25))

    def test_ring_center_and_outer_safe_point(self):
        self.assertTrue(self.hit(2, 0, 0))
        self.assertFalse(self.hit(2, 40, 40))

if __name__ == '__main__':
    unittest.main()
