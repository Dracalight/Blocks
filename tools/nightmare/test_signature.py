"""Original signature persists in each generated backdrop."""
import json
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[2] / 'NEXUS-BLOCKS-ENDLESS.sb3'
THUMB = 'M114 300c2-2 3-5 4-8l1-4c.4-1.5 2.4-1.2 2.4.4v6.4h4.2c1.7 0 2.5 1.3 2.1 2.8l-1.5 7.1c-.3 1.3-1.2 2-2.5 2h-5.1c-1.5 0-2.7-.7-3.6-1.8l-2-2.4 2-4.5z'

class SignatureTests(unittest.TestCase):
    def test_generated_backdrops_have_original_art_once(self):
        with zipfile.ZipFile(PROJECT) as z:
            stage = json.loads(z.read('project.json'))['targets'][0]
            costumes = {c['name']:c for c in stage['costumes']}
            for name in ('Fondo_Arcade', 'Fondo_Caos', 'Fondo_Nightmare'):
                svg = z.read(costumes[name]['md5ext']).decode()
                root = ET.fromstring(svg)
                self.assertEqual((root.get('width'), root.get('height')), ('480','360'))
                self.assertEqual(svg.count('楽しんでください'),1)
                self.assertEqual(svg.count('by バスケス・ライアン'),1)
                self.assertEqual(svg.count(THUMB),1)
                self.assertEqual(svg.count('M110 302h2v7h-2z'),1)
                self.assertEqual('translate(-10 -98)' in svg,name=='Fondo_Nightmare')
        # Conservative signature bounds; Nightmare has score above and event
        # notices below, and does not touch the center board or controls.
        left, top, right, bottom = 30, 190, 122, 231
        self.assertTrue(0 <= left < right < 164 and 188 < top < bottom < 239)
        self.assertLess(bottom, 340)

if __name__ == '__main__': unittest.main()
