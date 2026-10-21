from pathlib import Path
import sys,zipfile,json
sys.path.insert(0,'tools')
from validate_sb3 import Scratch3VMInterpreter
s=Path('audit-evidence/independent.py').read_text()
fixtures=s[s.index('# Confirmed defect fixtures'):s.index('# Graph reachability:')]
for label,path in [('main','audit-evidence/main.sb3'),('branch','audit-evidence/before.sb3')]:
 with zipfile.ZipFile(path) as z:v=Scratch3VMInterpreter(json.loads(z.read('project.json')))
 print('BASELINE',label)
 exec(fixtures.replace("Path('audit-evidence/findings.json')",f"Path('audit-evidence/{label}-findings.json')"))
