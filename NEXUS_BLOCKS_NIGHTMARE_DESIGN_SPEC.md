# NEXUS BLOCKS — NIGHTMARE
## Especificación de diseño, animaciones y plan de implementación en rama aislada

**Documento:** `NEXUS_BLOCKS_NIGHTMARE_DESIGN_SPEC.md`  
**Versión de diseño:** 0.1 — propuesta inicial, pendiente de validación con pruebas reales  
**Fecha:** 2026-10-28  
**Proyecto:** NEXUS BLOCKS  
**Repositorio:** https://github.com/Dracalight/Blocks  
**Rama de trabajo propuesta:** `feat/nightmare-mode-v1` (crear desde el `main` vigente; confirmar que no exista antes)  
**Estado:** **DISEÑO — no implementado ni aprobado como balance definitivo**  
**Alcance:** modo NIGHTMARE, sistema de eventos, retos de supervivencia, microjuego de esquiva, presentación y animaciones.  
**Regla de oro:** **no romper ni modificar la jugabilidad de Normal, Hard y Chaos**.

---

## 0. Resumen ejecutivo y decisiones tomadas

Se desea crear un **cuarto modo, NIGHTMARE**, más difícil que CHAOS, pero **sin aumentar su velocidad máxima de caída**. La dificultad debe proceder de tomar mejores decisiones bajo presión, gestionar amenazas combinadas y superar situaciones de supervivencia reconocibles. El usuario quiere, además, **muchas animaciones**, con identidad visual propia y rendimiento aceptable en Scratch 3.

Elementos solicitados o discutidos:

1. **Double Garbage**, sugerido por un compañero: ataque de dos filas de basura.
2. **Hold Jam**: inutilización temporal del intercambio de piezas.
3. **Garbage Debt**: deuda de basura que el jugador puede reducir cumpliendo objetivos.
4. **Chaos Chain**: combinaciones de eventos con reglas de compatibilidad y advertencia.
5. **Presión acumulativa**: peligro diferido y gestionable, nunca una avalancha oculta.
6. **Bloques blindados**: obstáculos que resisten una limpieza y requieren tratamiento especial.
7. **Nightmare Trials**: desafíos tipo coliseo por oleadas y objetivos de supervivencia.
8. **Glitch Protocol / Core Survival**: microjuego original de esquiva con un núcleo energético, rayos y patrones digitales; inspiración de género en el esquive de proyectiles y la supervivencia, **sin copiar personajes, corazón rojo, cajas, ataques, música ni arte reconocibles de Undertale o Hollow Knight**.
9. **Animaciones abundantes**: intro, alertas, cargas de ataques, impactos, fracturas, oleadas, victoria y derrota, con medidas anti-lag y legibilidad.

**Separación recomendada de modalidades:**

- `NIGHTMARE ENDLESS`: puntuación ilimitada, comparable consigo misma, sin final fijo.
- `NIGHTMARE TRIALS`: cinco oleadas consecutivas, objetivos de supervivencia y pantalla de victoria.
- `NIGHTMARE TRIALS+`: variante posterior con modificadores; **NO** incluir en el primer piloto si compromete estabilidad.

Estas son propuestas de producto; las cifras que aparecen a continuación son **valores iniciales de balance**, no hechos confirmados por playtesting.

---

## 1. Contexto real del repositorio — comprobado en lectura

**Fuentes consultadas** en `main` al preparar el documento:

- `README.md`: tres modos actuales (NORMAL/HARD/CHAOS); reconstrucción y verificación.
- `docs/ARCHITECTURE.md`: reloj lógico, control, física, ataques Chaos, geometría y renderizado.
- `tools/build_sb3.py`: generador Python y fuente de verdad de `.sb3`.

### 1.1 Contratos existentes que deben mantenerse

| Aspecto | Estado observado | Restricción para NIGHTMARE |
|---|---|---|
| Juego | Scratch 3 nativo `.sb3`, generado desde Python | No introducir una dependencia de navegador o runtime externo en el juego distribuido. |
| Generador canónico | `tools/build_sb3.py` | Modificar el generador; regenerar el `.sb3`; no editar solo un binario `.sb3`. |
| Tablero | 10 columnas x 20 filas | Conservar representación y reglas originales para modos 1–3. |
| Caída mínima | 0,07 s/fila | **Nightmare nunca debe reducirla**. |
| Caída inicial Chaos | 0,23 s/fila, con progresión y ráfagas | Nightmare puede heredar la fórmula de Chaos; no añadir un multiplicador que traspase el mínimo. |
| Bloqueo | 0,35 s sobre superficie | Mantener inicialmente, evitar endurecer todo a la vez. |
| Eventos Chaos | Primer evento ~12 s, primera basura ~25 s | Reutilizar contratos compatibles y priorizar cambios encapsulados. |
| Control | Flechas, espacio, C, P, R, selección 1/2/3, Enter | Conservar mapeo en modos existentes; añadir modo 4 sin romper selección. |
| Render | Extensión Pen; escenario 480x360; 4 targets | Favorecer estampado y SVG, con presupuesto de render; nuevos targets solo si se justifican. |
| Temporización | Bucle de un hilo: `Tick`, `Leer_Teclado`, espera cooperativa 0,01 s | Estados y timers explícitos, sin loops paralelos que muten el tablero. |
| Pausa | Congela gravedad, bloqueo y plazos de Chaos | Congelar también eventos, oleadas, microjuego y animaciones jugables. |
| Regeneración | ZIP `.sb3` de construcción reproducible | Preservar determinismo y validadores. |

**Ojo:** la espera cooperativa de `0,01 s` no implica 100 FPS reales. Los efectos deben diseñarse para las capacidades del planificador Scratch y probarse en iPad/teclado y escritorio.

### 1.2 Riesgo previo observado durante partidas escolares

Se relató **una observación aislada, no reproducida**, de una pieza **T** rotada rápidamente antes de una limpieza aparentemente extraordinaria. **No se considera un bug confirmado**: un T-spin double puede limpiar dos líneas legítimamente y se requiere distinguir geometría real, wall kicks, timing, estado del tablero y renderizado. Antes de endurecer mecánicas de limpieza y blindaje, agregar prueba de regresión `QA-ROT-T-01` para verificar que la pieza fija exactamente sus cuatro minos y que solo se eliminan líneas completas; comprobar además secuencias legales de T-spin double.

---

## 2. Filosofía de diseño de NIGHTMARE

**Objetivo:** convertir la dificultad en **anticipación + toma de decisiones + gestión de recursos + ejecución**, no en una velocidad arbitraria.

Principios vinculantes:

1. **Legibilidad:** todo evento que pueda perjudicar al jugador tiene aviso visible y tiempo de respuesta.
2. **Justicia:** no lanzar combinaciones inevitables; registrar y limitar la acumulación de amenazas.
3. **Habilidad por encima de azar:** aleatoriedad acotada, telegráfica y reproducible con semilla en pruebas.
4. **Dificultad adicional, no descontrol:** la gravedad respeta siempre el mínimo de Chaos; no confundir efectos visuales con velocidad física.
5. **Integridad:** pausa, reinicio, Hold, spawn, bloqueo, limpieza y top-out siguen siendo coherentes.
6. **Rendimiento:** animaciones no deben bloquear lectura del teclado ni añadir decenas de clones.
7. **Identidad:** estética digital/energética propia de NEXUS BLOCKS; referencias externas únicamente como inspiración abstracta.
8. **Aislamiento:** Normal/Hard/Chaos siguen funcionando y presentándose igual, salvo cambios mínimos y comprobados necesarios para mostrar la nueva opción en el menú.

