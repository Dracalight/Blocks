# Historial de Versiones (CHANGELOG) — NEXUS BLOCKS: ENDLESS

## [v2.0.0] — 2026-10-19 (Segunda Etapa: Modos Especiales, Audio y Pulido Táctil)
### Añadido
* **Modo `CHAOS MODE`**: Sistema de eventos temporales previsibles cada 15 segundos con aviso previo de 3 segundos (`AVISO: EVENTO EN 3s`) en el monitor del escenario y cambio automático al fondo `Fondo_Caos`:
  * `TURBO x2 PUNTOS`: incrementa ligeramente la velocidad de caída y duplica toda la puntuación obtenida.
  * `GRAVEDAD LUNAR`: reduce la velocidad de caída un 35% para facilitar recuperaciones en situaciones críticas.
  * `BONO LINEA +500`: otorga `+500` puntos adicionales al completar cualquier línea durante el evento.
* **Modo `SPRINT 40L`**: Cronómetro en tiempo real (`Tiempo_Sprint`) y detección automática de victoria (`Estado_Juego = "VICTORIA"`) con cartel y fanfarria al completar 40 líneas.
* **Objeto `Efecto_Linea`**: Animaciones visuales no bloqueantes (`¡LÍNEA! +100`, `¡DOBLE! +300`, `¡TRIPLE! +500`, `¡NEXUS x4! +800`) al completar de 1 a 4 líneas simultáneamente.
* **Síntesis de 8 efectos de sonido WAV originales**: `Sonido_Mover`, `Sonido_Rotar`, `Sonido_Caida`, `Sonido_Linea`, `Sonido_Hold`, `Sonido_Caos`, `Sonido_GameOver` y `Sonido_Victoria`.

### Verificado
* Suite de pruebas `tools/validate_sb3.py` ampliada con intérprete de bloques `Scratch3VMInterpreter` verificando los 1052 bloques y las 11 pruebas obligatorias.

## [v1.0.0] — 2026-10-19 (Primera Etapa: Motor Base, Dificultades y Controles)
### Añadido
* Motor principal `Motor_Juego` compatible con Scratch 3 usando renderizado por extensión oficial `pen` (`Renderizar_Todo` sin refresco de pantalla) libre del límite de 300 clones.
* Tablero de 10 columnas × 20 filas (`Tablero`), 7 piezas con colores diferenciados y tablas geométricas `Offset_X` / `Offset_Y` (112 entradas).
* Generador aleatorio equilibrado mediante bolsa de 7 piezas (`Bolsa_7`).
* Sistema de rotación con 6 pruebas *Wall Kick* (`Kick_X`, `Kick_Y`), pieza fantasma (`Fila_Fantasma`), reserva `Hold` (`Guardar_Hold`) con bloqueo por turno y eliminación simultánea de 1 a 4 líneas.
* Cuatro dificultades seleccionables (`Fácil`, `Normal`, `Difícil`, `Pesadilla`) con límite técnico de seguridad (`Velocidad_Caida >= 0.06 s`) y modos `ENDLESS CLASSIC` y `RELAX`.
* Interfaz completa de 10 botones táctiles para iPad horizontal y controles de teclado.
