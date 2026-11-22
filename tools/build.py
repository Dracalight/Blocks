#!/usr/bin/env python3
"""Reproducible Scratch 3 builder for the R2 runtime acceptance lane."""
from __future__ import annotations
import hashlib, json, zipfile
from itertools import count
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'/'Geometry-Dash-SubZero-NEXUS-V1.sb3'
PARAMS=json.loads((ROOT/'engine/physics/parameters.json').read_text())
LEVEL=json.loads((ROOT/'levels/runtime_acceptance/level.json').read_text())
SPIKES=[o for o in LEVEL['objects'] if o['type']=='spike']
PLATFORM_DATA=next(o for o in LEVEL['objects'] if o['type']=='platform')
PLAYER=b'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path fill="#19e6ef" stroke="#eaffff" stroke-width="4" d="M11 11h42v42H11z"/><path fill="#12253c" d="M20 22h9v9h-9zm16 0h9v9h-9zM21 39h23v6H21z"/></svg>'''
SPIKE=b'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="56" viewBox="0 0 64 56"><path fill="#ff3b73" stroke="#fff0f5" stroke-width="3" d="M2 54 32 3l30 51z"/></svg>'''
PLATFORM=b'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="24" viewBox="0 0 180 24"><path fill="#19e6ef" d="M0 2h180v22H0z"/><path fill="#ddffff" d="M0 2h180v5H0z"/></svg>'''
BACKDROP=b'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360"><defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="#111536"/><stop offset="1" stop-color="#182c57"/></linearGradient><pattern id="p" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M0 0h48v48H0z" fill="none" stroke="#2a4e78" stroke-width="1"/></pattern></defs><path fill="url(#g)" d="M0 0h480v360H0z"/><path fill="url(#p)" d="M0 0h480v360H0z"/><path fill="#14203b" d="M0 280h480v80H0z"/><path stroke="#19e6ef" stroke-width="4" d="M0 280h480"/><circle cx="410" cy="58" r="35" fill="#ff42c8" opacity=".15"/></svg>'''
def md5(b): return hashlib.md5(b).hexdigest()
def costume(name,data,cx,cy): return {'name':name,'bitmapResolution':1,'dataFormat':'svg','assetId':md5(data),'md5ext':md5(data)+'.svg','rotationCenterX':cx,'rotationCenterY':cy}
class Blocks:
 def __init__(self,prefix,ids): self.prefix=prefix;self.ids=ids;self.blocks={}
 def add(self,op,inputs=None,fields=None,top=False,x=0,y=0):
  i=f'{self.prefix}{next(self.ids):05d}'; b={'opcode':op,'next':None,'parent':None,'inputs':inputs or {},'fields':fields or {},'shadow':False,'topLevel':top}
  if top:b.update(x=x,y=y)
  self.blocks[i]=b
  for value in (inputs or {}).values():
   if isinstance(value,list) and len(value)>=2 and value[0] in (2,3):
    child=value[1]
    if isinstance(child,str) and child in self.blocks:self.blocks[child]['parent']=i
    if len(value)>2 and isinstance(value[2],str) and value[2] in self.blocks:self.blocks[value[2]]['parent']=i
  return i
 @staticmethod
 def n(v):return [1,[4,str(v)]]
 @staticmethod
 def s(v):return [1,[10,str(v)]]
 @staticmethod
 def boolean(v):return [1,[10,'true' if v else 'false']]
 @staticmethod
 def ref(i):return [2,i]
 def op(self,op,a,b=None):
  if op=='operator_not':return self.ref(self.add(op,{'OPERAND':a}))
  keys={'operator_add':('NUM1','NUM2'),'operator_subtract':('NUM1','NUM2'),'operator_multiply':('NUM1','NUM2'),'operator_divide':('NUM1','NUM2'),'operator_lt':('OPERAND1','OPERAND2'),'operator_gt':('OPERAND1','OPERAND2'),'operator_equals':('OPERAND1','OPERAND2'),'operator_and':('OPERAND1','OPERAND2'),'operator_or':('OPERAND1','OPERAND2')}[op]
  return self.ref(self.add(op,{keys[0]:a,keys[1]:b}))
 def var(self,n):return self.ref(self.add('data_variable',fields={'VARIABLE':[n,n]}))
 def set(self,n,v):return self.add('data_setvariableto',{'VALUE':v},{'VARIABLE':[n,n]})
 def change(self,n,v):return self.add('data_changevariableby',{'VALUE':v},{'VARIABLE':[n,n]})
 def seq(self,ids):
  for a,b in zip(ids,ids[1:]):self.blocks[a]['next']=b;self.blocks[b]['parent']=a
  return ids[0] if ids else None
 def stack(self,ids):return [2,self.seq(ids)] if ids else None
 def iff(self,c,body):return self.add('control_if',{'CONDITION':c,'SUBSTACK':self.stack(body)})
 def ifelse(self,c,yes,no):return self.add('control_if_else',{'CONDITION':c,'SUBSTACK':self.stack(yes),'SUBSTACK2':self.stack(no)})
 def forever(self,body):return self.add('control_forever',{'SUBSTACK':self.stack(body)})

