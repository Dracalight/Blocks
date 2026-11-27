let worker, rejectActive
export function cancel(){
  worker?.terminate()
  worker=null
  rejectActive?.(new DOMException('Cancelado','AbortError'))
  rejectActive=null
}
export function search(position,opts){
  cancel()
  return new Promise((resolve,reject)=>{
    const multi=opts.full&&globalThis.crossOriginIsolated&&opts.threads>1
    const name=opts.full?(multi?'stockfish-19':'stockfish-19-single'):'stockfish-19-lite-single'
    const active=new Worker('./engine/'+name+'.js')
    worker=active
    const pv={}
    const timer=setTimeout(()=>fail(Error('Tiempo de espera del motor agotado')),60000+opts.ms)
    function close(){clearTimeout(timer);active.terminate();worker=null;rejectActive=null}
    function fail(error){close();reject(error)}
    rejectActive=fail
    active.onerror=()=>fail(Error('No se pudo cargar el motor seleccionado'))
    active.onmessage=({data})=>{
      const send=line=>active.postMessage(line)
      if(data==='uciok'){
        if(multi)send('setoption name Threads value '+opts.threads)
        send('setoption name Hash value '+opts.hash)
        send('setoption name MultiPV value 2')
        send('isready')
      }
      if(data==='readyok'){send('position '+position);send('go depth '+opts.depth+' movetime '+opts.ms)}
      const info=data.match(/multipv (\d+).*?score (cp|mate) (-?\d+).*? pv (.+)/)
      if(info)pv[info[1]]={type:info[2],value:Number(info[3]),line:info[4].split(' ')}
      if(data.startsWith('bestmove ')){close();resolve({best:data.split(' ')[1],pv})}
    }
    active.postMessage('uci')
  })
}
