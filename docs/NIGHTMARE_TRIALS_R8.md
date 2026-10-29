# NIGHTMARE Trials: recorridos persistentes R8

`python tools/nightmare/simulate_trials.py --limit 300` ejecuta el proyecto generado con el intérprete AST de bloques Scratch. Tres semillas se reproducen con cada política: básica y heurística. Se ejecutan selección inicial, arranque, rotaciones, desplazamientos, Hold, hard drop, limpieza, eventos, transiciones, Glitch y top-out mediante procedimientos del proyecto. El tablero se conserva y la simulación no asigna líneas ni contadores de progreso. Las métricas están en `evidence/trials-r8.jsonl`.

| Política | Semilla | Fijaciones | Líneas | Oleadas completadas | Resultado |
| --- | ---: | ---: | ---: | --- | --- |
| Básica | 11 | 18 | 0 | Ninguna | Game Over |
| Básica | 23 | 15 | 0 | Ninguna | Game Over |
| Básica | 37 | 15 | 0 | Ninguna | Game Over |
| Heurística | 11 | 132 | 45 | 1–4 | Game Over en Core |
| Heurística | 23 | 166 | 71 | 1–5 | Victoria |
| Heurística | 37 | 165 | 64 | 1–5 | Victoria |

No se observó parada sin progreso. Las ejecuciones victoriosas sobrevivieron Glitch mediante entradas activas; los resultados completos incluyen alturas, huecos, filas de garbage, activaciones y reloj. La política heurística solo explora giros sin kick y ejecuta acciones idealizadas; cada fijación deja avanzar 0,1 s de juego. No representa latencia ni ritmo humano. La entrada activa a Glitch es idealizada cada 50 ms y no prueba repetición real del teclado. El intérprete AST no es el planificador oficial ni un renderizador. Las pruebas adversariales son fixtures, no una tercera política de partidas completas.

`python -m unittest discover -s tools/nightmare -p 'test_*.py' -v` incluye tres fixtures adversariales añadidos: fallo de Glitch en Core con penalización y reintento exitoso sin duplicar recompensa; Double Garbage con top-out antes de la segunda fila; dos filas totalmente blindadas agrietadas y resueltas sin hueco. Se complementan con los escenarios de presión, pausas, top-out, cadenas, T-spin y cinco colisiones de `tools/validate_sb3.py`. Los fixtures asignan estados para aislar casos y no cuentan como recorridos completos.

**Pendiente:** más semillas, política adversarial completa, pruebas con ritmo y teclado reales, QA visual y balance humano. No se modificaron parámetros de dificultad en R8.
