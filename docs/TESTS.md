# Pruebas y límites — 2026-10-19

## Firma y efectos de sonido — 2026-10-21

- `python tools/build_sb3.py`, `python tools/validate_sb3.py` y `python tools/test_sb3.py`: aprobados. El proyecto contiene 50 entradas ZIP, 49 activos con hashes/formato verificados y 1221 bloques Scratch.
- Se confirmó la firma en ambos SVG de fondo y la presencia de los siete WAV autorizados. Las pruebas funcionales seleccionan exactamente un efecto 07–10 por jugada, avanzan `Nivel` al alcanzar 10 líneas, disparan `12_level_up` una vez y limitan `11_chaos_warning` a una vez por ataque.
- `npm ci --ignore-scripts` y `npm test`: aprobados. El planificador Scratch VM comprobó las mecánicas e interacciones, pero el entorno indicó que no hay módulo de renderizado ni motor de audio. Por ello, no se afirma una reproducción auditiva real ni una comprobación visual del aspecto final en el editor oficial.
- Pendiente: escuchar los sonidos y verificar visualmente la firma en el editor Scratch 3 con renderizado y sonido habilitados.

## Evidencia ejecutada

- Python: estructura ZIP, hashes MD5, SVG/XML, WAV/PCM, opcodes oficiales y grafo sin huérfanos. Artefacto: 4 targets, 1178 bloques, 42 recursos.
- Intérprete de bloques del SB3: 7-bag, paredes con siete piezas, wall kicks y giro bloqueado, ghost, soft/hard drop, 1/2/3/4 líneas y puntuación, hold, top-out, reinicio, pausa, velocidades, aceleración, garbage y 150 ciclos. Incluye 20 segundos simulados del mismo Tick que llama el hilo principal.
- Motor oficial scratch-vm 5.0.300 con scratch-storage 6.2.1: carga real del SB3 y planificador en tiempo de pared. Cada modo se dejó 20.1 segundos sin ninguna entrada tras arrancar. Se midió la mediana de los primeros diez intervalos de descenso consecutivos, excluyendo el salto de spawn. No se confundió una variable de velocidad con un intervalo observado.

| Modo | Configurado, s/fila | Mediana observada, s/fila | Fijaciones en 20.1 s |
| --- | --- | --- | --- |
| NORMAL | 0.650 | 0.669 | 1 |
| HARD | 0.300 | 0.318 | 3 |
| CHAOS | 0.230 | 0.247 | 6 |

Resultados de esa ejecución: [runtime-results.json](runtime-results.json). La gravedad no otorgó puntos de soft drop. La prueba oficial cubre también pausa durante 1.1 segundos con tiempo y fila congelados, reanudación, flechas, giro, hold sostenido, hard drop sostenido sin doble fijación, soft drop, reinicio y selección de modos. Para alcanzar eventos Chaos sin depender de una partida humana, ajusta sus deadlines mediante fixtures: DIFFICULT PIECES, SPEED BURST, aviso y garbage con nueve obstáculos y un hueco.

El test Node no conecta renderer ni audio: sus avisos de recursos sin renderer/audio son esperables. No acredita rendimiento visual ni sonidos. Las dependencias npm son exclusivamente de desarrollo, no se incluyen en el SB3; el árbol oficial fijado reportó vulnerabilidades transitivas en npm audit. No se hicieron actualizaciones incompatibles para ocultarlas.

## Navegador oficial

Se importó el SB3 en https://scratch.mit.edu/projects/editor/ mediante File / Load from your computer y se abrió a pantalla completa. Se observaron menú en inglés sin botones, caída sin entrada durante más de 20 segundos, pila fijada y nuevas piezas. Se ejecutaron selección de Hard, Enter, izquierda, giro, C, Space y P; se verificaron hold, pila y panel de pausa. Se volvió a importar el artefacto final tras los cambios de presentación.

La prueba se realizó en navegador de escritorio, no en iPad. No se afirma haber medido los intervalos por captura de vídeo en Safari ni haber evaluado auditivamente los sonidos.

## Investigación del fallo reportado

La inmovilidad absoluta original NO se reprodujo en el motor oficial: una copia del SB3 previo descendió de fila 3 a fila 9 durante cinco muestras de un segundo, sin teclado. No hay evidencia suficiente para atribuir el síntoma de iPad a una causa raíz única confirmada.

Sí se identificaron riesgos concretos: varias hats de teclado con autorepeat podían reiniciar scripts; las acciones y gravedad mutaban estado desde hilos distintos; la pausa reiniciaba el reloj de gravedad pero no congelaba deadlines de Chaos; no había bloqueo de superficie independiente; las pruebas antiguas llamaban procedimientos y nunca ejecutaban el bucle de gravedad. La nueva arquitectura elimina esos riesgos y prueba el planificador. Esto no demuestra retrospectivamente cuál causó el síntoma original.

## Pendiente y límites conocidos

- Teclado físico de iPad escolar con Safari, foco, teclas y rendimiento a pantalla completa.
- Medición visual de la cadencia y carga máxima en iPad, especialmente el piso de 0.07 s/fila. Ese valor es un límite configurado, no una velocidad verificada en dispositivo.
- Evaluación auditiva de los siete sonidos y legibilidad en el iPad físico.
- Las pestañas en segundo plano pueden ser limitadas por el navegador. El delta está acotado a 0.1 s y descarta retrasos grandes en vez de acumular caídas al volver.

## Reproducción

Ejecutar desde la raíz: python tools/build_sb3.py; python tools/validate_sb3.py; python tools/test_sb3.py. Para planificador oficial: npm ci --ignore-scripts y npm test. El test tarda algo más de un minuto. Los tests estructurales y lógicos no sustituyen la aceptación en el dispositivo final.