def build_project():
 ids=count(1); spike_world=[o['world_x'] for o in SPIKES]
 defaults={'state':'MENU','resumeState':'PLAYING','vy':0,'distance':0,'checkpointDistance':0,'checkpointY':-62,'lastTime':0,'dt':0,'droppedTime':0,'accumulator':0,'steps':0,'previousY':0,'grounded':True,'attempts':0,'speed':180,'touchLatch':0}
 stage_vars={k:[k,v] for k,v in defaults.items()}
 stage={'isStage':True,'name':'Stage','variables':stage_vars,'lists':{},'broadcasts':{},'blocks':{},'comments':{},'currentCostume':0,'costumes':[costume('neon-grid',BACKDROP,240,180)],'sounds':[],'volume':100,'layerOrder':0,'tempo':60,'videoTransparency':50,'videoState':'on','textToSpeechLanguage':None}
 targets=[stage]; p=Blocks('P',ids)
 def vr(n):return p.var(n)
 def nv(v):return p.n(v)
 def op(o,a,b=None):return p.op(o,a,b)
 def set(n,v):return p.set(n,v)
 def start_body(mode='PLAYING'):return [set('state',p.s(mode)),p.change('attempts',nv(1)),p.add('motion_sety',{'Y':nv(PARAMS['ground_center_y'])}),set('vy',nv(0)),set('grounded',p.boolean(True)),set('distance',nv(0)),set('checkpointDistance',nv(0)),set('checkpointY',nv(PARAMS['ground_center_y'])),set('speed',nv(PARAMS['base_scroll_units_per_second'])),set('accumulator',nv(0)),set('lastTime',p.ref(p.add('sensing_timer')))]
 # Space, up-arrow, and stage-click hats start/restart or jump only while grounded.
 def keyhat(key):return p.add('event_whenkeypressed',fields={'KEY_OPTION':[key,None]},top=True,x=25,y=30)
 def control_hat(hat):
  start=op('operator_or',op('operator_equals',vr('state'),p.s('MENU')),op('operator_or',op('operator_equals',vr('state'),p.s('DEAD')),op('operator_equals',vr('state'),p.s('COMPLETE'))))
  active=op('operator_or',op('operator_equals',vr('state'),p.s('PLAYING')),op('operator_equals',vr('state'),p.s('PRACTICE')))
  jumpcond=op('operator_and',active,vr('grounded'))
  jump=[set('vy',nv(PARAMS['jump_speed_units_per_second'])),set('grounded',p.boolean(False))]
  p.seq([hat,p.ifelse(start,start_body(),[p.iff(jumpcond,jump)])])
 for k in ('space','up arrow'):control_hat(keyhat(k))
 click=p.add('event_whenstageclicked',top=True,x=25,y=250);control_hat(click)
 # V starts practice from the menu. Practice collisions restore the latest checkpoint.
 v_hat=keyhat('v')
 v_start=p.iff(op('operator_equals',vr('state'),p.s('MENU')),start_body('PRACTICE'))
 p.seq([v_hat,v_start])
 # P toggles pause while preserving the mode; R starts a clean normal attempt.
 p_hat=keyhat('p')
 resume_mode=p.ifelse(op('operator_equals',vr('state'),p.s('PLAYING')),
  [set('resumeState',p.s('PLAYING')),set('state',p.s('PAUSED'))],
  [p.ifelse(op('operator_equals',vr('state'),p.s('PRACTICE')),
   [set('resumeState',p.s('PRACTICE')),set('state',p.s('PAUSED'))],
   [p.iff(op('operator_equals',vr('state'),p.s('PAUSED')),[set('state',vr('resumeState'))])])])
 p.seq([p_hat,resume_mode])
 r_hat=keyhat('r')
 restart=p.iff(op('operator_or',op('operator_equals',vr('state'),p.s('DEAD')),op('operator_equals',vr('state'),p.s('COMPLETE'))),start_body())
 p.seq([r_hat,restart])
 # Fixed 120 Hz simulation driven by Scratch's monotonic project timer.
 now=p.ref(p.add('sensing_timer'))
 set_dt=set('dt',op('operator_subtract',now,vr('lastTime')))
 save_time=set('lastTime',p.ref(p.add('sensing_timer')))
 dt_hi=p.iff(op('operator_gt',vr('dt'),nv(PARAMS['max_frame_delta_seconds'])),
  [p.change('droppedTime',op('operator_subtract',vr('dt'),nv(PARAMS['max_frame_delta_seconds']))),set('dt',nv(PARAMS['max_frame_delta_seconds']))])
 dt_lo=p.iff(op('operator_lt',vr('dt'),p.n(0)),[set('dt',p.n(0))])
 step=PARAMS['fixed_step_seconds']
 def one_step():
  previous=set('previousY',p.ref(p.add('motion_yposition')))
  gravity=p.change('vy',op('operator_multiply',nv(PARAMS['gravity_units_per_second_squared']),nv(step)))
  vertical=p.add('motion_changeyby',{'DY':op('operator_multiply',vr('vy'),nv(step))})
  progress=p.change('distance',op('operator_multiply',vr('speed'),nv(step)))
  reset_ground=set('grounded',p.boolean(False))
  ground=PARAMS['ground_center_y']
  floor=p.iff(op('operator_lt',p.ref(p.add('motion_yposition')),nv(ground+0.01)),
   [p.add('motion_sety',{'Y':nv(ground)}),set('vy',nv(0)),set('grounded',p.boolean(True))])
  # Platform top and bounds come from the original level data, not from artwork.
  plat=PLATFORM_DATA
  onplat=op('operator_and',op('operator_gt',vr('distance'),nv(plat['start_distance'])),op('operator_lt',vr('distance'),nv(plat['end_distance'])))
  player_center_y=plat['top_y']+17.6
  crossed=op('operator_and',op('operator_gt',vr('previousY'),nv(player_center_y)),op('operator_lt',p.ref(p.add('motion_yposition')),nv(player_center_y)))
  land=p.iff(op('operator_and',onplat,op('operator_and',op('operator_lt',vr('vy'),nv(0)),crossed)),
   [p.add('motion_sety',{'Y':nv(player_center_y)}),set('vy',nv(0)),set('grounded',p.boolean(True))])
  hits=[]
  for worldx in spike_world:
   half=PARAMS['spike_half_width_world_units']
   near=op('operator_and',op('operator_gt',vr('distance'),nv(worldx+120-half)),op('operator_lt',vr('distance'),nv(worldx+120+half)))
   low=op('operator_lt',p.ref(p.add('motion_yposition')),nv(PARAMS['spike_hit_center_y_below']))
   playing_now=op('operator_equals',vr('state'),p.s('PLAYING'))
   practice_now=op('operator_equals',vr('state'),p.s('PRACTICE'))
   hit=op('operator_and',near,low)
   practice_rewind=p.iff(practice_now,[set('distance',vr('checkpointDistance')),p.add('motion_sety',{'Y':vr('checkpointY')}),set('vy',nv(0)),set('grounded',p.boolean(True)),set('accumulator',nv(0))])
   normal_death=p.iff(playing_now,[set('state',p.s('DEAD')),set('vy',nv(0))])
   hits.append(p.iff(hit,[practice_rewind,normal_death]))
  fast=p.iff(op('operator_gt',vr('distance'),nv(PARAMS['boost_start_world_distance'])),[set('speed',nv(PARAMS['boost_scroll_units_per_second']))])
  win=p.iff(op('operator_gt',vr('distance'),nv(PARAMS['finish_world_distance'])),[set('state',p.s('COMPLETE'))])
  checkpoint=p.iff(op('operator_and',op('operator_equals',vr('state'),p.s('PRACTICE')),op('operator_gt',vr('distance'),nv(plat['end_distance']))),
   [set('checkpointDistance',nv(plat['end_distance'])),set('checkpointY',nv(player_center_y))])
  return [previous,reset_ground,gravity,vertical,progress,floor,land,*hits,checkpoint,fast,win,set('accumulator',op('operator_subtract',vr('accumulator'),nv(step))),p.change('steps',nv(1))]
 play=op('operator_or',op('operator_equals',vr('state'),p.s('PLAYING')),op('operator_equals',vr('state'),p.s('PRACTICE')))
 def has_step():
  return op('operator_or',op('operator_gt',vr('accumulator'),nv(step)),op('operator_equals',vr('accumulator'),nv(step)))
 substeps=[p.iff(has_step(),one_step()) for _ in range(PARAMS['max_substeps_per_visual_update'])]
 run_sim=[p.change('accumulator',vr('dt')),set('steps',nv(0)),*substeps]
 loop=p.forever([set_dt,save_time,dt_hi,dt_lo,p.iff(play,run_sim),p.add('control_wait',{'DURATION':p.n(0)})])
 flag=p.add('event_whenflagclicked',top=True,x=25,y=20)
 init=[set('state',p.s('MENU')),set('resumeState',p.s('PLAYING')),set('vy',p.n(0)),set('distance',p.n(0)),set('checkpointDistance',p.n(0)),set('checkpointY',nv(PARAMS['ground_center_y'])),set('lastTime',p.ref(p.add('sensing_timer'))),set('dt',p.n(0)),set('droppedTime',p.n(0)),set('accumulator',p.n(0)),set('steps',p.n(0)),set('previousY',nv(PARAMS['ground_center_y'])),set('grounded',p.boolean(True)),set('attempts',p.n(0)),set('speed',nv(PARAMS['base_scroll_units_per_second'])),p.add('motion_gotoxy',{'X':p.n(-120),'Y':nv(PARAMS['ground_center_y'])}),p.add('looks_show'),loop]
 p.seq([flag,*init])
 targets.append({'isStage':False,'name':'Player','variables':{},'lists':{},'broadcasts':{},'blocks':p.blocks,'comments':{},'currentCostume':0,'costumes':[costume('cyan-runner',PLAYER,32,32)],'sounds':[],'volume':100,'layerOrder':1,'visible':True,'x':-120,'y':PARAMS['ground_center_y'],'size':55,'direction':90,'draggable':False,'rotationStyle':'all around'})
 # Six independent visual obstacle targets. Their position is camera(world position - distance).
 for i,wx in enumerate(spike_world,1):
  b=Blocks(f'H{i}',ids)
  def visible_test():return b.op('operator_and',b.op('operator_gt',b.var('distance'),b.n(wx-260)),b.op('operator_lt',b.var('distance'),b.n(wx+500)))
  body=[b.add('motion_setx',{'X':b.op('operator_subtract',b.n(wx),b.var('distance'))}),b.add('motion_sety',{'Y':b.n(-48)}),b.iff(visible_test(),[b.add('looks_show')]),b.iff(b.op('operator_not',visible_test()),[b.add('looks_hide')]),b.add('control_wait',{'DURATION':b.n(0)})]
  fh=b.add('event_whenflagclicked',top=True,x=25,y=20);b.seq([fh,b.add('looks_hide'),b.forever(body)])
  targets.append({'isStage':False,'name':f'Spike {i:02d}','variables':{},'lists':{},'broadcasts':{},'blocks':b.blocks,'comments':{},'currentCostume':0,'costumes':[costume('original-pink-spike',SPIKE,32,28)],'sounds':[],'volume':100,'layerOrder':i+1,'visible':False,'x':240,'y':-48,'size':75,'direction':90,'draggable':False,'rotationStyle':'all around'})
 b=Blocks('L',ids);platform_world=(PLATFORM_DATA['start_distance']+PLATFORM_DATA['end_distance'])/2-120;px=b.op('operator_subtract',b.n(platform_world),b.var('distance'))
 def platform_visible():return b.op('operator_and',b.op('operator_gt',b.var('distance'),b.n(PLATFORM_DATA['start_distance']-300)),b.op('operator_lt',b.var('distance'),b.n(PLATFORM_DATA['end_distance']+300)))
 platloop=b.forever([b.add('motion_setx',{'X':px}),b.add('motion_sety',{'Y':b.n(7)}),b.iff(platform_visible(),[b.add('looks_show')]),b.iff(b.op('operator_not',platform_visible()),[b.add('looks_hide')]),b.add('control_wait',{'DURATION':b.n(0)})])
 ph=b.add('event_whenflagclicked',top=True,x=25,y=20);b.seq([ph,b.add('looks_hide'),platloop])
 targets.append({'isStage':False,'name':'Cyan platform','variables':{},'lists':{},'broadcasts':{},'blocks':b.blocks,'comments':{},'currentCostume':0,'costumes':[costume('original-platform',PLATFORM,90,12)],'sounds':[],'volume':100,'layerOrder':9,'visible':False,'x':240,'y':7,'size':100,'direction':90,'draggable':False,'rotationStyle':'all around'})
 monitors=[]
 for mid,val,y in [('state','MENU',10),('distance',0,35),('attempts',0,60)]:monitors.append({'id':mid,'mode':'default','opcode':'data_variable','params':{'VARIABLE':mid},'spriteName':'Stage','value':val,'width':100,'height':20,'x':10,'y':y,'visible':True,'sliderMin':0,'sliderMax':100,'isDiscrete':True})
 return {'targets':targets,'monitors':monitors,'extensions':[],'meta':{'semver':'3.0.0','vm':'0.2.0','agent':'nexus-subzero-runtime-r2'}}
def build():
 project=build_project();assets={md5(x)+'.svg':x for x in (PLAYER,SPIKE,PLATFORM,BACKDROP)};OUT.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in [('project.json',json.dumps(project,separators=(',',':'),ensure_ascii=False).encode()),*sorted(assets.items())]:
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
 return OUT
if __name__=='__main__':print(build())
