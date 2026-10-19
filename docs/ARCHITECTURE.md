# Arquitectura Interna — NEXUS BLOCKS: ENDLESS

Este documento explica cómo está estructurado el proyecto dentro de Scratch 3 para que cualquier estudiante o desarrollador pueda inspeccionar, comprender y modificar sus sistemas sin romper la lógica del juego.

## 1. Principios de Diseño en Scratch 3

1. **Cero uso de clones para el tablero (Extensión Oficial Lápiz / Pen)**:
   * Scratch 3 impone un límite estricto de **300 clones** simultáneos. Un tablero de `10x20` celdas ocupa por sí solo 200 bloques, lo que sumado a la interfaz y vistas previas satura fácilmente el motor si se usan clones.
   * Para garantizar un rendimiento constante en el navegador de un iPad escolar, el objeto **`Motor_Juego`** utiliza un bloque personalizado con la opción **"Ejecutar sin actualizar la pantalla" (`warp: true`)** llamado `Renderizar_Todo`. En cada actualización, borra el lienzo (`pen_clear`) y estampa (`pen_stamp`) únicamente las celdas ocupadas del tablero, las 4 celdas de la pieza fantasma, las 4 de la pieza activa y las miniaturas de `HOLD` y `NEXT`.
2. **Separación estricta de responsabilidades por Objetos (Sprites)**:
   * **`Stage` (Escenario)**: Almacena todas las variables globales, las listas de datos y los fondos vectoriales (`Fondo_Arcade` y `Fondo_Caos`).
   * **`Motor_Juego`**: Contiene toda la lógica matemática, física de colisiones, rotación, bolsa de 7 piezas, puntuación, bucle principal de tiempo y renderizador Lápiz.
   * **`Efecto_Linea`**: Muestra animaciones no bloqueantes (`¡LÍNEA!`, `¡DOBLE!`, `¡TRIPLE!`, `¡NEXUS x4!`) cuando se eliminan filas.
   * **`Pantalla_Estado`**: Gestiona las pantallas superpuestas de Menú Principal, Pausa, Game Over y Victoria en Sprint 40L.
   * **10 Objetos de Botones Táctiles (`Btn_*`)**: Cada botón táctil es un objeto independiente con detección directa de toque (`al hacer clic en este objeto` + sensor `¿ratón presionado? y ¿tocando puntero del ratón?`), lo que evita conflictos de coordenadas y permite mantener pulsado para desplazar piezas en el iPad.

## 2. Representación del Tablero y Geometría de las Piezas

### Lista `Tablero` (200 elementos)
El tablero visible de **10 columnas** (`c` de `1` a `10`, de izquierda a derecha) y **20 filas** (`f` de `1` a `20`, de arriba hacia abajo) se almacena en la lista unidimensional `Tablero` mediante la fórmula de índice en base 1 de Scratch:

$$\text{índice} = (f - 1) \times 10 + c$$

* Valor `0`: Celda vacía.
* Valores `1` a `7`: Bloque fijado con el color de la pieza correspondiente (`1 = I Cian`, `2 = O Amarillo`, `3 = T Púrpura`, `4 = S Verde`, `5 = Z Rojo`, `6 = J Azul`, `7 = L Naranja`).

### Tablas de Geometría Precalculadas (`Offset_X` y `Offset_Y`, 112 elementos)
En lugar de encadenar decenas de bloques condicionales `si / si no` para saber dónde están los 4 cuadrados de cada pieza en cada rotación, el proyecto utiliza dos listas constantes de **112 números** (`7 piezas × 4 rotaciones × 4 bloques`):

$$\text{tabla\_idx} = ((\text{tipo} - 1) \times 16) + (\text{rot} \times 4) + i \quad (i \in \{1, 2, 3, 4\})$$

Para cualquier pieza `tipo` (`1..7`) y orientación `rot` (`0..3`), las coordenadas en el tablero de su bloque $i$-ésimo son:
* $\text{bloque\_col} = \text{col} + \text{elemento}(\text{tabla\_idx}) \text{ de } \text{Offset\_X}$
* $\text{bloque\_fila} = \text{fila} + \text{elemento}(\text{tabla\_idx}) \text{ de } \text{Offset\_Y}$

## 3. Bloques Personalizados ("Mis Bloques") en `Motor_Juego`

Todos los bloques personalizados se ejecutan con `warp = true` (*Sin actualizar la pantalla*) para completarse de forma atómica dentro de un mismo fotograma:

