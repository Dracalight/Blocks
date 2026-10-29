# NIGHTMARE R9 — NO READY FOR OWNER QA

Continuación desde `a533aff89a91ecac0dfd0f5fe68435cd3e22fffa`. PR #2 Draft; no fusionar. **RUNTIME_VISUAL_QA_BLOCKED**: el editor oficial en el navegador disponible mostró `Your Browser Does Not Support WebGL`; el ejecutor no tiene Chromium, Firefox ni Xvfb. Hay bibliotecas EGL, pero no un navegador o instalación de renderer ejecutable. No se comprobó audio, controles humanos, iPad ni imágenes del juego. La VM oficial usada abajo no incluye renderer/audio.

## Cambios y hallazgos

- Los cuatro ataques rectangulares usan intersección del rombo de radio 6 y sus formas rectangulares; el anillo ahora usa distancia euclídea mínima al rombo y radio exterior 31/30 del radio dibujado, incluyendo el trazo del círculo. El disfraz del anillo se selecciona antes de escalar y su radio mínimo se fija a 25/12 px, consistente con el mínimo de 5 px que aplica la VM a un disfraz de 72 px. La prueba `test_scratch_size.cjs` comprueba esa regla con la clase oficial y un renderer simulado; no produce píxeles. Los límites exactos usan desigualdad estricta. El antialiasing y trazo del núcleo no están modelados; el aspecto en Scratch y cualquier limitación del escalado de disfraces requieren renderer.
- El acierto resta 1 HP con invulnerabilidad 0,45 s y sonido. En una traza sin entradas del intérprete los valores fueron 3→2→1→0 y tres llamadas de sonido; el resultado de pérdida indica HP 0 y dos filas en dos fijaciones. El resultado de victoria registra +100 y sonido al entrar en resultado y solo una vez; Core solo se marca completo en victoria. El modal describe el bonus; la actualización gráfica del SCORE se ve al volver al tablero. No se ha reproducido la observación del OWNER visualmente y no se afirma causa raíz completa.
- La presión de ENDLESS empieza tras 12 s y cinco fijaciones elegibles (antes 20 s y seis); el primer Burst empieza tras 12 s (antes 15). La velocidad base de NIGHTMARE se reduce de 0,23 a 0,18 s; CHAOS permanece en 0,23 s. Se probó también 0,23 bajo el mismo calendario y las mismas semillas. Son parámetros candidatos; la comparación inferior no acredita que NIGHTMARE sea más difícil para humanos. CHAOS no fue modificado.
- Se conservan dos filas tras el fallo de Glitch. La evidencia comparativa no justifica con confianza tres ni permite evaluar justicia humana. Son no cancelables, dos fijaciones de aviso; el riesgo sigue abierto.
- Se incorporó build QA independiente y una [guía concreta](NIGHTMARE_R9_QUICK_QA.md); 5 Glitch, 6 Triple, 7 Burst solo en la build QA. La prueba de aislamiento inspecciona el proyecto normal y la build QA; el proyecto normal no incorpora esos atajos.

## Matriz de evidencia

| Requisito | Resultado | Alcance y límites |
|---|---|---|
| Geometría de los cinco ataques | PARCIAL | Cuadrícula de rectángulos y anillo contra oráculos independientes sobre bloques generados, CHARGE, esquinas y ejemplos de zonas seguras; sin comparación con píxeles ni revisión humana. |
| Daño, resultado, penalización y recompensa | PARCIAL | Intérprete: 3→2→1→0, tres sonidos solicitados, dos filas exactamente una vez, victoria +100 inmediata una vez, pausa/reintento; no se escucha ni observa en renderer. |
| Triple | PARCIAL | 0–3 filas, cancelación parcial y total acumulada, top-out, pausa y calendario observado en comparación ENDLESS y simulación Trials; no se han agotado todas las combinaciones adversariales ni revisado avisos en pantalla. |
| Burst | PARCIAL | VM oficial comprueba aceleración, pausa y recuperación con fixture; comparación avanza reloj y observa eventos naturales. El intérprete comprueba reloj congelado en Glitch y pausa; no hay medición visual de caída ni prueba exhaustiva de todas las interacciones. |
| Trials y Core | PARCIAL | Simulación persistente completa desde oleada 1: semillas 23 y 37 terminan Core; 11 llega a Core y pierde. Entradas idealizadas, no ejecución humana; fixtures cubren fallo/reintento Core y tablero conservado. Véase `docs/evidence/trials-r9.jsonl`. |
| Balance | NO DEMOSTRADO | Comparación emparejada de seis semillas y dos políticas: mayor presión y menos supervivencia básica, pero mayor tiempo medio de la política heurística. No puede declararse superior; consultar cifras abajo. |
| QA rápido | PASS parcial | Build y teclas verificadas por VM oficial y aislamiento comprobado; aún no se han probado en renderer. |
| Estructura, lógica y build | PASS | `validate_sb3.py`, pruebas Python, y doble build idéntico. Las pruebas no prueban apariencia ni audio. |
| Scratch renderer, controles, sonido, iPad | RUNTIME_VISUAL_QA_BLOCKED | Editor oficial informó falta de WebGL; no hay captura o vídeo de gameplay. |

