import {Chess} from './chess.js'
import {search,cancel} from './engine.js'
import {analyze,project,value} from './analyzer.js'
const $=id=>document.getElementById(id), ids=['side','mode','profile','ms','depth','hash','theme']
let game=new Chess(), rows=[], end='', selected='', busy=false, epoch=0, side='w', pending=null
const glyph={p:'♟',r:'♜',n:'♞',b:'♝',q:'♛',k:'♚'}
function save(){try{localStorage.setItem('nexus1',JSON.stringify({pgn:game.pgn(),end,side,rows,pending,settings:Object.fromEntries(ids.map(id=>[id,$(id).value]))}))}catch{$('speech').textContent='Almacenamiento local lleno.'}}
try{const s=JSON.parse(localStorage.nexus1);game.loadPgn(s.pgn);({rows,end,side,pending}=s);for(const id of ids)$(id).value=s.settings[id]}catch{}
function terminal(){return end||(game.isCheckmate()?'Jaque mate':game.isStalemate()?'Ahogado':game.isDraw()?'Tablas':'')}
function paint(){
 const squares=game.board().flatMap((rank,i)=>rank.map((piece,j)=>({piece,s:String.fromCharCode(97+j)+(8-i),dark:(i+j)%2})))
 const targets=selected?game.moves({square:selected,verbose:true}).map(m=>m.to):[]
 $('board').replaceChildren(...(side==='b'?squares.reverse():squares).map(({piece,s,dark})=>{
 const b=document.createElement('button');b.className=['sq',dark?'dark':'',selected===s?'selected':'',targets.includes(s)?'target':'',piece?.color==='w'?'white':''].join(' ')
 b.textContent=piece?glyph[piece.type]:'';b.setAttribute('aria-label',s);b.dataset.square=s
 if(s[0]===(side==='w'?'a':'h')||s[1]===(side==='w'?'1':'8')){const coord=document.createElement('small');coord.textContent=s;b.append(coord)}
 b.onclick=()=>click(s);b.draggable=piece?.color===side;b.ondragstart=e=>e.dataTransfer.setData('text/plain',s);b.ondragover=e=>e.preventDefault();b.ondrop=e=>{e.preventDefault();move(e.dataTransfer.getData('text/plain'),s)}
 return b}))
 $('status').textContent=terminal()||(busy?'Nexus está pensando…':game.isCheck()?'Tu rey está en jaque':'Tu turno')
 $('cat').classList.toggle('thinking',busy)
 $('history').textContent=game.history().map((m,i)=>(i%2?'':Math.floor(i/2+1)+'. ')+m).join(' ')||'Sin movimientos'
 const r=rows.at(-1);$('review').textContent=rows.map(r=>r.move+' · '+r.category).join(' / ')
 $('score').textContent=r?'Evaluación tras '+r.move+' · '+(r.current/100).toFixed(2):''
 const colors={'Sakura':['#f1cfdb','#ac7a94'],'Midnight':['#acbbcf','#505a7c'],'Oscuro':['#989598','#59545a'],'Clásico':['#e6d5af','#9a805e'],'Broken Gambit':['#d8c7b7','#91717c']}[$('theme').value]
 if(colors){document.body.style.setProperty('--a',colors[0]);document.body.style.setProperty('--b',colors[1])}
}
function click(s){if(busy||terminal()||game.turn()!==side)return
 if(game.get(s)?.color===side){selected=selected===s?'':s;paint()}else if(selected)move(selected,s)}
function move(from,to){if(busy||terminal()||game.turn()!==side)return
 const choices=game.moves({square:from,verbose:true}).filter(m=>m.to===to)
 if(!choices.length)return
 let promotion=choices[0].promotion
 if(promotion){promotion=prompt('Promoción: q (dama), r (torre), b (alfil), n (caballo)','q');if(!choices.some(m=>m.promotion===promotion))return}
 const previous=position(),legal=game.moves().length,m=game.move({from,to,promotion})
 pending={previous,legal,move:m};selected='';save();run()}
