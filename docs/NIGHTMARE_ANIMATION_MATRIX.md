# Matriz de animación NIGHTMARE

Una fila «implementada» indica código conectado, no calidad visual verificada. Duraciones son segundos lógicos; Scratch puede limitar el avance a 0,1 s por tick. No se realizó reproducción gráfica real en este entorno.

| Efecto / activación | Estado | Duración | Pausa | M | Evidencia automática |
| --- | --- | --- | --- | --- | --- |
| Entrada de Nightmare, al iniciar | Implementada | 0,8 | Sí | Sin desplazamiento/escala | Intro, pausa y reloj en `validate_sb3.py` |
| Selección Endless/Trials al pulsar 4 | Implementada: escala del submodo y entrada del menú | 0,6 | Menú no pausado | Estática | Tecla 4 y temporizador en planificador |
| Avisos, garbage, jam, deuda, cadena, presión | Implementada: señal de margen activada por estado, avisos persistentes | 0,8 | Sí | Suprime señal secundaria | `Nightmare_VisualCue`, aviso y pausa en `validate_sb3.py` |
| Entrada y daño de blindaje | Implementada: entrada y golpe señalados; celdas 9 intactas, 10 agrietadas | 0,8 / estado persistente | Sí | Suprime señal, no celdas | Ataque y daño en `validate_sb3.py` |
| Destrucción de blindaje | Implementada: la limpieza de una fila agrietada activa señal; desaparece la fila | 0,8 | Sí | Suprime señal | `Armor_Broken` en filas individuales y múltiples |
| Objetivo de Trials | Implementada: señal al limpiar y cada cinco fijaciones, progreso persistente y panel de siguiente ola | 0,8 / panel 3 | Sí | Suprime señal y desplazamiento | Progreso y transición en `validate_sb3.py` |
| Inicio y finalización de objetivo | Implementada: señales diferentes al inicio y cuando se cumplen las condiciones de transición | 0,8 | Sí durante intermedio | Sin señal secundaria | Inicio, final y caducidad de señal en `validate_sb3.py` |
| Introducción de Core | Implementada: panel de transición de la quinta ola | 3, entrada 0,8 | Sí | Panel estático | Progresión en intérprete y planificador |
| Entrada de Glitch | Implementada: panel interpolado, revelado y escala de arena y núcleo | 0,8 | Sí | Arena estática | Entrada, escala, revelado, pausa y M en `validate_sb3.py` |
| Cinco avisos y ataques Glitch | Implementada: movimiento de amenazas, carga, activación y daño del núcleo | 0,6 aviso + hasta 0,4 activo por patrón | Sí | Sin cambio: información esencial | Cinco colisiones, rutas muestreadas e invulnerabilidad |
| Resultado y salida de Glitch | Implementada: panel de resultado, reducción de arena y retorno | 0,65 | Sí | Arena estática | Éxito, fracaso, penalización, reintento y retorno |
| Game Over Nightmare / derrota Core | Implementada: paneles diferentes con entrada vertical | 0,8 | No hay pausa en Game Over | Estático | Temporizador y reset en intérprete; render pendiente |
| Victoria Trials / Core | Implementada: panel con entrada horizontal | 0,8 | No hay pausa en victoria | Estático | Victoria y reloj en intérprete; render pendiente |
| Regreso al menú y selección | Implementada: menú se desplaza y escala tras seleccionar modo desde Nightmare; reinicio usa entrada Nightmare | 0,6 / 0,8 | Menú no pausado; intro sí | Sin desplazamiento/escala | Selección y reinicio en planificador |