### 2.1 Estructura recomendada

```text
NEXUS BLOCKS
├── NORMAL                 (existente; intacto)
├── HARD                   (existente; intacto)
├── CHAOS                  (existente; intacto)
└── NIGHTMARE              (nuevo)
    ├── ENDLESS            (puntuación y resistencia)
    └── TRIALS             (cinco oleadas)
        └── TRIALS+        (futuro; detrás de una bandera)

Motor de eventos Nightmare
├── WARNING / TELEGRAPH
├── DOUBLE_GARBAGE
├── HOLD_JAM
├── GARBAGE_DEBT
├── ARMORED_GARBAGE
├── CHAOS_CHAIN
└── GLITCH_PROTOCOL

Capa visual (solo presentación)
├── Intro / HUD / Avisos
├── Animaciones del tablero
├── Animaciones de oleadas
└── Arena de esquiva, proyectiles y telegráficos
```

---

## 3. Modelo de estados y precedencias

**No agregar hilos que muten la física en paralelo.** Mantener una única autoridad de actualización de estado.

Estados lógicos propuestos:

```text
MENU
  -> INTRO_NIGHTMARE
      -> PLAYING_NIGHTMARE
          -> EVENT_WARNING (la física sigue)
          -> EVENT_RESOLUTION (aplicar amenaza en instante seguro)
          -> TRIAL_INTERMISSION (tablero congelado; entre oleadas)
          -> GLITCH_INTRO (tablero congelado)
          -> GLITCH_DODGE (microjuego activo)
          -> GLITCH_RESULT (resolución única)
          -> PLAYING_NIGHTMARE / TRIAL_INTERMISSION
      -> GAME_OVER | TRIAL_CLEAR
```

`PAUSED` debe actuar como **estado superior**: congelar relojes lógicos de cualquier subestado; al despausar retomar exactamente el estado de origen. `RESTART` limpia todos los contadores, cola, animaciones, proyectiles, modificadores, flags y temporizadores asociados.

**Orden determinista en un tick de juego:**

1. Leer teclas y controlar pausa/reinicio/transiciones.
2. Si pausa o animación bloqueante, no avanzar física de tablero.
3. Avanzar reloj lógico de gameplay con delta limitado.
4. Resolver movimiento/rotación/drop/bloqueo/limpieza de línea.
5. Actualizar deudas y objetivos de oleada usando eventos de juego consumidos **una sola vez**.
6. Actualizar avisos y calendario de ataques.
7. Aplicar eventos vencidos solo en un **punto seguro** (sin pieza en proceso de fijarse o limpieza a mitad de frame).
8. Evaluar derrota/victoria de forma única.
9. Construir instantánea visual y estampar animaciones, sin alterar geometría por efectos visuales.

**Regla temporal:** usar `Tiempo_Juego`/reloj lógico o contadores de piezas bloqueadas, nunca tiempos de pared independientes para efectos que determinan resultados. Las transiciones de presentación y el microjuego usan relojes lógicos específicos, congelados durante pausa. Los segundos de intro y animación no consumen temporizadores de evento ni permiten gravedad en el tablero.

---

## 4. Sistema común de amenazas y balance

### 4.1 Definiciones

- `garbage_pending`: filas pendientes no materializadas, **0–4 máximo**, incluyendo deudas convertidas a ataque solo cuando vencen.
- `garbage_debt`: contrato cancelable independiente, con plazo en **piezas fijadas** y recompensa por limpiar líneas.
- `event_queue`: máximo 2 amenazas activas/comprometidas en la misma secuencia; las demás se aplazan.
- `event_cooldown`: intervalo mínimo después de resolver una amenaza para evitar saturación; sugerencia inicial: **6 piezas fijadas** antes de iniciar otra amenaza fuerte, salvo la segunda mitad de un Chaos Chain anunciado.
- `event_notice`: indicador de **qué ocurre, cuándo y con qué intensidad**, sin depender exclusivamente del color.
- `hazard_seed`: semilla opcional de QA para reproducir patrones en test, no para mostrar al jugador.

**Nunca materializar más de 4 filas pendientes en un solo tramo de resolución.** Si exceden, posponer *las filas sobrantes* con aviso explícito, no borrarlas silenciosamente. Mantener un tope total y un protocolo de saturación: al llegar al máximo de pendientes, suspender la generación de nuevas deudas/ataques de presión hasta que haya capacidad. Las penalizaciones de Glitch Protocol respetan este límite.

### 4.2 Orden de prioridad

1. `GAME_OVER` / `TRIAL_CLEAR` (si corresponde).
2. Resolución de una pieza fijada y limpieza del tablero.
3. Reducción/cancelación de deudas por líneas limpiadas.
4. Vencimiento de deudas y consolidación de garbage pendiente.
5. Aplicación de ataque anunciado, segura para el tablero.
6. Activación de nueva amenaza o transición.

No convertir un aviso en un ataque si el jugador entra a Glitch Protocol en ese mismo tick; primero fijar el orden y aplazar la amenaza hasta el regreso, sin pérdida ni duplicación.

---

## 5. Eventos normales de NIGHTMARE — reglas propuestas

### 5.1 DOUBLE GARBAGE

**Propósito:** presión espacial adicional con posibilidad de preparación.

| Campo | Regla v0.1 |
|---|---|
| Disparo | Evento elegible en Nightmare desde el arranque, sujeto a calendario y capacidad. |
| Aviso | **4 piezas antes** del ataque; mensaje `DOUBLE GARBAGE IN 4...3...2...1`. |
| Efecto | Aparecen **2 filas** de basura; un hueco por fila, posición predeterminada por semilla de evento. |
| Aplicación | Un único cambio de estado atómico, reutilizando la lógica de desplazamiento/top-out con soporte para N filas. |
| Cancelación | Si se habilita contrajuego, cada **2 líneas limpiadas durante la advertencia** reducen una fila de este ataque, máximo dos. Configurable; para piloto usar esta regla. |
| Límites | Nunca superar `garbage_pending <= 4`; respetar aviso y top-out. |
| Visuales | Letrero de peligro, barra de cuenta atrás, dos líneas luminosas entrando desde la base y onda de impacto. |

**Caso de prueba:** basura doble con pieza activa situada cerca de la cima; no atravesar celdas, no elevar de forma inconsistente, no generar top-out incorrecto. Probar también si las dos filas se cancelan por completo justo al vencer el aviso.

### 5.2 HOLD JAM

**Propósito:** restringir una herramienta táctica sin alterar caída ni giro.

