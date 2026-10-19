# Informe de Pruebas y Validación — NEXUS BLOCKS: ENDLESS

En cumplimiento de la sección 9 de la especificación, este documento detalla qué pruebas automatizadas se han ejecutado directamente sobre el archivo generado `NEXUS-BLOCKS-ENDLESS.sb3` mediante la suite `tools/validate_sb3.py`, sus resultados verificables y qué comprobaciones visuales quedan sujetas a la ejecución en el navegador del dispositivo final.

## 1. Metodología de Verificación Real (No Solo Sintaxis JSON)

Para no confundir un archivo JSON sintácticamente válido con un videojuego funcional, `tools/validate_sb3.py` implementa **dos niveles independientes de auditoría**:

1. **Auditoría Estructural y de Compatibilidad Scratch 3 (`validate_sb3_structure`)**:
   * Descomprime `NEXUS-BLOCKS-ENDLESS.sb3` y verifica la presencia de `project.json` en la raíz del archivo ZIP (`38` archivos internos en total).
   * Recalcula el hash MD5 real de los **37 activos multimedia** (29 disfraces vectoriales SVG y 8 efectos de sonido WAV) y comprueba que coincida exactamente con su `assetId` y nombre de archivo `<md5>.<ext>`.
   * Parsea cada archivo SVG con `xml.etree.ElementTree` para garantizar que no existan errores de XML mal formado, y abre cada archivo WAV con `wave` para verificar su codificación PCM mono a `22050 Hz`.
   * Recorre los **1052 bloques Scratch 3** distribuidos en los 14 objetos (`Stage` + 13 sprites), comprobando que el 100% de los `opcode` pertenezcan a la lista blanca oficial de Scratch 3, que no existan bloques huérfanos, que cada relación `parent ↔ next` y `parent ↔ input` sea bidireccional, y que todas las referencias a variables, listas, mensajes (`broadcasts`) y procedimientos (`procedures_call`) existan.
2. **Intérprete de Máquina Virtual Scratch 3 (`Scratch3VMInterpreter`)**:
   * Carga en memoria el grafo de bloques real contenido en `project.json` del archivo `.sb3` y **ejecuta directamente las instrucciones de los bloques de Scratch** (bucles `control_repeat`, `control_repeat_until`, condicionales `control_if_else`, operaciones de listas `data_replaceitemoflist`, llamadas a procedimientos `procedures_call` y eventos `event_broadcast`) para comprobar el comportamiento matemático y de estado de todas las mecánicas.

## 2. Matriz de Resultados de las 11 Pruebas Obligatorias

