export function value(info){return info?.type==='mate'?Math.sign(info.value)*(10000-Math.abs(info.value)):info?.value??0}
export function analyze(move,before,after,legal,game){
 const previous=value(before.pv[1]), current=game.isCheckmate()?10000:game.isDraw()?0:-value(after.pv[1])
 const loss=Math.max(0,previous-current), best=before.best===move.lan
 const weights={p:1,n:3,b:3,r:5,q:9,k:0}, weightsOf=p=>p?weights[p]:0
 const sacrifice=after?.pv[1]?.line?.[0]?.slice(2,4)===move.to&&weightsOf(move.piece)>weightsOf(move.captured)+1
 const justified=sacrifice&&best&&current>=100&&after.pv[1].line.length>=4&&previous-value(before.pv[2])>=100&&before.pv[2]
 const onlyStrong=best&&before.pv[2]&&previous-value(before.pv[2])>=120
 const material=game.board().flat().reduce((n,p)=>n+(p?weightsOf(p.type)*(p.color===move.color?1:-1):0),0)
 const chance=cp=>1/(1+Math.exp(-cp/180))
 const threats=game.moves({verbose:true}).filter(m=>m.captured||m.san.includes('+')).map(m=>m.san)
 const category=game.isCheckmate()?'CHECKMATE':legal===1?'FORCED':justified?'BRILLIANT':onlyStrong?'GREAT':best?'BEST':previous>200&&current<50?'MISSED_OPPORTUNITY':loss>=200?'BLUNDER':loss>=100?'MISTAKE':loss>=50?'INACCURACY':loss<=15?'EXCELLENT':'GOOD'
 return {piece:move.piece,material,phase:game.board().flat().filter(Boolean).length<=12?'final':game.moveNumber()<=10?'apertura':'medio juego',sacrifice,threats,chanceBefore:chance(previous),chanceAfter:chance(current),move:move.san,category,previous,current,loss,best:before.best,line:before.pv[1]?.line||[],capture:move.captured,check:game.isCheck(),promotion:move.promotion}
}
export function project(row,mode,index,intensity=2){
 if(mode==='Silencioso'||mode==='Competitivo'&&index%3)return ''
 if(mode==='Entrenador')return row.move+' · '+row.category+'. Alternativa del motor: '+row.best+'. Pérdida estimada: '+row.loss+' cp.'
 const scene=row.sacrifice?'Con '+row.move+' ofreciste más de lo que recibiste':row.category==='BRILLIANT'?'Encontraste una respuesta que parecía imposible':row.category==='CHECKMATE'?'El rey se quedó sin salida':row.loss>=100?'Una puerta se cerró con '+row.move:row.capture?'Una pieza dejó su sitio':row.check?'El rey tuvo que escuchar':row.promotion?'Un peón estrenó otro destino':'Con '+row.move+' cambiaste el paisaje'
 const endings=mode==='Filósofo'?['la paciencia también ocupa espacio','decidir es renunciar a otro camino','el tiempo cambia el valor de las cosas']:['hasta la nostalgia necesita una casilla libre','quizá mañana lo veamos de otra forma','yo también guardo cartas que nunca envío','algunas despedidas caben en un solo paso','por suerte aún tenemos café']
 if(intensity===1)return scene+'.'
 return scene+(intensity===3?' y hasta el reloj contuvo el aliento':'')+'; '+endings[index%endings.length]+'.'
}
