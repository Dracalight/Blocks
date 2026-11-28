// Runtime contract. No model is bundled or silently downloaded. A backend must
// implement actual inference before it can report ready/accelerated.
export class NeuralRuntime {
  constructor() { this.backend = 'procedural'; this.model = null; this.ready = false; this.controller = null }
  async detect() { return { webgpu: !!navigator.gpu, wasm: typeof WebAssembly === 'object' } }
  async loadModel() { throw new Error('No local model runtime is installed. Procedural projections remain available offline.') }
  async generate() { throw new Error('No local model runtime is installed.') }
  cancel() { this.controller?.abort(); this.controller = null }
  async unload() { this.cancel(); this.model = null; this.ready = false; this.backend = 'procedural' }
  metrics() { return { ready: this.ready, backend: this.backend, model: this.model, measured: false } }
}