| # | Prueba Obligatoria | Método de Ejecución | Resultado | Evidencia Obtenida |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Generación aleatoria equilibrada (7-Bag)** | Ejecución de 21 llamadas consecutivas al bloque `Extraer_De_Bolsa` en `Scratch3VMInterpreter`. | **SUPERADA** | Las 21 extracciones produjeron exactamente 3 bolsas completas de `{1, 2, 3, 4, 5, 6, 7}` (p. ej. `[1, 7, 4, 3, 2, 5, 6]`) sin repeticiones indebidas ni vaciado de lista. |
| **2** | **Movimiento contra paredes** | Ejecución de 15 llamadas seguidas a `Mover_Horizontal (-1)` y `Mover_Horizontal (1)` para cada una de las 7 piezas (`1..7`). | **SUPERADA** | Ninguna pieza atravesó las columnas `1` ni `10`; `Comprobar_Colision` devolvió `0` en la posición límite y `1` al intentar avanzar un paso más hacia la pared. |
| **3** | **Rotaciones cerca de paredes y obstáculos** | Ejecución de `Rotar_Pieza` con la pieza `I` vertical pegada a la pared izquierda y rodeada de bloques fijos en `Tablero`. | **SUPERADA** | En la pared izquierda, el sistema *Wall Kick* desplazó automáticamente la columna hacia el interior (`Rotacion_Exito = 1`); rodeada de obstáculos sólidos, impidió el giro (`Rotacion_Exito = 0`) sin superponer bloques. |
| **4** | **Colisiones al descender y Pieza Fantasma** | Ejecución de `Actualizar_Fantasma`, `Paso_Caida (1)` y `Caida_Instantanea` con la pieza `O` desde la fila 2. | **SUPERADA** | `Fila_Fantasma` se calculó en la fila `19`; la caída suave sumó `+1` punto en la fila `3`; la caída instantánea sumó `+32` puntos (`16 filas × 2`) y fijó los 4 bloques exactamente en las filas 19 y 20. |
| **5** | **Eliminación de 1, 2, 3 y 4 líneas** | Rellenado de 1, 2, 3 y 4 filas inferiores con un bloque testigo en la fila superior y ejecución de `Revisar_Y_Eliminar_Lineas`. | **SUPERADA** | Se eliminaron simultáneamente 1, 2, 3 y 4 líneas otorgando `100`, `300`, `500` y `800` puntos base, desplazando el bloque testigo hasta la fila 20 sin dejar bloques residuales. |
| **6** | **Intercambio Hold (`Guardar_Hold`)** | Ejecución de `Guardar_Hold` dos veces en el mismo turno y una vez tras fijar la pieza con `Caida_Instantanea`. | **SUPERADA** | El primer uso guardó la pieza activa y cargó `Siguiente_Pieza` poniendo `Puede_Guardar = 0`; el segundo intento en el mismo turno fue bloqueado; tras fijar la pieza, `Puede_Guardar` volvió a `1`. |
| **7** | **Reinicio después de Game Over** | Ocupación de la fila 2 de aparición, llamada a `Generar_Nueva_Pieza` y emisión del mensaje `Iniciar_Juego`. | **SUPERADA** | Al colisionar en la zona de aparición, `Estado_Juego` cambió a `"GAMEOVER"`; al emitir `Iniciar_Juego`, las 200 celdas de `Tablero` volvieron a `0` y `Puntuacion = 0`, `Lineas = 0`, `Nivel = 1`. |
| **8** | **Pausa y reanudación** | Emisión de `Alternar_Pausa`, intento de `Mover_Horizontal` y `Rotar_Pieza`, y segunda emisión de `Alternar_Pausa`. | **SUPERADA** | Durante `Estado_Juego == "PAUSA"`, la columna y rotación permanecieron intactas; al reanudar a `"JUGANDO"`, el movimiento volvió a responder con normalidad. |
| **9** | **Cambios de dificultad y modos** | Ciclos completos de `Cambiar_Dificultad` y `Cambiar_Modo`, prueba en Nivel 50 y línea 40 en `SPRINT 40L`. | **SUPERADA** | Velocidades iniciales verificadas (`Fácil: 0.85s`, `Normal: 0.60s`, `Difícil: 0.38s`, `Pesadilla: 0.22s`), piso técnico `>= 0.06s` respetado en Nivel 50 y transición a `"VICTORIA"` al alcanzar 40 líneas en Sprint. |
| **10** | **Partidas prolongadas** | Simulación de 150 turnos consecutivos ejecutando movimientos, giros, Hold, caídas y renderizado Lápiz. | **SUPERADA** | Cero desbordamientos de listas, cero errores aritméticos y `Renderizar_Todo` registró correctamente los sellos `pen_stamp` del tablero, fantasma, pieza activa, `HOLD` y `NEXT`. |
| **11** | **Controles táctiles y teclado** | Disparo programático de los mensajes de botones táctiles (`Accion_Tactil` + `Ejecutar_Accion`) y verificación de sombreros `event_whenkeypressed`. | **SUPERADA** | Todos los códigos táctiles (`IZQ`, `DER`, `BAJAR`, `ROTAR`, `CAIDA`, `HOLD`) y eventos de teclado ejecutan los procedimientos correspondientes del motor. |

## 3. Pruebas Ejecutadas vs. Pruebas Visuales Pendientes en Navegador

* **Pruebas realizadas en este entorno (100% automatizadas)**:
  * Validación binaria del paquete ZIP `.sb3`, hashes MD5, estructura XML de los 29 SVG, cabeceras PCM de los 8 WAV y grafo completo de 1052 bloques.
  * Ejecución lógica completa del árbol de bloques de `project.json` mediante el intérprete `Scratch3VMInterpreter` en `tools/validate_sb3.py`.
* **Pruebas pendientes de verificación visual por el usuario en el iPad**:
  * Dado que el entorno de construcción opera en una máquina virtual sin navegador gráfico interactivo conectado a una pantalla física de iPad, queda para comprobación visual del estudiante al abrir `NEXUS-BLOCKS-ENDLESS.sb3` en Safari/Chrome del iPad: la comodidad ergonómica subjetiva de los botones táctiles según el tamaño de funda del iPad y el volumen acústico de los efectos WAV en los altavoces del dispositivo.