| Campo | Regla v0.1 |
|---|---|
| Aviso | **2 piezas antes** de activarse. |
| Duración | **7 piezas fijadas** (no segundos). |
| Efecto | Tecla `C` no intercambia/guarda piezas; la pieza previamente guardada permanece intacta. |
| Conteo | Cada pieza fijada consume exactamente 1 unidad. Hard drop cuenta normalmente. |
| Interacciones | Puede coincidir con Garbage Debt si está anunciado por Chaos Chain; no reiniciar duración por reactivación. |
| Final | Al fijar la séptima pieza, Hold vuelve a habilitarse en punto seguro. |
| Visuales | Panel HOLD con sello de interferencia, efecto de pequeños glitches, contador `JAM: 7`…`1`, animación de restauración. |

**No** alterar la lógica de `hold_used_this_piece`: al salir del jam, la regla ordinaria de una utilización por pieza se mantiene.

### 5.3 GARBAGE DEBT

**Propósito:** introducir presión acumulada que el jugador pueda contrarrestar jugando bien.

| Campo | Regla v0.1 |
|---|---|
| Inicio | Se anuncia un contrato de **2 filas de deuda**. |
| Plazo | **12 piezas fijadas** a partir de activación. |
| Contramedida | Cada **2 líneas limpiadas** mientras el contrato está activo cancelan 1 fila, hasta 2 filas. |
| Final | Al cumplirse 12 piezas, las filas restantes pasan a `garbage_pending`, con aviso final de **2 piezas** antes de entrar. |
| Si se cancela | Mostrar `DEBT CLEARED`, sin ataque. |
| Si hay varias deudas | Solo **1 contrato activo** en el piloto; reprogramar otros, nunca sobreescribirlo. |
| Visuales | Medidor `DEBT 0/4 LINES`, cuenta atrás de piezas, filas virtuales sombreadas, efecto de cancelación. |

**Semántica importante:** las líneas que ya se limpiaron antes de activar la deuda no cuentan; una limpieza de cuatro líneas cancela dos filas; limpiar una sola línea deja progreso parcial. Registrar cada evento de limpieza exactamente una vez.

### 5.4 ARMORED GARBAGE / BLOQUES BLINDADOS

**Propósito:** dificultad estratégica al gestionar limpieza de filas.

**Concepto visual:** bloques de basura con borde metálico y un indicador de resistencia.

**Regla de diseño v0.1 — pendiente de prototipo técnico:**

1. Un ataque especial puede introducir **como máximo una fila blindada**.
2. Cada celda blindada posee resistencia `2`; las celdas ordinarias tienen resistencia implícita `1`.
3. Cuando una fila completa contiene al menos un bloque blindado con resistencia `2`, el intento de limpieza **desgasta** los bloques blindados de esa fila a resistencia `1` y **NO elimina la fila todavía**.
4. Una limpieza posterior de esa misma fila, ya sin resistencia extra, sí la elimina.
5. El evento de desgaste emite un efecto de fractura (`ARMOR BREAK`); no concede puntos/líneas de una limpieza efectiva ni incrementa la deuda cancelada.
6. La segunda limpieza, que sí elimina la fila, usa las reglas normales de puntuación y progreso.
7. Si coexisten varias filas completas, procesar desgaste y eliminación con una política simultánea determinista; **no compactar filas blindadas no eliminadas**.

**Advertencia arquitectónica:** la regla 3 cambia la lógica habitual de "fila completa = eliminación inmediata" y puede generar un tablero sin espacios vacíos en una fila no eliminada. Este diseño requiere **spike de viabilidad y test de jugabilidad** antes de comprometerlo: si produce atascos imposibles, sustituir por un sistema alternativo de "celdas blindadas que se agrietan al limpiar filas adyacentes" o "bloque endurecido que se destruye con una acción específica claramente anunciada". No implementar el modelo defectuoso solo para cumplir la especificación.

**No activar blindaje dentro de Chaos, Normal o Hard**.

### 5.5 CHAOS CHAIN

**Propósito:** encadenar amenazas entendibles, no convertir el tablero en una lotería.

| Campo | Regla v0.1 |
|---|---|
| Estructura | 2 subeventos, con orden definido y anunciado. |
| Aviso | Mostrar ambos nombres antes de comenzar: `CHAIN: HOLD JAM → GARBAGE DEBT`. |
| Transición | El segundo evento empieza **después** del primer hito definido, con al menos 2 piezas de advertencia. |
| Límite | Máximo 2 amenazas en una cadena; prohibido iniciar otra cadena mientras una esté activa. |
| Compatible piloto | `HOLD JAM → GARBAGE DEBT`; `DOUBLE GARBAGE → HOLD JAM`. |
| No compatible piloto | `DOUBLE GARBAGE + ARMORED GARBAGE` simultáneos si el tablero está muy alto; dos deudas superpuestas; dos microjuegos simultáneos. |
| Visuales | Tarjeta doble con conectores, progresión A→B, pulso cuando se activa la siguiente etapa. |

**Detector de riesgo recomendado:** no generar presión adicional si las cuatro filas superiores ya están ocupadas en un umbral elevado, si se ha alcanzado `garbage_pending` máximo o si no existe ventana de respuesta. Si un evento queda aplazado, anunciar `DELAYED` y reintentar cuando sea seguro; si la partida acaba, no aplicar eventos residuales.

---

## 6. NIGHTMARE ENDLESS — progresión inicial

La física de caída se basa en CHAOS y conserva el límite absoluto de **0,07 segundos/fila**. No se utiliza el incremento de velocidad como palanca principal de dificultad. Se conserva el nivel por líneas del juego existente.

### 6.1 Calendario de amenazas sugerido

| Fase | Supervivencia aproximada | Reglas iniciales |
|---|---|---|
| Entrada | 0–20 s | Presentación Nightmare; primera advertencia, sin castigo sorpresa. |
| Presión I | 20–60 s | Double Garbage / Hold Jam alternados. Solo un evento fuerte a la vez. |
| Presión II | 60–120 s | Introducir Garbage Debt; avisos y contrajuego. |
| Presión III | 120–180 s | Introducir Chaos Chain de dos etapas. |
| Presión IV | >180 s | Mayor frecuencia **controlada** de eventos, posible blindaje validado. No aumentar gravedad máxima. |

**Frecuencia:** propuesta: un evento fuerte cada **18–26 s de reloj lógico**, condicionado también a un mínimo de piezas fijadas y ventanas seguras. Evitar usar un temporizador de pared fijo si el juego está pausado o en Glitch Protocol. El planificador debería controlar tanto tiempo lógico como cantidad de piezas, para no saturar al jugador que se mueve lento.

**RNG:** selección ponderada por fase, semilla reproducible en pruebas. Evitar rachas imposibles (por ejemplo, tres Double Garbage seguidos); imponer regla anti-repetición donde proceda.

**Puntuación:** reutilizar reglas existentes; los premios de supervivencia o esquiva deben estar identificados y no crear una explotación infinita. Registrar récord Nightmare por separado del resto. No asumir guardado persistente de récords: actualmente los usuarios conservan capturas, y la persistencia **no** forma parte del alcance obligatorio de esta versión.

---

## 7. NIGHTMARE TRIALS — desafíos de supervivencia

