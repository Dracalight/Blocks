# Guía de Controles — NEXUS BLOCKS: ENDLESS

El juego admite simultáneamente **controles táctiles en pantalla** (diseñados para sujetar el iPad en orientación horizontal con ambos pulgares) y **controles de teclado** (para ordenadores o iPad con teclado acoplado), sin necesidad de cambiar ningún ajuste.

## 1. Controles Táctiles en Pantalla (iPad Horizontal)

Los botones están distribuidos en los márgenes izquierdo, derecho e inferior del escenario (`480x360`) para no tapar nunca el tablero central de `10x20` celdas:

| Botón Táctil | Ubicación en Pantalla | Acción | Comportamiento al Mantener Pulsado |
| :--- | :--- | :--- | :--- |
| **◀ IZQ (MOVER)** | Izquierda central (`x: -198, y: -42`) | Desplaza la pieza activa 1 columna a la izquierda. | **Movimiento continuo (DAS/ARR)**: mueve 1 celda al tocar, espera `0.16 s` y repite cada `0.055 s` mientras mantengas el dedo sobre el botón. |
| **DER ▶ (MOVER)** | Izquierda central (`x: -122, y: -42`) | Desplaza la pieza activa 1 columna a la derecha. | **Movimiento continuo (DAS/ARR)**: mueve 1 celda al tocar, espera `0.16 s` y repite cada `0.055 s` mientras mantengas el dedo sobre el botón. |
| **▼ BAJAR SUAVE** | Izquierda inferior (`x: -160, y: -108`) | Desciende la pieza 1 fila rápidamente y suma `+1` punto por celda. | **Descenso continuo**: baja de forma continua cada `0.055 s` mientras mantengas pulsado el botón. |
| **⇄ HOLD (GUARDAR)** | Izquierda superior (`x: -160, y: 26`) | Guarda la pieza actual en la reserva `HOLD` o la intercambia por la guardada (máximo 1 vez por turno). | **Pulsación única con bloqueo anti-rebote**: espera a levantar el dedo para evitar dobles pulsaciones accidentales. |
| **⟳ ROTAR PIEZA** | Derecha central (`x: 160, y: -42`) | Gira la pieza `90°` en sentido horario aplicando corrección *Wall Kick* si está junto a una pared. | **Pulsación única con bloqueo anti-rebote**: gira exactamente `90°` por toque. |
| **⚡ CAÍDA DURA** | Derecha inferior (`x: 160, y: -108`) | Aterriza y fija la pieza instantáneamente sobre la posición de la pieza fantasma (`+2` puntos por fila). | **Pulsación única con bloqueo anti-rebote**: impide que la siguiente pieza caiga por accidente si dejas el dedo apoyado. |
| **⏸ PAUSA** | Derecha superior (`x: 160, y: 26`) | Pausa o reanuda la partida en curso mostrando el panel modal de pausa. | Pulsación única. |
| **MODO DE JUEGO** | Esquina inferior izquierda (`x: -160, y: -156`) | Alterna entre `ENDLESS CLASSIC`, `RELAX`, `CHAOS MODE` y `SPRINT 40L`. | Pulsación única. |
| **DIFICULTAD** | Esquina inferior derecha (`x: 160, y: -156`) | Alterna entre `Fácil`, `Normal`, `Difícil` y `Pesadilla`. | Pulsación única. |
| **↻ NUEVA PARTIDA** | Centro inferior (`x: 0, y: -164`) | Inicia o reinicia inmediatamente una partida limpia desde cero. | Pulsación única. |
| **Panel Central (`Pantalla_Estado`)** | Centro del tablero (`x: 0, y: 6`) | Al tocar el cartel central en Menú, Game Over o Victoria, inicia una nueva partida; en Pausa, reanuda el juego. | Pulsación única. |

## 2. Controles de Teclado

| Tecla | Acción en el Juego | Detalles de Respuesta |
| :--- | :--- | :--- |
| **Flecha Izquierda (`←`)** | Mover a la izquierda | Movimiento inicial inmediato + auto-repetición tras `0.15 s` cada `0.05 s`. |
| **Flecha Derecha (`→`)** | Mover a la derecha | Movimiento inicial inmediato + auto-repetición tras `0.15 s` cada `0.05 s`. |
| **Flecha Abajo (`↓`)** | Caída suave (*Soft Drop*) | Descenso acelerado continuo (`+1` punto por fila avanzada). |
| **Flecha Arriba (`↑`)** | Rotar pieza (`90°`) | Giro horario con sistema *Wall Kick* de 6 posiciones y bloqueo hasta soltar la tecla. |
| **Espacio (`Space`)** | Caída instantánea (*Hard Drop*) / Iniciar | Durante la partida, aterriza la pieza al instante (`+2` puntos por fila); en Menú o Game Over, inicia una nueva partida. |
| **Tecla `C`** | Guardar / Intercambiar pieza (`Hold`) | Guarda la pieza activa en la caja `HOLD` o la intercambia (1 uso permitido por cada pieza fijada). |
| **Tecla `P`** | Pausa / Reanudar | Congela el temporizador de caída y muestra la pantalla de pausa hasta volver a pulsar `P`. |
