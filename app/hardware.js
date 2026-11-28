// NEXUS Hardware Adaptation Engine. All hardware values are capability probes,
// never promises about available memory or physical GPU utilization.
const timeout = (promise, ms) => Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(Error('probe timeout')), ms))])

export async function inspectHardware() {
  const result = {
    webgpu: { available: !!navigator.gpu, adapter: false, device: false, backend: 'unavailable', features: [], limits: {} },
    wasm: { available: typeof WebAssembly === 'object', simd: false },
    sharedArrayBuffer: typeof SharedArrayBuffer === 'function', isolated: !!globalThis.crossOriginIsolated,
    logicalCores: navigator.hardwareConcurrency || null, storage: null, tier: 0, profile: 'Universal',
    notes: []
  }
  try { result.wasm.simd = WebAssembly.validate(new Uint8Array([0,97,115,109,1,0,0,0,1,5,1,96,0,1,123,3,2,1,0,10,10,1,8,0,65,0,253,15,26,11])) } catch {}
  try {
    if (navigator.storage?.estimate) {
      const { quota, usage } = await navigator.storage.estimate()
      if (Number.isFinite(quota)) result.storage = { quota, usage: usage || 0, available: Math.max(0, quota - (usage || 0)) }
    }
  } catch { result.notes.push('Storage estimate unavailable') }
  if (navigator.gpu) try {
    const adapter = await timeout(navigator.gpu.requestAdapter({ powerPreference: 'high-performance' }), 2500)
    if (adapter) {
      result.webgpu.adapter = true
      result.webgpu.features = [...adapter.features]
      result.webgpu.limits = { maxBufferSize: adapter.limits.maxBufferSize, maxStorageBufferBindingSize: adapter.limits.maxStorageBufferBindingSize }
      const device = await timeout(adapter.requestDevice(), 2500)
      result.webgpu.device = !!device
      result.webgpu.backend = device ? 'WebGPU device ready (physical/software adapter not identifiable reliably)' : 'adapter only'
      device?.destroy()
    }
  } catch (e) { result.notes.push(`WebGPU probe failed: ${e.message}`) }
  // Conservative selection; never infer RAM from device names or core counts.
  if (result.webgpu.device && result.webgpu.features.includes('shader-f16') && result.logicalCores >= 8) { result.tier = 3; result.profile = 'Desktop Neural' }
  else if (result.webgpu.device) { result.tier = 1; result.profile = 'Mobile Neural' }
  else if (result.wasm.simd) { result.tier = 0; result.profile = 'Universal (WASM SIMD)' }
  return result
}

export const hardwareStatus = () => inspectHardware()