| Bloque Personalizado | Responsabilidad Técnica |
| :--- | :--- |
| `Rellenar_Bolsa_7` | Comprueba si la lista `Bolsa_7` está vacía; si lo está, inserta las piezas `1, 2, 3, 4, 5, 6, 7`. |
| `Extraer_De_Bolsa` | Elige un índice al azar de `Bolsa_7`, guarda el valor en `temp_pieza`, lo elimina de la lista y recarga la bolsa si queda vacía. Garantiza que nunca salgan más de 2 piezas iguales seguidas y que cada ciclo de 7 piezas contenga todos los tetrominós. |
| `Comprobar_Colision (tipo) (col) (fila) (rot)` | Recorre los 4 bloques de la pieza propuesta. Si alguno sale de `col 1..10` o `fila 1..20`, o coincide con una celda de `Tablero > 0`, asigna `Colision_Detectada = 1`; en caso contrario, `0`. |
| `Mover_Horizontal (delta_col)` | Verifica con `Comprobar_Colision` si `Pieza_Col + delta_col` está libre. Si no hay colisión, actualiza `Pieza_Col`, reproduce `Sonido_Mover`, recalcula la pieza fantasma y redibuja. |
| `Rotar_Pieza` | Calcula `test_rot = (Pieza_Rotacion + 1) mod 4` y prueba secuencialmente los 6 desplazamientos de las listas `Kick_X` (`[0, -1, 1, 0, -2, 2]`) y `Kick_Y` (`[0, 0, 0, -1, 0, 0]`). Aplica el primer desplazamiento sin colisión (*Wall Kick*). |
| `Actualizar_Fantasma` | Parte de `Fila_Fantasma = Pieza_Fila` e incrementa fila a fila hasta detectar colisión en `Fila_Fantasma + 1`, determinando el punto exacto de aterrizaje. |
| `Paso_Caida (es_suave)` | Intenta descender 1 fila. Si está libre, incrementa `Pieza_Fila` (sumando puntos si `es_suave = 1`); si hay colisión debajo, reproduce `Sonido_Caida` y llama a `Fijar_Y_Procesar_Pieza`. |
| `Caida_Instantanea` | Suma `(Fila_Fantasma - Pieza_Fila) * 2 * Multiplicador_Caos` a `Puntuacion`, traslada la pieza a `Fila_Fantasma` y la fija inmediatamente. |
| `Guardar_Hold` | Si `Puede_Guardar == 1`, guarda `Pieza_Actual` en `Pieza_Guardada` (o las intercambia si ya había una guardada), reposiciona en `(col=5, fila=2)` y bloquea `Puede_Guardar = 0` hasta el siguiente turno. |
| `Fijar_Y_Procesar_Pieza` | Escribe los 4 bloques de la pieza activa en `Tablero`, invoca `Revisar_Y_Eliminar_Lineas`, y si la partida sigue en `"JUGANDO"`, invoca `Generar_Nueva_Pieza` y `Renderizar_Todo`. |
| `Revisar_Y_Eliminar_Lineas` | Escanea de la fila 20 a la 1. Cada vez que detecta una fila sin ceros, incrementa `Lineas_Turno`, desplaza todas las filas superiores una posición hacia abajo sin decrementar el puntero de fila actual (para capturar líneas múltiples consecutivas), limpia la fila 1 y calcula puntos, combos, nivel y condición de victoria en `SPRINT 40L`. |
| `Actualizar_Velocidad_Y_Caos` | Ajusta `Velocidad_Caida` según `Dificultad`, `Modo_Juego`, `Nivel` y `Evento_Caos`, aplicando siempre un tope mínimo de `0.06 s`. |
| `Iniciar_Partida` | Reinicia las 200 celdas de `Tablero` a `0`, vacía y rellena `Bolsa_7`, restablece contadores (`Puntuacion`, `Nivel`, `Lineas`, `Combo`, `Pieza_Guardada`) y arranca la partida limpia. |
| `Renderizar_Todo` | Borra el lienzo Lápiz y estampa los bloques del tablero, la pieza fantasma, la pieza activa y las vistas previas `NEXT` y `HOLD`. |

## 4. Cómo Modificar o Ampliar el Juego

* **Cambiar colores de las piezas**: Abre el objeto `Motor_Juego`, entra en la pestaña **Disfraces** y edita los disfraces `Bloque_1_I` a `Bloque_7_L`.
* **Ajustar velocidades de caída**: En `Motor_Juego`, localiza el bloque `definir Actualizar_Velocidad_Y_Caos` y modifica los valores de `Velocidad_Base` (`0.85`, `0.60`, `0.38`, `0.22`).
* **Añadir nuevos eventos a Chaos Mode**: En el bucle principal `al hacer clic en bandera verde` de `Motor_Juego`, amplía el bloque condicional que selecciona `Evento_Caos` cada 15 segundos y añade su efecto en `Actualizar_Velocidad_Y_Caos` o `Revisar_Y_Eliminar_Lineas`.
