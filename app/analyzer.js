export function value(info){return info?.type==='mate'?Math.sign(info.value)*(10000-Math.abs(info.value)):info?.value??0}
export function analyze(move,before,after,legal,game){
 const previous=value(before.pv[1]), current=game.isCheckmate()?10000:game.isDraw()?0:-value(after.pv[1])
 const loss=Math.max(0,previous-current), best=before.best===move.lan
 const category=game.isCheckmate()?'CHECKMATE':legal===1?'FORCED':best?'BEST':previous>200&&current<50?'MISSED_OPPORTUNITY':loss>=200?'BLUNDER':loss>=100?'MISTAKE':loss>=50?'INACCURACY':loss<=15?'EXCELLENT':'GOOD'
 return {move:move.san,category,previous,current,loss,best:before.best,line:before.pv[1]?.line||[],capture:move.captured,check:game.isCheck(),promotion:move.promotion}
}
export function project(row,mode,index){
 if(mode==='Silencioso'||mode==='Competitivo'&&index%3)return ''
 if(mode==='Entrenador')return row.move+' · '+row.category+'. Alternativa del motor: '+row.best+'. Pérdida estimada: '+row.loss+' cp.'
 const scene=row.category==='CHECKMATE'?'El rey se quedó sin salida':row.loss>=100?'Una puerta se cerró con '+row.move:row.capture?'Una pieza dejó su sitio':row.check?'El rey tuvo que escuchar':row.promotion?'Un peón estrenó otro destino':'Con '+row.move+' cambiaste el paisaje'
 const endings=mode==='Filósofo'?['la paciencia también ocupa espacio','decidir es renunciar a otro camino','el tiempo cambia el valor de las cosas']:['hasta la nostalgia necesita una casilla libre','quizá mañana lo veamos de otra forma','yo también guardo cartas que nunca envío','algunas despedidas caben en un solo paso','por suerte aún tenemos café']
 return scene+'; '+endings[index%endings.length]+'.'
}
