# Prototipo aislado de blindaje

El modelo original deja una fila completamente ocupada después del primer impacto. Sin una acción que retire una celda, esa fila no puede volver a recibir una pieza y no tiene un segundo disparador de limpieza. El prototipo de `tools/nightmare/armor_spike.py` explora una alternativa **no integrada en Scratch**:

- Una fila completa con blindaje intacto cambia sus celdas blindadas a dañadas, abre la primera celda ordinaria y no concede línea ni puntos.
- Una fila completa sin blindaje intacto se elimina normalmente. Las filas eliminadas se compactan a la vez; las dañadas se conservan.
- Una fila de basura blindada propuesta tiene nueve celdas intactas y un hueco. El prototipo rechaza una fila completa blindada sin ninguna celda ordinaria para abrir.

El comando `python -m unittest discover -s tools/nightmare -p 'test_*.py' -v` comprueba desgaste y segunda limpieza, varias filas y compactación, una configuración de celdas de T-spin double, inserción de basura, top-out y reinicialización del modelo. No ejecuta la física, el giro, la entrada ni el render de Scratch. El helper de top-out conserva el tablero en caso de fallo, mientras que el garbage actual de Scratch desplaza antes de finalizar: esto es una diferencia explícita del prototipo, no una modificación del juego.

Abrir una celda evita la fila completamente sólida retenida, pero **no demuestra que el hueco sea alcanzable desde arriba** en todos los tableros. También falta probar la invariancia de la representación ante todas las operaciones reales, puntuación, visuales y pausas. No integrar este modelo hasta resolver esos puntos y ejecutar las regresiones en el SB3 y partidas reales.
