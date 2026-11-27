// Paired openings. Each executable must implement stdin/stdout UCI.
import {spawn} from 'node:child_process'
import {createInterface} from 'node:readline'
import {once} from 'node:events'
import os from 'node:os'
import {Chess} from '../app/chess.js'
const [a,b]=process.argv.slice(2)
const ms=Number(process.env.MOVE_MS||40)
function engine(path){
 const proc=path?spawn(path):spawn(process.execPath,['node_modules/stockfish/bin/stockfish-19-lite-single.js'])
 const lines=createInterface({input:proc.stdout})
 const send=s=>proc.stdin.write(s+'\n')
 async function until(prefix){
 const abort=AbortSignal.timeout(30000)
 return await new Promise((resolve,reject)=>{const listener=line=>{if(line.startsWith(prefix)){lines.off('line',listener);resolve(line)}};lines.on('line',listener);abort.addEventListener('abort',()=>{lines.off('line',listener);reject(Error('UCI timeout'))},{once:true})})
 }
 return {async init(){send('uci');await until('uciok');send('setoption name Threads value 1');send('setoption name Hash value 16');send('isready');await until('readyok')},
 async move(history){send('position startpos moves '+history.join(' '));send('go movetime '+ms);return (await until('bestmove ')).split(' ')[1]},close(){proc.kill()}}
}
let wins=0,losses=0,draws=0
console.log(os.platform(),os.cpus()[0].model,{ms,threads:1,hashMiB:16,a,b})
for(const opening of ['e4 e5','d4 d5'])for(const flip of [0,1]){
 const engines=[engine(a),engine(b)],g=new Chess()
 try{await Promise.all(engines.map(e=>e.init()));for(const m of opening.split(' '))g.move(m)
 const history=g.history({verbose:true}).map(m=>m.lan)
 while(!g.isGameOver()){const turn=Number(g.turn()==='b')^flip,m=await engines[turn].move(history);g.move(m);history.push(m)}
 if(!g.isCheckmate())draws++;else if(Number(g.turn()==='b')===flip)losses++;else wins++
 console.log(g.pgn(),{wins,losses,draws})}finally{engines.forEach(e=>e.close())}
}
const n=wins+losses+draws,s=(wins+draws/2)/n,eps=Math.sqrt(Math.log(40)/(2*n))
const elo=x=>400*Math.log10(x/(1-x))
console.log('Elo descriptivo',elo(s),'intervalo conservador para partidas independientes',elo(Math.max(0,s-eps)),elo(Math.min(1,s+eps)))
