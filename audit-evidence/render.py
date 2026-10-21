from pathlib import Path
import zipfile,json,subprocess
from PIL import Image,ImageChops,ImageDraw
root=Path('audit-evidence')
for label,src in [('before',root/'before.sb3'),('after',Path('NEXUS-BLOCKS-ENDLESS.sb3'))]:
 with zipfile.ZipFile(src) as z:
  p=json.loads(z.read('project.json'))
  for c in p['targets'][0]['costumes']:
   data=z.read(c['md5ext']);(root/f'{label}-{c["name"]}.svg').write_bytes(data)

subprocess.run(["node", "audit-evidence/render-sharp.cjs"],check=True)
for name in ('Fondo_Arcade','Fondo_Caos'):
 a=Image.open(root/f'before-{name}.png').convert('RGB');b=Image.open(root/f'after-{name}.png').convert('RGB');diff=ImageChops.difference(a,b)
 print(name,'changed pixels bbox',diff.getbbox());outside=diff.copy();ImageDraw.Draw(outside).rectangle((0,285,145,337),fill='black');assert outside.getbbox() is None
 canvas=Image.new('RGB',(960,390),'#ffffff');canvas.paste(a,(0,30));canvas.paste(b,(480,30));d=ImageDraw.Draw(canvas);d.text((12,9),'BEFORE / ANTES',fill='black');d.text((492,9),'AFTER / DESPUES (librsvg, not Scratch)',fill='black');canvas.save(root/f'comparison-{name}.png')
 canvas.crop((0,315,960,369)).resize((1920,108)).save(root/f'credit-detail-{name}.png')