Inspiración general: progresión por oleadas y tensión de supervivencia. **No imitar diseños de enemigos, escenarios ni material original ajeno.**

### 7.1 Reglas globales

- Cinco oleadas secuenciales; la partida termina en **TRIAL CLEARED** tras la quinta, o `GAME OVER` si el tablero supera las condiciones de derrota habituales.
- El tablero **permanece entre oleadas**; no se limpia gratuitamente.
- `INTERMISSION` de **3 s de presentación** con física y amenazas congeladas; no se pueden manipular piezas en ese intervalo.
- Los objetivos se miden en **piezas bloqueadas**, no tiempo real, para mejorar reproducibilidad y tolerar distintas capacidades de hardware.
- Las amenazas de la oleada deben aparecer en hitos previstos; si una amenaza queda pendiente al terminar, **resolverla/neutralizarla de forma explícita** antes de pasar, nunca descartarla en secreto. En el piloto: impedir transición hasta terminar avisos y saldar una amenaza activa, y no iniciar nuevas amenazas en esa espera.
- Cada oleada anuncia objetivos, eventos permitidos y progreso.
- El usuario puede pausar durante oleadas y desafíos; la pausa no reduce temporizadores ni plazos.

### 7.2 Cinco oleadas propuestas

| Oleada | Nombre | Meta | Guion de amenazas |
|---|---|---|---|
| I | `THE AWAKENING` | Bloquear **20 piezas** | Un Double Garbage anunciado hacia la pieza 10. |
| II | `BROKEN CONTROL` | Bloquear **25 piezas** | Dos Hold Jam separados, evitando solapamientos. |
| III | `THE DEBT` | Bloquear **30 piezas** | Dos Garbage Debt en ventanas con oportunidad de limpiar líneas. |
| IV | `NO MERCY` | Bloquear **35 piezas** | Una fila blindada (solo si el prototipo supera QA) y dos Chaos Chain escalonados. |
| V | `NIGHTMARE CORE` | Bloquear **40 piezas** | Tres etapas anunciadas: Double Garbage, Hold Jam + Debt, Chaos Chain. Incluir un Glitch Protocol final como clímax opcional. |

**Balance en prueba:** simular rutas de supervivencia con jugador competente y jugador promedio; si alguna oleada produce imposibilidad objetiva, rediseñar el patrón. El modo Trials no debe depender de RNG puro; preferir secuencias fijas o semilla por prueba.

### 7.3 NIGHTMARE TRIALS+ — después del piloto

Modificadores independientes, seleccionables al empezar y con tablas de récords separadas:

- `NO HOLD`: sin Hold durante toda la prueba.
- `HEAVY DEBT`: deuda máxima ligeramente superior, sujeta al límite global de basura.
- `IRON FIELD`: más blindaje en fases avanzadas, solo si el prototipo de blindaje está probado.
- `ENDURANCE`: un **25 % más** de piezas objetivo por oleada; definir redondeo y calendario sin aumentar densidad de eventos sin control.

**Exclusión:** no presentar modificadores como funcionalidad lista en v1. Mantener flags apagados por defecto.

---

## 8. GLITCH PROTOCOL — microdesafío original de esquiva

### 8.1 Identidad

**Nombre propuesto:** `GLITCH PROTOCOL`, subtítulo `NEXUS CORE SURVIVAL`.  
**Fantasía:** un protocolo digital de emergencia que pone a prueba la resistencia del **NEXUS CORE** mediante ataques de energía y patrones geométricos.

**Diferenciación visual y jugable:** el avatar es un **rombo/fragmento de energía** (no corazón rojo); arena de **retícula digital**; rayos, pulsos y fragmentos originales; interfaz y música/SFX propios. Evitar replicar ataques, colores, patrones característicos o arte concretos de Undertale/Hollow Knight.

### 8.2 Reglas concretas para un primer prototipo

| Campo | V0.1 |
|---|---|
| Activación | Evento poco frecuente en Nightmare Endless; en Trials puede ser oleada especial/etapa final. |
| Frecuencia Endless | No antes de **60 s** de juego, y como máximo una vez cada **45 s** adicionales de reloj de gameplay. No activarlo en cadena activa sin cerrar. |
| Duración | **5 s efectivos de esquiva**, excluyendo intro, resultado y pausa. |
| Arena | Rectángulo digital propio de aproximadamente **120x120 px** centrado, dentro del escenario de 480x360. Tamaño exacto a validar. |
| Avatar | Rombo luminoso, radio de colisión menor que su brillo visual. |
| Controles | Flechas mueven avatar, con movimiento diagonal normalizado o prohibición explícita de diagonal, según resultado de prototipo. `P` pausa, `R` reinicia según política de juego. |
| Física tablero | **Totalmente congelada** mientras el microjuego está activo; gravedad, lock delay, garbage y plazos se preservan. |
| Impactos | 3 puntos de integridad (`CORE HP=3`) al iniciar. Un impacto descuenta 1 y otorga **0,45 s de invulnerabilidad**. |
| Victoria | Sobrevivir 5 s con al menos 1 HP. |
| Derrota | Llegar a 0 HP, o fallar una condición especial explícita si se añade más adelante. |
| Recompensa | Cancelar hasta **2 filas de basura pendiente**; si no existen, cancelar hasta 1 fila de deuda activa; si ninguna existe, otorgar un bono pequeño de puntuación, con límite por evento. |
| Penalización | Añadir **hasta 2 filas de basura** como Double Garbage **con advertencia al retornar**; nunca daño/muerte automática durante la transición. |
| No explotación | No dar recompensa si el jugador reinicia/abandona la prueba; registrar resolución exactamente una vez. |

**Importante:** no se debe convertir Glitch Protocol en una forma de escapar gratis de un top-out ya determinado. Si `GAME_OVER` está confirmado, no se inicia. Si se invoca mientras hay una amenaza por resolverse, preservar la amenaza y el orden original y reanudar solo después del resultado.

### 8.3 Patrones de ataque originales — catálogo

| ID | Ataque | Aviso | Resolución / evasión | Dificultad |
|---|---|---|---|---|
| `BEAM_H` | **Signal Beam horizontal** | Línea tenue 0,55 s | Rayo sólido 0,25 s a altura anunciada; hueco seguro alcanzable. | Baja |
| `BEAM_V` | **Signal Beam vertical** | Columna tenue 0,55 s | Barrido breve desde borde; jugador se aparta. | Baja |
| `DATA_FRAG` | **Data Fragments** | Destellos de borde 0,45 s | Cuadrados/triángulos avanzan en trayectorias simples. | Media |
| `SWEEP_WALL` | **Sweep Wall** | Muro fantasma 0,70 s | Pared avanza con una **apertura visible**. | Media |
| `PULSE_GRID` | **Pulse Grid** | Filas/columnas resaltadas 0,65 s | Solo se dañan celdas marcadas; resto permanece seguro. | Alta |
| `TARGET_ZONE` | **Target Markers** | Baldosas marcadas 0,65 s | Impacto localizado; el jugador se recoloca. | Media |

