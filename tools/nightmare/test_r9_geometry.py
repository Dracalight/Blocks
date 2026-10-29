"""Exercise generated Scratch blocks at visible rectangle edges, not a mirror model."""
import json
import math
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

    def test_rectangles_grid_against_distance_to_rectangle(self):
        # Independent oracle: shortest Manhattan distance from core center to
        # the drawn rectangle must be strictly less than the diamond radius.
        vm = Scratch3VMInterpreter(self.project)
        for phase, rects in ((0,[(0,0,60,6)]),(1,[(0,0,15,15)]),
                             (3,[(0,38.5,14,21.5),(0,-38.5,14,21.5)]),
                             (4,[(0,25,14,14),(0,-25,14,14)])):
            for x in range(-50,51,5):
                for y in range(-50,51,5):
                    expected=any(max(abs(x-cx)-hx,0)+max(abs(y-cy)-hy,0)<6
                                 for cx,cy,hx,hy in rects)
                    # Avoid exact boundaries sensitive to decimal representation.
                    if any(abs(max(abs(x-cx)-hx,0)+max(abs(y-cy)-hy,0)-6)<1e-8 for cx,cy,hx,hy in rects): continue
                    vm.vars.update(Estado_Juego='GLITCH_PLAY',G_Time=phase+.8,G_PrevPhase=phase,
                                   G_TargetX=0,G_TargetY=0,G_X=x,G_Y=y,G_HP=3,G_Invuln=0,Delta=0,G_SoundedPhase=phase)
                    vm.call_proc('Glitch_Advance')
                    self.assertEqual(vm.vars['G_HP']==2,expected,(phase,x,y))

    def test_ring_grid_against_independent_segment_distance(self):
        # Minimum Euclidean distance to the four sides of the drawn diamond.
        vertices = [(6,0),(0,6),(-6,0),(0,-6)]
        vm = Scratch3VMInterpreter(self.project)
        for inner in (.7, .8, .95):
            radius = (inner-.6)*75*31/30
            for x in range(-30,31,5):
                for y in range(-30,31,5):
                    distances=[]
                    for i,(ax,ay) in enumerate(vertices):
                        bx,by=vertices[(i+1)%4]; dx,dy=bx-ax,by-ay
                        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
                        distances.append(math.hypot(x-(ax+t*dx),y-(ay+t*dy)))
                    distance=0 if abs(x)+abs(y)<=6 else min(distances)
                    if abs(distance-radius)<1e-8: continue
                    vm.vars.update(Estado_Juego='GLITCH_PLAY',G_Time=2+inner,G_PrevPhase=2,
                                   G_X=x,G_Y=y,G_HP=3,G_Invuln=0,Delta=0,G_SoundedPhase=2)
                    vm.call_proc('Glitch_Advance')
                    self.assertEqual(vm.vars['G_HP']==2, distance<radius,(inner,x,y,distance,radius))

    def test_ring_center_and_outer_safe_point(self):
        self.assertTrue(self.hit(2, 0, 0))
        self.assertFalse(self.hit(2, 40, 40))

if __name__ == '__main__':
    unittest.main()