function position(){const hist=game.history({verbose:true});return 'fen '+(hist[0]?.before||game.fen())+(hist.length?' moves '+hist.map(m=>m.lan).join(' '):'')}
const number=(id,min,max)=>Math.min(max,Math.max(min,Math.floor(Number($(id).value)||min)))
async function run(){
 const token=++epoch;cancel();busy=Boolean(pending||!terminal()&&game.turn()!==side);$('retry').hidden=true;paint()
 if(!busy)return
 const opts={ms:number('ms',100,30000),depth:number('depth',1,99),hash:number('hash',1,128),full:$('profile').value==='Mittens Killer'}
 try{
 let after
 if(pending){
 const before=await search(pending.previous,opts);if(token!==epoch)return
 after=terminal()?null:await search(position(),opts);if(token!==epoch)return
 const r=analyze(pending.move,before,after,pending.legal,game);r.fen=pending.move.before;rows.push(r);pending=null
 $('speech').textContent=project(r,$('mode').value,rows.length);save()
 }
 if(!terminal()&&game.turn()!==side){after??=await search(position(),opts);if(token!==epoch)return
 const m=game.moves({verbose:true}).find(x=>x.lan===after.best);if(!m)throw Error('Respuesta UCI ilegal')
 game.move(m);save()}
 }catch(e){if(token===epoch){$('speech').textContent=e.message+'. Puedes elegir Móvil y reintentar.';$('retry').hidden=false}}
 finally{if(token===epoch){busy=false;paint()}}
}
function reset(g){epoch++;cancel();game=g;pending=null;rows=[];end='';selected='';side=$('side').value;$('speech').textContent='Otra posición. Otra posibilidad.';save();run()}
$('fresh').onclick=()=>reset(new Chess());$('retry').onclick=run
for(const [id,msg] of [['resign','Rendición'],['draw','Tablas acordadas']])$(id).onclick=()=>{if(terminal())return;epoch++;cancel();pending=null;busy=false;end=msg;game.setHeader('Result',id==='draw'?'1/2-1/2':side==='w'?'0-1':'1-0');save();paint()}
$('fen').onclick=()=>$('notation').value=game.fen();$('pgn').onclick=()=>$('notation').value=game.pgn()
$('load').onclick=()=>{try{const g=new Chess(),s=$('notation').value.trim();if(!s)throw Error();if(s.split(' ')[0].split('/').length===8)g.load(s);else g.loadPgn(s);reset(g)}catch{$('speech').textContent='La notación no es válida.'}}
ids.forEach(id=>$(id).onchange=()=>{save();paint()})
let touch
$('board').addEventListener('touchstart',e=>{touch=e.target.closest('.sq')?.dataset.square},{passive:true})
$('board').addEventListener('touchend',e=>{const t=e.changedTouches[0],to=document.elementFromPoint(t.clientX,t.clientY)?.closest('.sq')?.dataset.square;if(touch&&to&&touch!==to){e.preventDefault();move(touch,to)}},{passive:false})
run()
if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{})
let branchStep=0
function showReview(){
 const hist=game.history({verbose:true}),i=Number($('ply').value),m=hist[i-1]
 const pos=new Chess(m?.after||hist[0]?.before||game.fen())
 const row=m&&rows.find(r=>r.fen===m.before)
 if(branchStep&&row){pos.load(m.before);for(const lan of row.line.slice(0,branchStep))pos.move(lan)}
 const result=rows.length?Math.round(rows.reduce((n,r)=>n+100*Math.exp(-r.loss/150),0)/rows.length):null
 $('caption').textContent=(m?.san||'Inicio')+(row?' · '+row.category:'')+(branchStep?' · Variante '+branchStep:'')
 $('summary').textContent=result===null?'Sin análisis del jugador':'Precisión estimada '+result+'%. Mayor pérdida: '+rows.reduce((a,b)=>a.loss>=b.loss?a:b).move+'.'
 $('variation').disabled=!row?.line.length
 $('diagram').replaceChildren(...pos.board().flatMap((rank,i)=>rank.map((p,j)=>{const el=document.createElement('span');el.className='sq '+((i+j)%2?'dark ':'')+(p?.color==='w'?'white':'');el.textContent=p?glyph[p.type]:'';return el})))
}
$('inspect').onclick=()=>{$('ply').max=game.history().length;$('ply').value=$('ply').max;branchStep=0;showReview();$('viewer').showModal()}
$('closeReview').onclick=()=>$('viewer').close()
$('ply').oninput=()=>{branchStep=0;showReview()}
$('variation').onclick=()=>{const m=game.history({verbose:true})[Number($('ply').value)-1],row=rows.find(r=>r.fen===m.before);branchStep=(branchStep+1)%(row.line.length+1);showReview()}
