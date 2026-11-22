#!/usr/bin/env python3
"""Reproducible, dependency-free Scratch 3 project packager for NEXUS GD SubZero."""
import hashlib, json, zipfile, io, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def md5(b): return hashlib.md5(b).hexdigest()
# Original vector art only. No Geometry Dash artwork, fonts, or music is included.
player=b'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path fill="#19e6ef" stroke="#eaffff" stroke-width="4" d="M11 11h42v42H11z"/><path fill="#12253c" d="M20 22h9v9h-9zm16 0h9v9h-9zM21 39h23v6H21z"/><path fill="#ff42c8" d="M4 4h7v7H4zm49 49h7v7h-7z"/></svg>'''
hazard=b'''<svg xmlns="http://www.w3.org/2000/svg" width="72" height="64" viewBox="0 0 72 64"><path fill="#ff3b73" stroke="#fff0f5" stroke-width="3" d="M3 61 36 4l33 57z"/><path fill="#431b48" d="m36 20 5 25h-10z"/></svg>'''
backdrop=b'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360"><defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="#111536"/><stop offset="1" stop-color="#182c57"/></linearGradient><pattern id="p" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M0 0h48v48H0z" fill="none" stroke="#2a4e78" stroke-width="1"/></pattern></defs><path fill="url(#g)" d="M0 0h480v360H0z"/><path fill="url(#p)" d="M0 0h480v360H0z"/><path fill="#14203b" d="M0 230h480v130H0z"/><path stroke="#19e6ef" stroke-width="4" d="M0 230h480"/><circle cx="410" cy="58" r="35" fill="#ff42c8" opacity=".15"/></svg>'''
assets={}
for name,data,fmt in [('player.svg',player,'svg'),('hazard.svg',hazard,'svg'),('backdrop.svg',backdrop,'svg')]: assets[name]=(data,fmt)

