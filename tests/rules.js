import {Chess} from '../app/chess.js'
import {analyze,project} from '../app/analyzer.js'
import assert from 'node:assert/strict'
import test from 'node:test'
const play=(list,fen)=>{const g=new Chess(fen);for(const m of list.split(' '))g.move(m);return g}
test('legalidad, jaque y mate',()=>{assert.throws(()=>new Chess().move('e5'));const g=play('f3 e5 g4 Qh4#');assert.ok(g.isCheck()&&g.isCheckmate())})
test('enroque',()=>assert.equal(play('e4 e5 Nf3 Nc6 Bc4 Nf6 O-O').get('f1').type,'r'))
test('al paso',()=>assert.equal(play('e4 a6 e5 d5 exd6').get('d5'),undefined))
test('cuatro promociones',()=>{for(const p of 'QRBN')assert.equal(play('a8='+p,'7k/P7/8/8/8/8/8/7K w - - 0 1').get('a8').type,p.toLowerCase())})
test('ahogado, material y 50 movimientos',()=>{assert.ok(new Chess('7k/5K2/6Q1/8/8/8/8/8 b - - 0 1').isStalemate());assert.ok(new Chess('7k/8/8/8/8/8/8/K7 w - - 0 1').isInsufficientMaterial());assert.ok(new Chess('7k/8/8/8/8/8/8/KR6 w - - 100 1').isDrawByFiftyMoves())})
test('repetición y persistencia PGN',()=>{const g=play('Nf3 Nf6 Ng1 Ng8 Nf3 Nf6 Ng1 Ng8'), copy=new Chess();copy.loadPgn(g.pgn());assert.equal(copy.fen(),g.fen());assert.ok(copy.isThreefoldRepetition())})
test('error táctico y comentario contextual',()=>{const g=play('f3'),before={best:'e2e4',pv:{1:{type:'cp',value:40,line:['e2e4']}}},after={pv:{1:{type:'cp',value:180}}};const r=analyze(g.history({verbose:true})[0],before,after,20,g);assert.equal(r.category,'BLUNDER');assert.match(project(r,'Filósofo',0),/f3/);assert.equal(project(r,'Silencioso',1),'')})