Para v1, implementar primero **`BEAM_H`, `BEAM_V` y `TARGET_ZONE`**. Los demás se habilitan tras medir legibilidad y rendimiento. Nunca lanzar patrones que cubran todo el espacio libre; la ruta segura debe ser físicamente alcanzable con la velocidad del avatar desde las posiciones razonables de aparición.

### 8.4 Secuencia de muestra de 5 s

```text
-0.80 s a 0.00 s: GLITCH PROTOCOL — intro y controles (tablero congelado).
 0.00 s a 0.55 s: aviso BEAM_H (fila 2/4).
 0.55 s a 0.80 s: impacto BEAM_H.
 0.80 s a 1.40 s: zona segura de desplazamiento + aviso TARGET_ZONE.
 1.40 s a 1.65 s: impacto TARGET_ZONE.
 1.65 s a 2.25 s: aviso BEAM_V.
 2.25 s a 2.50 s: impacto BEAM_V.
 2.50 s a 3.20 s: aviso doble no simultáneo (dos líneas con espacio seguro).
 3.20 s a 4.00 s: activaciones escalonadas, nunca encerrando el avatar.
 4.00 s a 5.00 s: último patrón corto + confirmación supervivencia.
 5.00 s a 5.65 s: pantalla de resultado y animación.
```

La lista es un *storyboard* de diseño, no una garantía de que los patrones son esquivables. Validar cada posición inicial, ventana de reacción, hitbox y fps real antes de aceptar.

### 8.5 Rendimiento y colisiones

- Mantener **pocos proyectiles activos**; objetivo inicial: máximo **6 elementos de ataque con colisión** simultáneos y el avatar.
- Usar un conjunto de posiciones/estructuras de datos o render Pen, evitando una tormenta de clones y scripts.
- Separar **hitbox lógica** de destellos y partículas; brillo no hace daño.
- Invulnerabilidad temporal y feedback claro: sonido, microparpadeo **limitado** y barra HP; no invocar flashes de pantalla completa repetidos.
- No avanzar ataques, física ni HP mientras `PAUSED`.
- En fase de `GLITCH_RESULT`, aplicar recompensa/castigo **una única vez** y limpiar todos los proyectiles.

---

## 9. DIRECCIÓN DE ANIMACIONES — requisito prioritario

**Objetivo del OWNER:** Nightmare debe tener **bastantes animaciones**, ser vistoso y conservar la rapidez/respuesta de NEXUS BLOCKS. El arte y animaciones de Nightmare pueden ser nuevos; los de los modos existentes permanecen iguales.

### 9.1 Lenguaje visual NIGHTMARE

- Identidad: **tecnología oscura, interferencias digitales, energía, alertas de emergencia**, no terror genérico ni referencias copiadas.
- Paleta candidata: fondo azul-negro ya existente; acentos violeta eléctrico, rojo de advertencia y cian para el núcleo. Colores por validar contra el tema actual.
- Elementos geométricos: rombos, retículas, segmentos de señal, fisuras digitales, anillos/pulsos abstractos.
- Señales redundantes: icono + texto + forma + color (no depender solo del rojo).
- **Legibilidad por encima del espectáculo:** animaciones nunca ocultan dónde caerá una pieza o qué casillas están ocupadas.

### 9.2 Catálogo de animaciones v1

| ID | Momento | Animación propuesta | Duración inicial | Criticidad |
|---|---|---|---|---|
| `AN-01` | Elegir Nightmare | **Intro:** título `NIGHTMARE`, borde del tablero encendiéndose por segmentos y transición elegante. | 0,8–1,2 s | Alta |
| `AN-02` | Iniciar juego | Pulso de activación breve desde el centro; contador `READY / GO`. | 0,5–0,8 s | Media |
| `AN-03` | Aviso de evento | Banda deslizante con nombre y cuenta atrás; **sin ocultar tablero**. | 0,25 s de entrada | Alta |
| `AN-04` | Double Garbage | Dos barras de energía desde abajo, vibración leve de borde y subida lógica sin ambigüedad. | 0,25–0,40 s | Alta |
| `AN-05` | Hold Jam inicia | Glitch local en panel HOLD + candado/ondas de interferencia + contador. | 0,25–0,35 s | Alta |
| `AN-06` | Hold Jam termina | Candado fracturado y retorno de brillo al panel. | 0,25–0,40 s | Media |
| `AN-07` | Garbage Debt comienza | Filas fantasma en lateral, medidor de deuda y contador de piezas. | 0,30 s entrada | Alta |
| `AN-08` | Cancelar deuda | Una barra de deuda se disuelve en partículas, texto `DEBT -1`. | 0,25–0,40 s | Alta |
| `AN-09` | Blindaje se desgasta | Fisuras SVG/Pen, pequeña lluvia de fragmentos, `ARMOR BREAK`. | 0,20–0,35 s | Alta |
| `AN-10` | Fila blindada se elimina | Desintegración metálica breve, distinta del borrado normal. | 0,25–0,40 s | Media |
| `AN-11` | Chaos Chain | Dos tarjetas conectadas, transición A→B, resaltado del evento activo. | 0,40–0,65 s | Alta |
| `AN-12` | Nueva oleada | Cortina diagonal de líneas digitales + `WAVE II / ...` + objetivos. | 0,9–1,2 s dentro de intermission | Alta |
| `AN-13` | Oleada superada | Onda de expansión y emblema de progreso; tablero visible al volver. | 0,5–0,8 s | Media |
| `AN-14` | Glitch Protocol entra | Tablero se atenúa **sin borrar su estado**, retícula de arena aparece con líneas ensamblándose, avatar se materializa. | 0,6–0,8 s | Alta |
| `AN-15` | Carga de láser | Línea de preaviso crece/brilla gradualmente y marcador auditivo corto. | 0,45–0,70 s | **Crítica: legibilidad** |
| `AN-16` | Láser disparado | Haz de energía más intenso, breve cola luminosa, sin tapar zonas seguras. | 0,20–0,30 s | Alta |
| `AN-17` | Core impactado | Pulso localizado, sacudida **del núcleo** y escudo de invulnerabilidad. | 0,20–0,35 s | Alta |
| `AN-18` | Core esquiva/sobrevive | Estelas discretas de movimiento, brillo final + `SURVIVED`. | 0,45–0,65 s | Media |
| `AN-19` | Core falla | Interferencia localizada, núcleo descompuesto en fragmentos + `FAILED`, sin Game Over automático. | 0,45–0,65 s | Alta |
| `AN-20` | Nightmare Core final | Entrada ceremonial de jefe abstracto: símbolo geométrico, contador de 3 etapas, transiciones de fase. | 0,8–1,2 s | Alta |
| `AN-21` | Trial Clear | Secuencia de victoria: bordes, símbolos de cinco oleadas, sello `TRIAL CLEARED`. | 1,2–1,8 s | Alta |
| `AN-22` | Game Over Nightmare | Desactivación de energía del tablero y resultado legible, sin retrasar controles de reinicio. | 0,6–0,9 s | Media |
| `AN-23` | HUD Nightmare | Pulso suave y esporádico de amenaza pendiente; contadores estables. | Bucle discreto | Media |
| `AN-24` | Menú Nightmare/Trials | Resaltado al escoger modalidad; **no alterar arte original de 1/2/3**. | 0,2–0,35 s | Media |

