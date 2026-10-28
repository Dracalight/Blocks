"""Rutas conservadoras en una cuadrícula: no mide latencia ni FPS reales."""
import unittest


def hit(pattern, t, x, y, target):
    if t <= .6:
        return False
    pos = -55 + (t - .6) * 275
    if pattern == 0: return abs(y) < 6
    if pattern == 1: return abs(x-target[0]) < 15 and abs(y-target[1]) < 15
    if pattern == 2: return x*x+y*y < ((t-.6)*75)**2
    if pattern == 3: return abs(x-pos) < 15 and abs(y) > 17
    return (abs(x-pos) < 15 and abs(y-25) < 15) or (abs(x+pos) < 15 and abs(y+25) < 15)


def safe_route(pattern, start):
    x,y = start
    for tick in range(20):
        t = tick * .05
        # Primer paso inmediato, después una demora conservadora de 200 ms.
        if tick == 0 or tick >= 4:
            if pattern == 0 and abs(y) < 12:
                y += 6 if y >= 0 else -6
            elif pattern == 1 and abs(x-start[0]) < 18:
                x += -6 if start[0] > 0 else 6
            elif pattern == 2 and abs(x) < 36:
                x += 6 if x >= 0 else -6
            elif pattern == 3 and abs(y) > 12:
                y += -6 if y > 0 else 6
            elif pattern == 4 and abs(y) > 6:
                y += -6 if y > 0 else 6
            x=max(-55,min(55,x));y=max(-55,min(55,y))
        if hit(pattern,t,x,y,start):
            return False
    return True


class GlitchRoutes(unittest.TestCase):
    def test_each_pattern_has_an_axis_aligned_route_from_sampled_positions(self):
        for pattern in range(5):
            for x in range(-54,55,6):
                for y in range(-54,55,6):
                    self.assertTrue(safe_route(pattern,(x,y)), (pattern,x,y))


if __name__ == '__main__': unittest.main()
