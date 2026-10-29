# NIGHTMARE R9 — avance parcial, NO READY FOR OWNER QA

Base: `f2fd2d64cb7904c950aa7c83f2ebf1b653eb0015`. PR #2 sigue Draft. Esta entrega no cierra R9 y no acredita que NIGHTMARE sea más difícil que CHAOS en partidas humanas.

## Hallazgos y cambios

- Los cinco ataques comprobaban el **centro** del núcleo, aunque su dibujo se extiende hasta 6 px; un contacto aparente del borde podía no contar. Se amplían las zonas de colisión; esto es una aproximación conservadora, no una intersección exacta con el rombo: especialmente cerca de esquinas de blancos y fragmentos puede dar falsos positivos. No se ha reproducido la observación del OWNER con renderer, por lo que no se atribuye la incidencia completa a esta causa.
- El diálogo de resultado se ocultaba tras unos 0,3 s. Ahora permanece durante el estado de resultado (1,4 s); el fallo mantiene dos filas con aviso de dos fijaciones. Se conservan dos filas provisionalmente: no hay pruebas humanas que justifiquen tres.
- Triple: aviso de cinco fijaciones; cada dos líneas cancela una fila; máximo tres. Se incorpora en ENDLESS (secuencia periódica tras 45 s) y en el primer hito de CORE. Las filas usan la rutina de basura existente, deteniéndose si ocurre top-out.
- Burst: primer inicio a los 15 s de tiempo de juego, aviso durante los 2 s anteriores, duración 5 s y siguientes inicios cada 20 s. Usa la mitad del intervalo de caída, con piso 0,07 s. El reloj del tablero se congela durante pausa, Glitch y transiciones. `Delta` ya no se reutiliza como factor de velocidad.
- Estos parámetros son provisionales: no hay comparación controlada de dificultad ni validación de equidad de combinaciones.

## Comprobaciones

| Escenario | Estado | Alcance |
|---|---|---|
| ZIP, activos y 3202 bloques; regresiones Python | PASS | `python tools/validate_sb3.py`, intérprete y estructura. |
| 10 pruebas adicionales Python | PASS | `python -m unittest discover -s tools/nightmare -p 'test_*.py'`; `test_glitch_routes.py` aún describe la geometría anterior y no valida los límites nuevos. |
| Triple sin cancelación y 1/2/3 filas canceladas | PASS | Intérprete; conteo de celdas y huecos; cancelación completa usa fixture sintético. |
| Triple, Burst y daño Glitch | PASS | `node tools/nightmare/test_r9_runtime.cjs`: planificador oficial y eventos de teclado con fixtures de estado; **sin renderer ni audio**. |
| Regresiones NORMAL/HARD/CHAOS y controles | PASS | `npm test`, planificador oficial sin renderer, sobre el build anterior a la extensión del resultado de 0,65 a 1,4 s. |
| Build reproducible | PASS | Dos builds consecutivos del build final: SHA-256 idéntico. |
| Trials tablero persistente | PARCIAL | `simulate_trials.py --limit 50`: semillas 11/23/37; política básica pierde en oleada 1, heurística alcanza oleada 3 en 50 fijaciones. No llega a Triple/Core ni prueba balance humano. |
| Geometría exacta, bordes seguros, cinco ataques | NO CERRADO | Zonas ampliadas aproximadas; falta prueba gráfica y ajuste de esquinas/rutas. |
| Penalización material tras fallo, top-out Triple, cadenas, interacciones y reintentos | PARCIAL | Cobertura previa de Double y fixtures del intérprete; no hay prueba integral R9 con renderer. |
| Chaos vs Nightmare: mismas semillas, políticas y métricas | NOT RUN | No se demuestra la jerarquía de dificultad. |
| Ejecución interactiva Scratch 3 con renderer, audio y iPad | RUNTIME_VISUAL_QA_BLOCKED | Este entorno no tiene navegador gráfico instalado; no se produjo screenshot/video ni prueba humana. |

## Prueba manual provisional

