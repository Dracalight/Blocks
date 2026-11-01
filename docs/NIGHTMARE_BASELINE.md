# Nightmare: baseline y decisiones iniciales

Base: `cb3bf7f53a323c948dbf458ee577a35e32e008af` (main). Rama: `feat/nightmare-mode-v1`.

Lectura visual: arcade competitivo para jugadores con teclado, con lenguaje industrial brutalista, alarmas legibles y movimiento funcional en un escenario Scratch de 480 × 360. DESIGN_VARIANCE 8, MOTION_INTENSITY 8, VISUAL_DENSITY 6. El OWNER proporcionó el contrato design-taste-frontend en la conversación; no se localizó la skill original instalada. Aplicar sus principios pertinentes a Pen y SVG, sin introducir una interfaz web. Una referencia relacionada existe en el entorno, pero no se presenta como la skill original.

## Verificación inicial

- `python tools/build_sb3.py`, `python tools/validate_sb3.py` y `python tools/test_sb3.py`: pasan en la baseline. Dos reconstrucciones consecutivas produjeron SHA-256 `834f58dadb7008d54fa868e771ae0000ad0830a4490e35b55e6fd920c0c7772e`. El SB3 de main tiene SHA-256 `026a50c4c56798cd26a2c9a382068beb3583bcb671349a7e144e7f57afcdd70d`; sus 43 entradas tienen contenido idéntico, con diferencias en metadatos ZIP. No se modificó el SB3 en este commit.
- `npm ci --ignore-scripts` y `npm test`: pasan. Medianas observadas para NORMAL/HARD/CHAOS: 0.662/0.307/0.239 s por fila; 20.1 s por modo. El test usa scratch-vm sin renderer ni audio.
- Regresión nueva: 12 giros de T y fijación de exactamente cuatro celdas; una T rotada completa dos filas legítimas. No es una prueba de T-spin ni de teclado real.

## Riesgos antes de implementar

- El tablero actual guarda valores por celda y la limpieza compacta filas completas. La propuesta de dejar una fila blindada completa tras dañarla puede resultar irresoluble: requiere prototipo de jugabilidad y pruebas de compactación simultánea antes de integrarla. Una representación de resistencia separada o valores de celda adicionales afectaría colisiones, render y limpieza; preservar el camino original para modos 1–3.
- El reloj lógico de juego se detiene en pausa, pero la entrada repetida usa el temporizador de Scratch. Los estados de Glitch requieren congelar el tablero y sus deadlines, además de reinicializar los latches al retornar, sin introducir otro hilo de física.
- El ensayo del planificador no valida imágenes, sonido, latencia visual ni teclado físico. Faltan la prueba en el editor oficial, partidas de larga duración y aceptación en iPad.

La especificación v0.1 es una hipótesis de balance. Ningún sistema Nightmare está implementado ni aprobado para integrar a main en esta fase.
