// Serializes optional background work and lets gameplay preempt it.
export class ResourceScheduler {
  #generation = 0
  #background = null
  newGame() { this.#generation++; this.#background?.abort(); this.#background = null; return this.#generation }
  current(token) { return token === this.#generation }
  async background(task) {
    this.#background?.abort()
    const controller = new AbortController(); this.#background = controller
    try { return await task(controller.signal, this.#generation) }
    finally { if (this.#background === controller) this.#background = null }
  }
  cancelBackground() { this.#background?.abort(); this.#background = null }
}
