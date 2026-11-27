import {copyFile} from 'node:fs/promises'
for(const ext of ['wasm','js']){
 const file='stockfish-19-single.'+ext
 await copyFile('node_modules/stockfish/bin/'+file,'app/engine/'+file)
}
