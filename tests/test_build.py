import hashlib, json, subprocess, sys, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def references(value):
    if isinstance(value, list):
        if len(value)>=2 and value[0] in (2,3) and isinstance(value[1],str):
            yield value[1]
            if len(value)>2 and isinstance(value[2],str): yield value[2]
        for item in value: yield from references(item)
    elif isinstance(value,dict):
        for item in value.values(): yield from references(item)

class BuildTests(unittest.TestCase):
    def test_deterministic_build_and_valid_archive(self):
        subprocess.run([sys.executable,str(ROOT/'tools/build.py')],check=True,capture_output=True)
        artifact=ROOT/'dist/Geometry-Dash-SubZero-NEXUS-V1.sb3'
        first=artifact.read_bytes()
        subprocess.run([sys.executable,str(ROOT/'tools/build.py')],check=True,capture_output=True)
        self.assertEqual(first,artifact.read_bytes(),'SB3 archive bytes must be reproducible')
        with zipfile.ZipFile(artifact) as z:
            self.assertIsNone(z.testzip())
            names=set(z.namelist()); self.assertEqual(len(names),len(z.namelist()))
            project=json.loads(z.read('project.json'))
            self.assertEqual(project['meta']['agent'],'nexus-subzero-runtime-r2')
            self.assertEqual(len(project['targets']),9)
            global_vars=project['targets'][0]['variables']
            self.assertEqual({k:v[1] for k,v in global_vars.items()}['state'],'MENU')
            all_ids=set()
            costume_count=0
            for target in project['targets']:
                blocks=target['blocks']; ids=set(blocks)
                self.assertFalse(all_ids & ids,'Scratch block ids must be globally unique')
                all_ids |= ids
                for c in target['costumes']:
                    costume_count+=1
                    self.assertIn(c['md5ext'],names)
                    asset=z.read(c['md5ext'])
                    self.assertEqual(hashlib.md5(asset).hexdigest(),c['assetId'])
                    self.assertEqual(c['dataFormat'],'svg')
                owners={}
                for bid,b in blocks.items():
                    if b['topLevel']:
                        self.assertIsNone(b['parent'])
                    else:
                        self.assertIsNotNone(b['parent'],f'{target["name"]}:{bid} missing parent')
                        self.assertIn(b['parent'],ids)
                    if b['next']:
                        self.assertIn(b['next'],ids)
                        owners.setdefault(b['next'],[]).append(bid)
                        self.assertEqual(blocks[b['next']]['parent'],bid)
                    for child in references(b['inputs']):
                        self.assertIn(child,ids,f'dangling input {target["name"]}:{bid}->{child}')
                        owners.setdefault(child,[]).append(bid)
                        self.assertEqual(blocks[child]['parent'],bid)
                    field=b.get('fields',{}).get('VARIABLE')
                    if field:
                        var_id=field[1]
                        self.assertTrue(var_id in global_vars or var_id in target['variables'],f'unknown variable {var_id}')
                for bid,b in blocks.items():
                    self.assertLessEqual(len(owners.get(bid,[])),1,f'block {target["name"]}:{bid} reused by multiple parents')
                    if b['topLevel']: self.assertEqual(len(owners.get(bid,[])),0)
            self.assertGreaterEqual(costume_count,9)
            self.assertEqual(len(project['targets'][1]['blocks']),len(set(project['targets'][1]['blocks'])))
            self.assertEqual(project['targets'][1]['blocks'].keys().isdisjoint(project['targets'][2]['blocks'].keys()),True)
            ops=[b['opcode'] for t in project['targets'] for b in t['blocks'].values()]
            for required in ['control_if','control_wait','motion_changeyby','event_whenkeypressed','event_whenstageclicked','sensing_timer','operator_multiply']:
                self.assertIn(required,ops)
            self.assertFalse(any(n.lower().endswith(('.mp3','.wav','.ogg')) for n in names))
    def test_parameters_and_level_data_are_explicit_and_provisional(self):
        params=json.loads((ROOT/'engine/physics/parameters.json').read_text())
        level=json.loads((ROOT/'levels/runtime_acceptance/level.json').read_text())
        self.assertEqual(params['fixed_step_seconds'],1/120)
        self.assertEqual(params['source'],'prototype-tuning')
        self.assertEqual(len([o for o in level['objects'] if o['type']=='spike']),6)
        self.assertIn('not a SubZero level',level['status'])
if __name__=='__main__':unittest.main()