def make_project():
    blocks={}; counter=0
    def b(op, parent=None, inputs=None, fields=None, top=False, x=0,y=0, shadow=False):
        nonlocal counter
        counter+=1; bid=f'b{counter:04d}'
        blocks[bid]={'opcode':op,'next':None,'parent':parent,'inputs':inputs or {},'fields':fields or {},'shadow':shadow,'topLevel':top}
        if top: blocks[bid]['x']=x;blocks[bid]['y']=y
        return bid
    def lit_num(n): return [1,[4,str(n)]]
    def lit_str(s): return [1,[10,s]]
    def lit_bool(v): return [1,[10,'true' if v else 'false']]
    def var(name,vid): return {'VARIABLE':[name,vid]}
    def chain(ids):
        for a,z in zip(ids,ids[1:]): blocks[a]['next']=z
    # Inputs referencing real blocks use [2,id]; shadows are embedded literals.
    def num_input(op,n):
        q=b(op);return [2,q]
    def eq(left,right):
        q=b('operator_equals',inputs={'OPERAND1':left,'OPERAND2':right}); return [2,q]
    # Player control
    ids=[]
    hat=b('event_whenflagclicked',top=True,x=30,y=30); ids.append(hat)
    init=b('data_setvariableto',parent=hat,fields=var('state','state'),inputs={'VALUE':lit_str('menu')}); ids.append(init)
    init2=b('data_setvariableto',parent=init,fields=var('vy','vy'),inputs={'VALUE':lit_num(0)}); ids.append(init2)
    init3=b('data_setvariableto',parent=init2,fields=var('distance','distance'),inputs={'VALUE':lit_num(0)}); ids.append(init3)
    goto=b('motion_gotoxy',parent=init3,inputs={'X':lit_num(-120),'Y':lit_num(-95)}); ids.append(goto)
    show=b('looks_show',parent=goto); ids.append(show)
    forever=b('control_forever',parent=show); ids.append(forever)
    # Each frame: if space and menu, start; if play and grounded, jump; physics; duration win.
    key=b('sensing_keypressed',parent=forever,fields={'KEY_OPTION':['space','space']})
    state_menu=eq([2,b('data_variable',parent=None,fields=var('state','state'))],lit_str('menu'))
    menu_if=b('control_if',parent=forever,inputs={'CONDITION':state_menu,'SUBSTACK':[2,b('data_setvariableto',fields=var('state','state'),inputs={'VALUE':lit_str('play')})]})
    # key press starts menu; separate branch for jump during play
    eq_play=eq([2,b('data_variable',fields=var('state','state'))],lit_str('play'))
    grounded=eq([2,b('operator_round',inputs={'NUM': [2,b('motion_yposition')]})],lit_num(-95))
    cond_jump=b('operator_and',inputs={'OPERAND1':eq_play,'OPERAND2':grounded})
    jump_set=b('data_setvariableto',fields=var('vy','vy'),inputs={'VALUE':lit_num(13)})
    jumpif=b('control_if',inputs={'CONDITION':[2,cond_jump],'SUBSTACK':[2,jump_set]})
    # Build a nested key conditional inside forever.
    press_if=b('control_if',parent=forever,inputs={'CONDITION':[2,key],'SUBSTACK':[2,menu_if]})
    blocks[menu_if]['next']=jumpif
    # Physics under state=play: y += vy, vy -= .8, distance += 1; ground clamp.
    yadd=b('motion_changeyby',inputs={'DY':[2,b('data_variable',fields=var('vy','vy'))]})
    grav=b('data_changevariableby',fields=var('vy','vy'),inputs={'VALUE':lit_num(-0.8)})
    dist=b('data_changevariableby',fields=var('distance','distance'),inputs={'VALUE':lit_num(1)})
    clampcond=eq([2,b('operator_round',inputs={'NUM':[2,b('motion_yposition')]})],lit_num(-95))
    clampv=b('data_setvariableto',fields=var('vy','vy'),inputs={'VALUE':lit_num(0)})
    clamp=b('control_if',inputs={'CONDITION':[2,clampcond],'SUBSTACK':[2,clampv]})
    physics=b('control_if',inputs={'CONDITION':eq([2,b('data_variable',fields=var('state','state'))],lit_str('play')),'SUBSTACK':[2,yadd]})
    blocks[yadd]['next']=grav;blocks[grav]['next']=dist;blocks[dist]['next']=clamp
    blocks[press_if]['next']=physics
    blocks[forever]['inputs']={'SUBSTACK':[2,press_if]}
    chain(ids)
    player_blocks=blocks
    # Hazard movement and collision loop; collision causes retry state, touching key restarts.
    hids=[]; hhat=b('event_whenflagclicked',top=True,x=430,y=30); hids.append(hhat)
    hstart=b('motion_gotoxy',parent=hhat,inputs={'X':lit_num(230),'Y':lit_num(-85)});hids.append(hstart)
    hforever=b('control_forever',parent=hstart);hids.append(hforever)
    hstate=eq([2,b('data_variable',fields=var('state','state'))],lit_str('play'))
    hmove=b('motion_changexby',inputs={'DX':lit_num(-5)})
    respcond=b('operator_lt',inputs={'OPERAND1':[2,b('motion_xposition')],'OPERAND2':lit_num(-240)})
    resp=b('motion_gotoxy',inputs={'X':lit_num(250),'Y':lit_num(-85)})
    respif=b('control_if',inputs={'CONDITION':[2,respcond],'SUBSTACK':[2,resp]})
    touch=b('sensing_touchingobject',fields={'TOUCHINGOBJECTMENU':['Player','Player']})
    deadset=b('data_setvariableto',inputs={'VALUE':lit_str('dead')},fields=var('state','state'))
    touchif=b('control_if',inputs={'CONDITION':[2,touch],'SUBSTACK':[2,deadset]})
    blocks[hmove]['next']=respif;blocks[respif]['next']=touchif
    blocks[hforever]['inputs']={'SUBSTACK':[2,b('control_if',inputs={'CONDITION':[2,hstate],'SUBSTACK':[2,hmove]})]}
    chain(hids)
    # Variables
    vars={'state':['state','menu'],'vy':['vy',0],'distance':['distance',0]}
    return {'targets':[{'isStage':True,'name':'Stage','variables':vars,'lists':{},'broadcasts':{},'blocks':{},'comments':{},'currentCostume':0,'costumes':[{'name':'night-grid','bitmapResolution':1,'dataFormat':'svg','assetId':md5(backdrop),'md5ext':md5(backdrop)+'.svg','rotationCenterX':240,'rotationCenterY':180}],'sounds':[],'volume':100,'layerOrder':0,'tempo':60,'videoTransparency':50,'videoState':'on','textToSpeechLanguage':None},
    {'isStage':False,'name':'Player','variables':{},'lists':{},'broadcasts':{},'blocks':player_blocks,'comments':{},'currentCostume':0,'costumes':[{'name':'cyan-cube','bitmapResolution':1,'dataFormat':'svg','assetId':md5(player),'md5ext':md5(player)+'.svg','rotationCenterX':32,'rotationCenterY':32}],'sounds':[],'volume':100,'layerOrder':1,'visible':True,'x':-120,'y':-95,'size':55,'direction':90,'draggable':False,'rotationStyle':'all around'},
    {'isStage':False,'name':'Pulse hazard','variables':{},'lists':{},'broadcasts':{},'blocks':blocks,'comments':{},'currentCostume':0,'costumes':[{'name':'pink-spike','bitmapResolution':1,'dataFormat':'svg','assetId':md5(hazard),'md5ext':md5(hazard)+'.svg','rotationCenterX':36,'rotationCenterY':32}],'sounds':[],'volume':100,'layerOrder':2,'visible':True,'x':230,'y':-85,'size':75,'direction':90,'draggable':False,'rotationStyle':'all around'}],
    'monitors':[{'id':'state','mode':'default','opcode':'data_variable','params':{'VARIABLE':'state'},'spriteName':'Stage','value':'menu','width':0,'height':0,'x':0,'y':0,'visible':False,'sliderMin':0,'sliderMax':100,'isDiscrete':True},{'id':'distance','mode':'default','opcode':'data_variable','params':{'VARIABLE':'distance'},'spriteName':'Stage','value':0,'width':0,'height':0,'x':0,'y':0,'visible':False,'sliderMin':0,'sliderMax':100,'isDiscrete':True},{'id':'vy','mode':'default','opcode':'data_variable','params':{'VARIABLE':'vy'},'spriteName':'Stage','value':0,'width':0,'height':0,'x':0,'y':0,'visible':False,'sliderMin':0,'sliderMax':100,'isDiscrete':True}],
    'extensions':[],'meta':{'semver':'3.0.0','vm':'0.2.0','agent':'nexus-subzero-v1'}}

def build():
    # Current build is a playable ENGINE_READY physics prototype: it intentionally does not claim level parity.
    project=make_project()
    out=ROOT/'dist'/'Geometry-Dash-SubZero-NEXUS-V1.sb3';out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.json',json.dumps(project,separators=(',',':')))
        for n,(data,_) in assets.items(): z.writestr(md5(data)+'.svg',data)
    return out
if __name__=='__main__': print(build())