## Comparación reproducible

`python tools/nightmare/compare_modes.py --limit 100 --cadence 1.0` ejecuta los bloques Scratch con tablero persistente, mismas semillas 11/23/37/41/53/67, tablero inicial vacío, dos políticas y 1 s por decisión. Cada bloque aleatorio tiene su propio generador con semilla reproducible: los eventos no alteran la secuencia de bolsas; CHAOS puede sustituir piezas como parte de su mecánica. Es una adaptación del generador aleatorio, no ejecución del planificador oficial. Se cuentan fijaciones automáticas y manuales por separado. El bot hard-drop no refleja reacción ni percepción humana; el tiempo Glitch queda excluido del reloj del tablero y el límite de 100 caídas manuales censura partidas. Datos por partida en `docs/evidence/balance-r9-final.jsonl`.

| Política | Modo | Fijaciones medias | Segundos medios | Líneas medias | Filas basura medias | Segundos Burst medios | Top-out / 6 |
|---|---|---:|---:|---:|---:|---:|---:|
| Básica | CHAOS | 21,3 | 20,1 | 0 | 0 | 0 | 6 |
| Básica | NIGHTMARE | 17,8 | 15,7 | 0 | 1,2 | 3,2 | 6 |
| Heurística | CHAOS | 78,7 | 77,9 | 26,0 | 2,8 | 16,2 | 3 |
| Heurística | NIGHTMARE | 83,2 | 81,7 | 27,2 | 6,2 | 19,8 | 5 |

Los datos anteriores `balance-r9-before.jsonl` y `balance-r9-after.jsonl` son exploratorios con un generador aleatorio compartido y cuentan caídas manuales bajo el nombre `locks`; no compararlos directamente con la tabla corregida. La prueba final da indicios de más presión, pero los resultados de supervivencia son mixtos y no establecen que NIGHTMARE sea más difícil para humanos. Se requieren más políticas, semillas y pruebas humanas.

## Verificación y archivos

- Doble build release SHA-256 `198f2d17d9c7d8eef8fdca2fa3d87601cf80ff4dd075e323ef58aa221f8df7b9`; build QA SHA-256 `d01186f27237f6b4bdbc847f2296d0a38d0e506c5a33402a368139c4b40b09c1`.
- `python tools/validate_sb3.py`: PASS; `python -m unittest discover -s tools/nightmare -p 'test_*.py'`: 25 PASS; `python tools/nightmare/simulate_pressure.py`: PASS en fixture de tablero vacío.
- `npm test`: PASS; `node tools/nightmare/test_scratch_size.cjs`: PASS con renderer simulado. `python tools/test_sb3.py`: PASS tras el ajuste del tamaño mínimo. `node tools/nightmare/test_r9_runtime.cjs`: PASS y `node tools/nightmare/test_qa_fixture.cjs`: PASS, ambos VM oficial sin renderer/audio. Ver instrucciones de reproducción y límites arriba.
- Pendiente: pruebas de renderer y gameplay real, causa original observada, revisión visual de anillo/trazos, cobertura exhaustiva de combinaciones de amenazas y balance suficiente. Este documento no declara DONE ni READY FOR OWNER QA.

### Ensayo aislado de velocidad

Con el mismo generador por bloque y calendario, se comparó un build idéntico salvo velocidad base NIGHTMARE 0,23 s frente al candidato 0,18 s (`balance-r9-speed023.jsonl` y `balance-r9-final.jsonl`). Para 0,23, la política básica promedió 17,3 fijaciones y 16,1 s; para 0,18, 17,8 y 15,7 s. La heurística dio 83,2 fijaciones y 81,7 s en ambos casos, con 5 top-outs de 6. CHAOS produjo los mismos resultados en ambos ensayos. La reducción se conserva como candidato de presión inicial, **no** como prueba de mejora de dificultad; la diferencia observada es pequeña/mixta y aún debe evaluarse visual y humanamente. No se subió la penalización de Glitch basándose en estos resultados.
