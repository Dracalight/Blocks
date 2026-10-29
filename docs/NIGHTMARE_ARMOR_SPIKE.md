# Blindaje: prototipo anterior y regla integrada

## Regla integrada en Scratch

La variante integrada evita el hueco inaccesible sin depender de acceso físico. Una fila completa con al menos una celda intacta (`9`) convierte **todas** sus celdas intactas a dañadas (`10`), permanece completa y no concede línea ni puntos. En la próxima fijación, el procedimiento ordinario revisa todas las filas y elimina cualquier fila completa que ya no tenga celdas intactas. La eliminación concede puntos y progreso de líneas normalmente. La basura mueve filas completas sin mezclar sus celdas; las piezas no pueden ocupar celdas ya llenas. Por ello una fila dañada que siga en el tablero permanece completa y sin celdas `9` hasta la siguiente revisión, y no necesita que el jugador acceda a un hueco. Si ocurre Game Over antes de otra fijación, termina la partida conforme al top-out ordinario.

La revisión procede de abajo hacia arriba: una fila agrietada se conserva y se pasa a la fila superior; las filas ordinarias completas se eliminan y las superiores se compactan. Varias filas blindadas pueden agrietarse en la misma revisión y desaparecer en la siguiente. La entrada programada introduce una sola fila, con nueve celdas intactas y un hueco, tras cuatro fijaciones de aviso; reutiliza el desplazamiento, la colisión de la pieza activa y el top-out del garbage existente. No cambia las reglas de Normal, Hard ni Chaos.

Las pruebas ejecutan el generador y los procedimientos reales del SB3 en el intérprete del repositorio: fila adversarial de diez bloques intactos, daño sin puntuación, siguiente revisión, compactación mixta, T-spin y próxima fijación, advertencia e inserción, colisión, top-out, reinicio y doce tableros aleatorios comparados con una especificación simultánea independiente. El planificador oficial también cubre la entrada avisada de blindaje. Estas comprobaciones no demuestran que cualquier partida sea ganable ni sustituyen pruebas visuales y de balance. Si una revisión elimina más de cuatro filas debido a filas diferidas y nuevas, se conserva la rama de puntuación existente de cuatro o más filas (800 × nivel, más combo).

## Prototipo anterior, no integrado

El modelo original deja una fila completamente ocupada después del primer impacto. Sin una acción que retire una celda, esa fila no puede volver a recibir una pieza y no tiene un segundo disparador de limpieza. El prototipo de `tools/nightmare/armor_spike.py` explora una alternativa **no integrada en Scratch**:

- Una fila completa con blindaje intacto cambia sus celdas blindadas a dañadas, abre la primera celda ordinaria y no concede línea ni puntos.
- Una fila completa sin blindaje intacto se elimina normalmente. Las filas eliminadas se compactan a la vez; las dañadas se conservan.
- Una fila de basura blindada propuesta tiene nueve celdas intactas y un hueco. El prototipo rechaza una fila completa blindada sin ninguna celda ordinaria para abrir.

El comando `python -m unittest discover -s tools/nightmare -p 'test_*.py' -v` comprueba desgaste y segunda limpieza, varias filas y compactación, una configuración de celdas de T-spin double, inserción de basura, top-out y reinicialización del modelo. No ejecuta la física, el giro, la entrada ni el render de Scratch. El helper de top-out conserva el tablero en caso de fallo, mientras que el garbage actual de Scratch desplaza antes de finalizar: esto es una diferencia explícita del prototipo, no una modificación del juego.

Abrir una celda evita la fila completamente sólida retenida, pero **no demuestra que el hueco sea alcanzable desde arriba** en todos los tableros. También falta probar la invariancia de la representación ante todas las operaciones reales, puntuación, visuales y pausas. No integrar este modelo hasta resolver esos puntos y ejecutar las regresiones en el SB3 y partidas reales.
