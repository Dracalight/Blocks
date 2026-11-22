import hashlib, json, subprocess, sys, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BuildTests(unittest.TestCase):
    def test_reproducible_native_sb3_and_structure(self):
        subprocess.run([sys.executable,str(ROOT/'tools/build.py')],check=True,capture_output=True)
        p=ROOT/'dist/Geometry-Dash-SubZero-NEXUS-V1.sb3'
        with zipfile.ZipFile(p) as z:
            self.assertEqual(z.testzip(),None)
            names=z.namelist(); self.assertIn('project.json',names)
            data=json.loads(z.read('project.json'))
            self.assertEqual(data['meta']['semver'],'3.0.0')
            self.assertEqual(len(data['targets']),3)
            for target in data['targets']:
                for costume in target['costumes']:
                    self.assertIn(costume['md5ext'],names)
            scripts=[b for t in data['targets'] for b in t['blocks'].values()]
            self.assertTrue(any(b['opcode']=='event_whenflagclicked' for b in scripts))
            self.assertTrue(any(b['opcode']=='control_forever' for b in scripts))
            self.assertTrue(any(b['opcode']=='sensing_touchingobject' for b in scripts))
            self.assertTrue(any(b['opcode']=='motion_changeyby' for b in scripts))
            self.assertFalse(any(n.lower().endswith(('.mp3','.wav','.ogg')) for n in names))
if __name__=='__main__': unittest.main()
