# Arquitectura — NEXUS BLOCKS V2

El juego existente sigue generado por tools/build_sb3.py como proyecto Scratch 3 nativo. No hay runtime web externo. La extensión oficial Pen estampa el tablero y el HUD sin clones ni monitores. Los cuatro targets son Stage, Motor_Juego, Efecto_Linea y Pantalla_Estado. Se eliminaron sprites, recursos y eventos táctiles.

Los fondos Normal y Chaos comparten la firma discreta del creador en SVG; el pulgar se dibuja como vector para no depender de fuentes emoji. Los WAV autorizados 07–13 se guardan en `assets/sfx/` y el generador los incorpora con sus hashes y metadatos. Los efectos de línea se eligen por `Lineas_Turno`; Chaos usa `Aviso_Ataque` para emitir una sola advertencia por ataque. Al borrar líneas, `Nivel` avanza a `1 + floor(Lineas / 10)` sin recalcular la puntuación de esa misma jugada con el nivel nuevo.

## Planificación y gravedad

Un único hilo ejecuta Tick, Leer_Teclado y una espera cooperativa de 0.01 s. Los procedimientos finitos son warp y atómicos. El planificador de Scratch limita la cadencia a los frames disponibles; una espera de 0.01 no promete 100 FPS.

Tick lee sensing_timer, calcula el delta y actualiza Ultimo_Tick incluso en pausa. Solo en JUGANDO añade tiempo a Tiempo_Juego. Limita el delta a 0.1 s para descartar retrasos de pestañas suspendidas. Todas las deadlines de física y Chaos usan este reloj lógico. Reiniciar restaura su origen. Pausar conserva el tiempo restante de gravedad, bloqueo y eventos.

Actualizar_Velocidad_Y_Caos centraliza la fórmula: base / (1 + (nivel - 1) * factor), con bases 0.65 / 0.30 / 0.23 y factores 0.045 / 0.055 / 0.04 para NORMAL / HARD / CHAOS. Chaos divide además por (1 + tiempo / 180); SPEED BURST multiplica por 0.5. El intervalo final nunca baja de 0.07 s. Cada 10 líneas sube el nivel. La gravedad se evalúa aunque no haya teclas pulsadas.

Al detectar superficie, Bloqueo registra el tiempo lógico. Si sigue en superficie tras 0.35 s, se fija la pieza y aparece la siguiente. Despegarse borra el contador. Los movimientos sobre superficie no lo reinician indefinidamente. Hard drop fija inmediatamente. Spawn y hold restablecen el contador; un hold que colisiona en la aparición termina la partida.

## Entrada

Leer_Teclado consulta sensores oficiales. Los latches key_* detectan flancos para giro, hard drop, hold, pausa, restart, selección y Enter. Solo izquierda/derecha/abajo repiten mediante deadlines reales separadas de la gravedad (160 ms DAS, 50 ms ARR; abajo 50 ms). No hay hats de teclado que se reinicien con el autorepeat del sistema operativo. La entrada y la física mutan el estado en el mismo hilo.

## Chaos

El primer evento empieza a los 12 segundos. Alterna DIFFICULT PIECES y SPEED BURST durante 7 segundos. La frecuencia aumenta con la supervivencia: intervalo de ataque = max(10, 25 - tiempo/30); el siguiente evento se programa a 0.6 veces ese intervalo. No hay gravedad lunar ni bonus que sustituyan desafío.

DIFFICULT PIECES sesga futuras extracciones hacia S/Z con un 65% de sustitución. NEXT anuncia la pieza que realmente aparecerá. Fuera del evento se conserva el 7-bag clásico.

El primer garbage llega a los 25 segundos con aviso de 2 segundos. Desplaza el tablero una fila arriba e introduce 9 obstáculos y un hueco aleatorio abajo. Si había celdas fijadas en la fila superior hay top-out. La pieza activa permanece si sigue libre; si colisiona con el tablero desplazado, se eleva una fila y se comprueba otra vez. Se recalcula el fantasma. Una pieza recién aparecida no se eleva innecesariamente.

## Geometría y presentación

Tablero 10x20, índice (fila - 1)*10 + columna, siete tetrominós, cuatro rotaciones y seis candidatos de wall kick. Se mantiene la geometría original, ghost, hold, NEXT, combos, líneas y sonidos. Puntuación de 1/2/3/4 líneas: 100/300/500/800 por nivel, más combo; soft/hard drop suman 1/2 puntos por fila.

El tablero ocupa 150x300 de los 480x360 px. Etiquetas y paneles están en inglés; los identificadores internos conservan nombres españoles. El HUD estampa SVG sin monitores. Los paneles no contienen botones ni eventos de click.

El ZIP SB3 tiene timestamps fijos y orden estable: la misma fuente produce bytes reproducibles. validate_sb3.py comprueba hashes, formatos y enlaces; test_runtime.cjs ejecuta el planificador oficial sin emular la física.