### 9.3 Estructura técnica recomendada de las animaciones

- Una **capa de presentación** que consume eventos (`EVT_GARBAGE_APPLIED`, `EVT_ARMOR_DAMAGED`, `EVT_WAVE_CLEAR`, `EVT_CORE_HIT`, etc.) sin modificar estado físico.
- Reutilizar SVG generados en Python y la extensión Pen. Crear disfraces extra únicamente cuando sean necesarios, evitar inflar el `.sb3`.
- Animaciones **no bloqueantes** para avisos/HUD/efectos de línea: interpolación dependiente del reloj lógico, sin esperas largas.
- Animaciones **bloqueantes solo en estados explícitos** (`INTRO_NIGHTMARE`, `TRIAL_INTERMISSION`, `GLITCH_INTRO`, `GLITCH_RESULT`, `TRIAL_CLEAR`), con tablero congelado.
- **No** usar el mismo timer para física y una intro de 0,8 s de modo que el juego “salte” al salir; conservar deadlines exactas.
- Nunca mezclar partículas con la lista canónica de celdas del tablero.
- Priorizar 3 niveles visuales: `LOW`, `STANDARD`, `HIGH` (posterior si existe UI viable). **El balance y hitboxes son idénticos** en todos los niveles; reducir partículas/decoración, no telegráficos esenciales.
- Introducir `reduced_motion` como futuro ajuste, o al menos evitar parpadeos bruscos y sacudidas intensas. **No usar flashes estroboscópicos**.

### 9.4 Presupuesto orientativo de rendimiento

Estos números son **objetivos de prueba**, no garantías:

- Priorizar una respuesta estable de teclado y física a 30 FPS o al ritmo real de Scratch, según plataforma.
- Evitar más de 6 ataques con hitbox concurrentes en Glitch Protocol y más de 8–12 partículas decorativas concurrentes en v1.
- Si el equipo cae de rendimiento, omitir partículas automáticamente; **nunca omitir avisos, hitboxes, estado del tablero o controles**.
- Evitar recalcular SVG, crear sonidos o reconstruir estructuras masivas cada frame; generar recursos de antemano en `tools/build_sb3.py`.
- Medir duración de frames/latencia en escritorio e iPad escolar si se dispone de acceso permitido; comparar antes/después.
- La sensación de «muchas animaciones» debe salir del **ritmo y la variedad** de transiciones cortas, no de llenar la pantalla de sprites.

### 9.5 Storyboard de ejemplo: entrada a GLITCH PROTOCOL

```text
[PLAYING_NIGHTMARE]
  Advertencia "CORE INSTABILITY" (visible; tablero todavía activo)
     ↓ (al llegar a un punto seguro)
  Estado GLITCH_INTRO: congela tablero y temporizadores
     0.00–0.20 s  oscurecer bordes, preservar tablero subyacente
     0.20–0.50 s  dibujar retícula digital en el centro
     0.50–0.80 s  crear rombo NEXUS CORE + indicador 3 HP
     ↓
  GLITCH_DODGE 5,00 s
     avisos claros → rayos → esquiva → impactos posibles
     ↓
  GLITCH_RESULT 0,65 s
     "SURVIVED" o "FAILED" + animación y saldo del premio/castigo
     ↓
  Volver al tablero: restaurar render y deadlines pendientes
     ↓
[PLAYING_NIGHTMARE]
```

---

## 10. Interacciones entre mecánicas — matriz inicial

| A | B | Permitido | Regla de arbitraje |
|---|---|---|---|
| Double Garbage | Garbage Debt | **Sí, diferido** | La deuda sigue activa; ataques físicos respetan capacidad/avisos. |
| Hold Jam | Garbage Debt | **Sí** | Combinación estratégica favorita de Chaos Chain. |
| Double Garbage | Hold Jam | **Sí, secuencial** | Double se resuelve, Hold se activa tras su propio aviso. |
| Double Garbage | Blindaje | **No simultáneo en piloto** | Primero comprobar modelo de blindaje y colisiones. |
| Garbage Debt | Otra deuda | **No en piloto** | Encolar hasta finalizar la anterior. |
| Chaos Chain | Otro Chaos Chain | **No** | Una cadena por vez. |
| Glitch Protocol | Cualquier evento físico | **Suspende, no borra** | Congelar tablero y deadlines; la recompensa se aplica antes de resolver el evento pendiente según política explícita. |
| Fin de oleada | Ataque pendiente | **Transición aplazada** | Terminar/cancelar explícitamente lo pendiente; nunca olvidar basura. |
| Pausa | Todo | **Sí** | Congelar absolutamente todos los temporizadores y animaciones jugables. |
| Reinicio | Todo | **Sí** | Restablecer estado canónico y limpiar colas/FX/escudos. |

### 10.1 Condiciones de no-secuestro de control

- Un aviso nuevo no debe bloquear giro/drop con una transición modal en mitad de una pieza.
- Si hay señal visual crítica, conservar la zona central del tablero legible.
- Durante microjuego, las flechas controlan **solo** al núcleo; no deben desplazar piezas ocultas.
- Al regresar, restablecer exactamente el control del tablero y los latches de teclado para evitar un hard drop/hold fantasma por tecla mantenida.
- Cada evento produce a lo sumo **una** penalización o recompensa por resolución.

---

## 11. Diseño de controles, menú y HUD

### 11.1 Menú

- Añadir opción **`4 — NIGHTMARE`** al menú existente sin cambiar los tres primeros modos.
- Tras seleccionar Nightmare, mostrar `ENDLESS` / `TRIALS` con controles simples y visibles; sugerencia: `1 — ENDLESS`, `2 — TRIALS`, `ENTER — START`, pero **evitar conflictos de estado con el selector global 1/2/3**: el mapeo contextual se decide durante implementación.
- Conservar la pantalla `GAME OVER` y la posibilidad de reiniciar; añadir `TRIAL CLEARED` para desafíos terminados.
- Mostrar permanentemente nombre de modo, fase y puntuación mientras se juega.

### 11.2 HUD Nightmare

Mostrar, sin ocultar ni reducir área jugable:

- `DEBT: X/2` o barra equivalente.
- `INCOMING: N` y tiempo/piezas hasta llegada de basura.
- `HOLD JAM: N` cuando corresponda.
- `CHAIN A/B` cuando esté en marcha una cadena.
- `WAVE I–V`, objetivo de piezas y progreso en Trials.
- `CORE HP` y aviso de ataque dentro del microjuego.

**Riesgo:** el escenario Scratch mide 480x360, y el HUD ya ocupa áreas laterales. Diseñar wireframe verificando **posiciones reales** antes de ampliar texto; preferir información contextual que sustituya avisos ya terminados, no todos los contadores permanentemente.

---

## 12. Arquitectura de implementación sugerida (sin ejecutar)

Principio: separar **configuración**, **lógica de eventos**, **temporizadores**, **reglas del tablero** y **render**, aunque todos terminen serializados como bloques Scratch por el generador.

