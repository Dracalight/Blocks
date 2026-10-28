# NIGHTMARE: evidencia y QA pendiente

Estado: checkpoint de desarrollo, **no release candidate**. La dirección de Industrial Brutalist / Terminal Utility sigue el contrato `design-taste-frontend` facilitado por el OWNER (la skill original no estaba instalada). No se ha hecho una partida renderizada ni probado en iPad.

## Animación implementada

- Entrada de Nightmare y Glitch y transiciones de Trials: desplazamiento y escala con reloj lógico, pausables.
- Glitch: cinco avisos, disparo y movimiento de amenazas, núcleo con estado de daño y pantallas de resultado. La geometría relevante para el peligro no se desactiva con M.
- Confirmaciones de eventos: sellos vectoriales durante 0,8 s en el margen izquierdo para advertencia, impacto de garbage, bloqueo/desbloqueo de Hold, reducción de deuda, cadena, daño de blindaje y presión diferida. Se desplazan y cambian de escala; M los suprime. No se dibujan sobre el tablero ni la firma. Las alertas persistentes permanecen con M.
- La línea completada usa el efecto existente. El blindaje muestra disfraces intacto y agrietado.

Pendientes del catálogo: efectos diferenciados de aparición y destrucción de blindaje; inicio y final animados para todos los objetivos; entrada/salida de arena, retorno, victorias y Game Over con coreografía propia; transición de selección; verificación real del movimiento, la sincronización, los textos y la legibilidad. Los sellos de confirmación no cubren todos los efectos pedidos.

## Balance y simulación

No se han cambiado los parámetros de dificultad en esta pasada: modificar balance sin partidas observadas carece de evidencia. Endless sigue requiriendo al menos seis fijaciones y 20 s para programar eventos; el umbral de presión difiere amenazas nuevas. Hold Jam dura siete fijaciones. Los avisos de Double Garbage, blindaje y deuda se documentan en `NIGHTMARE_PROGRESS.md`.

`python tools/nightmare/simulate_pressure.py` ejecuta el procedimiento Scratch de eventos para seis semillas, 100 fijaciones por semilla y limpiezas sintéticas. En cada semilla programó ocho amenazas: 2 Double, 3 avisos de Jam, 2 deudas y 1 aviso de blindaje; en una quedó deuda activa al terminar el horizonte de simulación. Los contadores se mantuvieron en sus límites y el tablero en 200 celdas. El fixture vacía el tablero en cada paso: **no mide supervivencia, top-out, frecuencia real de eventos, duración de oleadas ni habilidad humana**. La simulación de rutas de Glitch es también un muestreo parcial. No se demuestra equilibrio ni ausencia de estados problemáticos.

## QA automático y límites

- Construcción doble reproducible y validación estructural Scratch; pruebas de regresión del intérprete y planificador oficial sin renderer.
- Firma comprobada estructuralmente en los tres fondos. El pulgar vectorial fue inspeccionado en una imagen estática. La fuente japonesa no está instalada aquí, por lo que el texto no pudo inspeccionarse visualmente.
- El editor oficial informó que el navegador de pruebas no soporta WebGL. La inspección de SVG no demuestra renderizado ni composición durante una partida.
- WAV presentes, íntegros y con duración de 0,035 a 0,66 s; no se ha escuchado el audio ni medido volumen, latencia o persistencia en el dispositivo.
- No hay medición gráfica ni ejecución en iPad; no se garantiza rendimiento o interacción física.

## Comprobación del OWNER en iPad

1. Abrir el SB3 de la rama en Scratch, en horizontal, conectar el teclado físico y pulsar la bandera.
2. En Normal, Hard y Chaos comprobar firma japonesa, pulgar, giro, Hold, caída, pausa, reinicio y Speed Burst de Chaos.
3. Seleccionar 4; cambiar Endless/Trials pulsando 4 en el menú. Verificar firma, marcadores y avisos sin superposiciones con puntuaciones largas y eventos simultáneos.
4. Jugar Endless hasta observar un evento y su aviso, confirmación y resolución; comprobar respuesta y fluidez.
5. En Trials observar objetivos, progresión, transiciones y Nightmare Core. Comprobar que perder Glitch no concede la victoria.
6. En Glitch probar flechas, avisos de ataques, pausa, reinicio y retorno; comprobar que el tablero no avanza durante el desafío.
7. Pulsar M y confirmar que bajan las animaciones secundarias y permanecen visibles las amenazas. Escuchar efectos y comprobar que no se quedan sonando.
8. Registrar cualquier fallo con modo, estado, pasos y, si es posible, foto o grabación.