1. Abrir el `.sb3` de esta rama en Scratch 3, seleccionar 4 y ENDLESS, iniciar con Enter. Jugar hasta Glitch; moverse deliberadamente a los ataques activos y comprobar HP, sonido, resultado y aplicación posterior de basura. Repetir sobreviviendo y comprobar +100 una sola vez.
2. Observar `BURST SOON` y `SPEED BURST`, pausar durante la ráfaga y comprobar que se reanuda y termina. En ENDLESS, seguir hasta `TRIPLE GARBAGE`; observar cuenta de fijaciones, filas y cancelación mediante líneas.
3. En TRIALS, avanzar hasta CORE y repetir. Registrar vídeo, sistema, dispositivo y cualquier impacto falso o invisible.

No existe todavía un harness gráfico desmontable para acelerar estos casos: la guía puede requerir una espera larga. No marcar DONE ni READY FOR OWNER QA hasta cerrar las verificaciones de R9 y la revisión visual/humana.

## Continuación: límites rectangulares (29 octubre)

Estado: **NO READY FOR OWNER QA / RUNTIME_VISUAL_QA_BLOCKED**. Se comprobó el PR #2 Draft en `e2e2250da01551469803207f1860e7f1137bd5fc` antes de este cambio.

En haz, objetivo, muro y fragmentos, la colisión usa intersección entre el rombo interior de radio 6 del núcleo y los rectángulos visibles de cada ataque. La comprobación de suma de distancias elimina las esquinas cuadradas de la ampliación anterior. El muro considera sus dos segmentos y el hueco; los fragmentos usan 14 px de semiextensión. Se emplean desigualdades estrictas, por lo que un contacto matemático exacto en el borde no cuenta. El borde del trazo del núcleo y el antialiasing no están modelados; el anillo conserva su aproximación circular anterior y no se ha validado gráficamente. Esto no demuestra la causa completa del problema observado por el OWNER ni su resolución visual.

- `test_r9_geometry.py`: seis pruebas de los bloques generados que comprueban CHARGE, límites y esquinas, incluido un punto exterior seguro del anillo. No constituyen una prueba exhaustiva de la circunferencia ni del renderer.
- Se actualizó `test_glitch_routes.py`, antes basado en la geometría obsoleta. Sus rutas son una simulación idealizada de movimientos por cuadrícula y no demuestran que un jugador humano pueda evitar todos los ataques.
- `validate_sb3.py`: PASS, 3276 bloques y pruebas lógicas; 16 pruebas Python: PASS. Build duplicado SHA-256 `894d8a9ab1e1d4428f88eb8710eb71a0da294a07ce4691e2ef56aed642a6611f`.
- `test_r9_runtime.cjs`: PASS para tres filas, Burst, pausa, daño/invulnerabilidad y programación de fallo; VM oficial sin renderer/audio, con estado preparado.
- Trials con semillas 11/23/37 y límite de 50 fijaciones: política básica termina en GAMEOVER en oleada 1 (18/15/15 fijaciones); heurística sigue jugando en oleada 3 (17/19/15 líneas). No alcanza Core ni valida balance humano.
- Se intentó abrir el editor oficial `https://scratch.mit.edu/projects/editor/` en Chrome del entorno: el propio editor mostró **Your Browser Does Not Support WebGL**. En el ejecutor no se encontró Chromium, Firefox ni Xvfb instalados. Sin renderer no se comprobaron entrada jugable, audio, capturas ni iPad.

Pendiente sin cambios: reproducción visual del bug original, anillo y límites completos, castigo y victoria visibles en partida, colisiones entre ticks, interacciones completas de Triple/Burst, Trials y Core integrales, harness rápido, comparación controlada CHAOS/NIGHTMARE y selección fundamentada de dos o tres filas. La penalización continúa provisional en dos; no se ha demostrado NIGHTMARE > CHAOS. Conservar guía manual provisional anterior y PR Draft; no presentar esta continuación como cierre R9.
- `npm test`: PASS, regresiones del planificador oficial y controles simulados, sin renderer ni audio.