### 12.1 Submódulos Python opcionales

El repositorio actualmente usa un generador único; extraer módulos no es obligatorio. **Si la complejidad lo justifica**, considerar:

```text
tools/
  build_sb3.py               # punto de entrada, fuente de orquestación
  nightmare/
    config.py                # parámetros/tipos/flags de modo
    events.py                # definiciones y prioridad de eventos
    trials.py                # datos de oleadas y objetivos
    core_survival.py         # patrones y hitboxes de esquiva
    animations.py            # SVG/guiones visuales del modo
  validate_sb3.py
  test_sb3.py
  test_runtime.cjs

docs/
  NIGHTMARE_DESIGN_SPEC.md   # presente documento tras revisión
  NIGHTMARE_TEST_PLAN.md     # opcional; derivado de QA de este documento
```

**Nota:** es estructura objetivo posible, no reflejo del árbol actual. Evitar "un archivo por función" y no renombrar componentes estables de forma innecesaria.

### 12.2 Estados/variables conceptuales (nombres tentativos)

```text
Game_Mode = NORMAL | HARD | CHAOS | NIGHTMARE
Nightmare_Submode = ENDLESS | TRIALS
Nightmare_Phase = ...
Nightmare_EventQueue = ...
Nightmare_PendingGarbage = 0..4
Nightmare_DebtLines = 0..2
Nightmare_DebtProgressLines = 0..4
Nightmare_DebtPiecesLeft = 0..12
Nightmare_HoldJamPiecesLeft = 0..7
Nightmare_ChainStage = 0..2
Nightmare_TrialWave = 1..5
Nightmare_WavePiecesLocked = ...
Nightmare_CoreHP = 0..3
Nightmare_CoreX / Nightmare_CoreY
Nightmare_CoreInvuln = ...
Nightmare_ActivePattern = ...
Nightmare_AnimState / Nightmare_AnimTime
Nightmare_RNGSeed = ... (QA)
```

No representar todos los estados como variables globales descoordinadas si se puede usar una disciplina de fase/contratos. Asegurar que Scratch ofrece límites y tipos adecuados.

### 12.3 Backwards compatibility

- No tocar la velocidad ni la tabla de puntuación de los modos existentes.
- No modificar geometría de piezas, rotaciones, wall kicks, comportamiento de Hold o reglas de colisión compartidas sin test que demuestre equivalencia.
- No sustituir los SFX originales ni la firma del creador; cualquier nuevo arte o sonido se añade de forma compatible.
- No eliminar controles para iPad con teclado físico; confirmar compatibilidad en editor oficial.
- No introducir persistencia remota o datos personales en el piloto.

---

## 13. Plan de implementación por fases, en rama nueva

**Estado actual:** solo documento. **Ningún cambio ni rama remota se crea por este archivo.**

### Fase 0 — preparación / baseline

1. Confirmar `main` actualizado; identificar SHA exacto de base; comprobar rama propuesta libre.
2. Crear `feat/nightmare-mode-v1` desde ese SHA.
3. Agregar este documento a `docs/NIGHTMARE_DESIGN_SPEC.md` (o ruta acordada) en la nueva rama.
4. Ejecutar baseline de construcción, validación y pruebas; guardar resultados y SHA de artefactos.
5. Definir feature flag `NIGHTMARE_ENABLED` que permita desactivar el modo sin afectar a 1–3.

### Fase 1 — armazón del cuarto modo

1. Menú selecciona Nightmare y submodo, sin modificar física de otros modos.
2. Máquina de estados, reloj lógico y sistema de avisos.
3. Pruebas de pausa/reinicio/contexto del teclado.
4. Intro Nightmare y alertas básicas (AN-01 a AN-03).

### Fase 2 — eventos base

1. Double Garbage + aviso y cancelación.
2. Hold Jam + bloqueo de C y contador.
3. Garbage Debt + progreso de líneas y vencimiento.
4. Sistema de colas y topes de amenaza, anticombinaciones imposibles.
5. Animaciones AN-04 a AN-08.

### Fase 3 — Chaos Chain y blindaje condicionado

1. Chaos Chain con 2 parejas compatibles.
2. Ensayar spike del blindaje; **si falla la semántica de filas completas, rediseñar antes de integrar**.
3. AN-09 a AN-11, más regresiones del tablero.

### Fase 4 — Nightmare Endless jugable

1. Calendario por etapas, pesos y cooldowns.
2. Puntaje y récord en sesión; pruebas largas de supervivencia.
3. Pruebas de 100+ eventos, reinicios y mezclas de amenazas.

### Fase 5 — Nightmare Trials

1. Cinco oleadas con objetivos y transiciones.
2. Conservación del tablero y resolución de amenazas pendientes.
3. AN-12, AN-13, AN-20, AN-21.

### Fase 6 — Glitch Protocol MVP

1. Arena y núcleo; controles y colisiones; pausa de tablero.
2. Tres patrones de rayo y zonas avisadas.
3. 3 HP, 5 s, premio/castigo y reanudación segura.
4. AN-14 a AN-19.
5. Agregar otros patrones solamente si calidad/rendimiento pasan.

### Fase 7 — pulido visual y optimización

1. Catálogo completo de animaciones, SFX originales, HUD, transiciones.
2. Reducir renders costosos, hacer pruebas en navegador/editor oficial.
3. Verificar fidelidad en teclado de iPad y escritorio, si hay acceso.

### Fase 8 — QA, revisión y lanzamiento

1. Ejecutar pipeline completo y pruebas de gameplay.
2. Comparar modos 1–3 con baseline; corregir regresiones.
3. Balance mediante partidas reales, incluyendo jugadores muy habilidosos.
4. Abrir PR con resultados y capturas/video; **no hacer merge automático** hasta revisión del OWNER.

**Para reducir riesgos:** dividir en PRs pequeños por fase o subrama, con tests de integración en la rama Nightmare. No mezclar el proyecto FOREX-NEXUS: este documento corresponde únicamente a `Dracalight/Blocks`.

---

## 14. Plan mínimo de pruebas y criterios de aceptación

### 14.1 Comandos del repositorio

```bash
python tools/build_sb3.py
python tools/validate_sb3.py
python tools/test_sb3.py
npm ci --ignore-scripts
npm test
```

Estos comandos están documentados en el README del repositorio; no se han ejecutado durante la redacción de esta especificación.

### 14.2 Pruebas automatizadas / semiautomatizadas a crear

