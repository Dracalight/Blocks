import {copyFile} from 'node:fs/promises'
for(const name of ['stockfish-19','stockfish-19-single'])for(const ext of ['wasm','js']){
 const file=name+'.'+ext
 await copyFile('node_modules/stockfish/bin/'+file,'app/engine/'+file)
}
