// Exercise official VM's size clamp against a minimal renderer stub.
// This does NOT render the project or validate actual SVG pixels.
const assert = require('node:assert/strict');
const path = require('node:path');
const RenderedTarget = require(path.resolve(path.dirname(require.resolve('scratch-vm')), '../../src/sprites/rendered-target')); 
let applied;
const sprite={isStage:false,visible:false,drawableID:1,
  renderer:{getCurrentSkinSize:()=>[72,72],updateDrawableDirectionScale:(id,direction,scale)=>{applied=scale}},
  runtime:{constructor:{STAGE_WIDTH:480,STAGE_HEIGHT:360},requestTargetsUpdate:()=>{}},
  _getRenderedDirectionAndScale(){return {direction:90,scale:[this.size,this.size]}}};
RenderedTarget.prototype.setSize.call(sprite,0.1);
assert.ok(Math.abs(sprite.size-100*5/72)<1e-10);
assert.ok(Math.abs(30*sprite.size/100-25/12)<1e-10);
assert.ok(applied);
console.log('PASS: official Scratch VM clamps 72px ring sprite to 5px (renderer stub; no pixel rendering)');