| ID | Escenario | Criterio de aceptación |
|---|---|---|
| `QA-MENU-01` | Opciones 1–4; selección de Endless/Trials | No cambia la selección ni los controles de modos 1–3. |
| `QA-PHYS-01` | Caída a alta dificultad | Nunca < 0,07 s/fila según configuración y deadlines. |
| `QA-DG-01` | Double Garbage con/sin cancelación | 0/1/2 filas correctas, sin celdas duplicadas. |
| `QA-DG-02` | Garbage de dos filas con pieza activa | Reubicación/top-out correcto y sin atravesar celdas. |
| `QA-HJ-01` | Hold Jam durante 7 bloqueos | C deshabilitada exactamente; Hold previo conservado. |
| `QA-HJ-02` | Hold Jam + pausa + reinicio | Contadores conservados al pausar y limpiados al reiniciar. |
| `QA-DEBT-01` | Limpiar 0/1/2/3/4 líneas antes de 12 piezas | Deuda convertida/cancelada correctamente sin dobles cómputos. |
| `QA-QUEUE-01` | 4 filas pendientes y nuevo evento | No superar límite; evento diferido/condicionado de modo visible. |
| `QA-CHAIN-01` | Hold Jam → Garbage Debt | Subfases anunciadas, no superpuestas accidentalmente. |
| `QA-ARMOR-01` | Desgastar fila completa blindada | Estado coherente; ausencia de callejón sin salida. |
| `QA-ARMOR-02` | Dos filas completas, solo una blindada | Orden de compactación/puntuación correcto. |
| `QA-TRIAL-01` | Pasar oleada con ataques pendientes | Ningún ataque desaparece en silencio; transición finita. |
| `QA-TRIAL-02` | Completar quinta oleada | `TRIAL CLEARED` solo una vez; registro correcto. |
| `QA-CORE-01` | Esquiva y colisiones | HP 3→0, invulnerabilidad 0,45 s, sin impactos duplicados. |
| `QA-CORE-02` | Salir de esquiva | Gravedad/deadlines y teclas vuelven sin saltos ni acciones fantasma. |
| `QA-CORE-03` | Pausar durante rayos | Congela patrones y movimiento; no daño durante pausa. |
| `QA-CORE-04` | Recompensa/penalización | Resultado único, cap de garbage y aviso de castigo. |
| `QA-ANIM-01` | Efectos intensivos y reinicios | Sin objetos residuales, colisiones visuales ni bloqueo de entrada. |
| `QA-REG-01` | Normal/Hard/Chaos | Física, menús, scoring, HUD y SFX equivalentes al baseline. |
| `QA-ROT-T-01` | T en giros rápidos y T-spin doubles legales | Exactamente 4 minos fijados; solo líneas válidas eliminadas. |

### 14.3 Pruebas manuales imprescindibles

- Jugar 15–30 min con animaciones activadas, tanto en Nightmare como en modos originales; si el rendimiento lo impide, registrar bloqueo y redimensionar efectos.
- Probar los casos extremos: top-out, Hold atascado, 4 filas pendientes, aviso que vence durante una limpieza, reinicio en mitad de Glitch Protocol, pausa durante rayos.
- Verificar lectura del HUD en pantalla 480x360 y pantalla de iPad con teclado físico.
- Comprobar con jugadores reales que los patrones de rayos son esquivables incluso con latencia real de Scratch.
- Comparar partidas Nightmare con semilla fija para asegurar reproducción.
- Confirmar que ninguna animación es necesaria para saber el estado (avisos textuales/indicadores siempre disponibles) y que no hay parpadeos molestos.

### 14.4 Condiciones de no-go

**No integrar ni publicar Nightmare** si se detecta cualquiera de estos bloqueos:

- Modos existentes regresionan o pierden controles.
- Una amenaza de garbage supera límites sin aviso, o se aplica dos veces.
- La pieza activa puede atravesar celdas o una fila blindada queda permanentemente irresoluble.
- Pausa/retorno desde microjuego consume tiempo de gravedad o causa hard drops no solicitados.
- Existe algún patrón de esquiva sin trayecto seguro físicamente alcanzable.
- Animaciones vuelven injugable la entrada o ocultan avisos críticos.
- El `.sb3` deja de cargar o de reconstruirse reproduciblemente.

---

## 15. Decisiones de producto pendientes (no bloquear el primer prototipo)

1. Definir si Nightmare Trials aparece en un submenú o como opción secundaria desde la pantalla Nightmare.
2. Elegir estética exacta de la paleta (violeta/rojo/cian), tipografías y SFX.
3. Confirmar si el microjuego se activa cada ~45 s o exclusivamente en hitos de oleada durante v1.
4. Elegir formalmente la semántica de bloques blindados tras el spike de QA: desgaste de fila o diseño alternativo.
5. Establecer el indicador de récord de modo Nightmare y el formato de capturas.
6. Añadir o no un ajuste de intensidad visual/reduced motion.
7. Definir logros y Trials+ como un trabajo separado, después del MVP.

**Valor por defecto:** usar las reglas v0.1 como hipótesis de balance; el agente debe señalar desviaciones propuestas antes de cambiarlas y adjuntar evidencia de pruebas.

---

## 16. Orden de trabajo reutilizable para CODEX / agente implementador

> **OWNER — NEXUS BLOCKS / NIGHTMARE**  
> Repositorio: `Dracalight/Blocks`. Crear una rama nueva desde el `main` vigente, nombre sugerido `feat/nightmare-mode-v1` (si está libre), con SHA base documentado.  
> Leer en primer lugar `README.md`, `docs/ARCHITECTURE.md`, `docs/CONTROLS.md`, `docs/TESTS.md`, `tools/build_sb3.py`, `tools/validate_sb3.py`, `tools/test_sb3.py` y este documento.  
> **Objetivo:** desarrollar incrementalmente el modo NIGHTMARE para NEXUS BLOCKS con eventos Double Garbage, Hold Jam, Garbage Debt, Chaos Chain, presiones y bloques blindados condicionados a QA; añadir Nightmare Endless, Nightmare Trials por oleadas y Glitch Protocol con núcleo energético que esquiva rayos. Incorporar un catálogo amplio de animaciones propias, legibles y eficientes.  
> **Restricciones:** no modificar el comportamiento de Normal/Hard/Chaos; no aumentar la gravedad máxima por encima de la dificultad actual (intervalo mínimo 0,07 s/fila); preservar arquitectura Scratch 3 nativa y fuente de verdad `tools/build_sb3.py`; no copiar propiedad intelectual visual/musical de otros videojuegos.  
> **Método:** implementar por fases pequeñas, con estado y timers explícitos, avisos claros, límites de amenaza, pruebas de regresión y rendimiento. Registrar diferencias respecto a la especificación cuando el prototipo revele problemas, especialmente en blindaje. Mantener el `.sb3` generado coherente con el código.  
> **Entrega:** commits y PR en rama aislada, pruebas reproducibles, capturas o grabación de gameplay cuando sea posible, explicación de restricciones de Scratch y lista de pendientes. **No realizar merge a `main` sin revisión y autorización del OWNER.**

---

## 17. Referencias internas y criterio de procedencia

- Repositorio: <https://github.com/Dracalight/Blocks>
- Arquitectura: <https://github.com/Dracalight/Blocks/blob/main/docs/ARCHITECTURE.md>
- README: <https://github.com/Dracalight/Blocks/blob/main/README.md>
- Generador: <https://github.com/Dracalight/Blocks/blob/main/tools/build_sb3.py>
- Estas fuentes se consultaron en modo **solo lectura**. Los demás nombres, cifras, eventos y composiciones son **propuestas de diseño derivadas de la conversación con el OWNER**, no funciones verificadas ni cambios ya publicados.

**Fin de la especificación v0.1.**
