"""Credits and the original Twemoji asset persist in the generated backdrops."""
import hashlib
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
                raw = z.read(costumes[name]['md5ext'])
                svg = raw.decode()
                root = ET.fromstring(svg)
                self.assertEqual((root.get('width'), root.get('height')), ('480','360'))
                self.assertEqual(svg.count('楽しんでください'),1)
                self.assertEqual(svg.count('by バスケス・ライアン'),1)
                if name == 'Fondo_Nightmare':
                    self.assertNotIn(THUMB, svg)
                    self.assertNotIn('M110 302h2v7h-2z', svg)
                    emoji = [el for el in root.iter() if el.get('id') == 'creator-thumb-emoji']
                    self.assertEqual(len(emoji), 1)
                    self.assertEqual(emoji[0].get('transform'), 'translate(115 294) scale(0.34)')
                    source = ET.parse(PROJECT.parent / 'assets/emoji/twemoji-1f44d.svg').getroot()
                    paths = [p for p in emoji[0] if p.tag.endswith('}path')]
                    self.assertEqual([p.attrib for p in paths], [p.attrib for p in source])
                    self.assertEqual({p.get('fill') for p in paths}, {'#FFDB5E', '#EE9547'})
                    self.assertIn('creativecommons.org/licenses/by/4.0/', svg)
                else:
                    self.assertEqual(svg.count(THUMB),1)
                    self.assertEqual(svg.count('M110 302h2v7h-2z'),1)
                    hashes = {'Fondo_Arcade':'fd9087837a1b51f81e8eed94785cbcf36eec61894fe7df106cd9aac185bd357d',
                              'Fondo_Caos':'9eb7d74e8f668010a53756486d1d951fc51225926ecd146033459c1ac6322ead'}
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), hashes[name])
                self.assertEqual('translate(-10 -98)' in svg,name=='Fondo_Nightmare')
        # Conservative signature bounds; Nightmare has score above and event
        # notices below, and does not touch the center board or controls.
        left, top, right, bottom = 30, 190, 122, 231
        self.assertTrue(0 <= left < right < 164 and 188 < top < bottom < 239)
        self.assertLess(bottom, 340)
        # Nominal 9 px CJK advances and scaled emoji bounds stay in the rail.
        emoji_left, emoji_top = 115 - 10, 294 - 98
        emoji_right, emoji_bottom = emoji_left + 36 * .34, emoji_top + 36 * .34
        self.assertGreaterEqual(emoji_left, 42 - 10 + 8 * 9)
        self.assertTrue(left <= emoji_left < emoji_right <= right)
        self.assertTrue(top <= emoji_top < emoji_bottom <= bottom)

if __name__ == '__main__': unittest.main()
