# 02 · Cuaderno de decisiones OWNER — D01 a D10

Cada elección aquí es una **decisión de diseño**, no autorización de implementación. Estado posible: `PROPOSED`, `OWNER_SELECTED`, `BLOCKED`, `VERIFIED`. Mantener fecha y razonamiento. No marcar VERIFIED sin evidencia técnica.

## Vista ejecutiva

| ID | Cuestión | Opción provisional recomendada | Estado inicial |
|---|---|---|---|
| D01 | Arquitectura A | M15 continuo + eventos confirmados + Discovery offline | PROPOSED |
| D02 | Frecuencia | Cierre de M15 válido; publicar tras disponibilidad real | PROPOSED |
| D03 | Evidencia y dirección | Vector por familia; global opcional; score 1–5 solo visual | PROPOSED |
| D04 | Débiles | Episodios causales offline; sin puerta directa al B operativo | PROPOSED |
| D05 | Familias | Breakout baseline; failed breakout prioritario; pullback condicional | PROPOSED |
| D06 | GMM/HMM | Features laterales opcionales, NO alterar A | PROPOSED |
| D07 | Conexión A→B | Eventos históricos a B original; evaluación y Discovery separados | BLOCKED |
| D08 | Dataset | Capas distintas, tiempo disponible y linaje inmutable | PROPOSED |
| D09 | Migración | Extensión aditiva y versionada, sin tocar historial | BLOCKED |
| D10 | Ejecución | Contratos → fixtures → pruebas → experimental offline → revisión | PROPOSED |

## D01 — Arquitectura

**A)** Solo eventos confirmados. **B)** Evaluación por toda M15 enviada directamente a B. **C)** Evaluación continua + eventos originales, sin Discovery etiquetado. **D)** Evaluación + eventos + Discovery offline sobre episodios.

**Recomendación:** D; C como fallback. Beneficio esperado: estudiar débiles sin reentrenar implícitamente el B actual. Coste: nuevo selector, nuevas identidades y validación.

**OWNER elige:** PENDIENTE  
**Motivo:** ...  
**Qué demostraría que se equivoca:** ...

## D02 — Calendario de A

**Recomendación:** vela M15 cerrada, con precios y watermark realmente disponibles; una evaluación válida por barra/versión, no una orden. En gaps/no readiness registrar causa; reintentos idempotentes; cierre nominal no equivale a disponibilidad instantánea.

**OWNER elige:** PENDIENTE  
**Sesiones/símbolos a investigar:** ...  
**Caducidad y late arrivals:** ...

## D03 — Score y contradicciones

**Recomendación:** conservar por familia evidencia alcista y bajista simultánea, con estados, motivos y calidad. Global BUY/SELL/NEUTRAL solo con política preregistrada. Si hay conflicto no resuelto, `ABSTAIN/UNRESOLVED`, no NEUTRAL. 1–5 es UI derivada del score continuo, NO calibración de acierto.

**OWNER elige:** PENDIENTE  
**Qué evidencia no debemos colapsar:** ...  
**Política de conflicto que requiere investigación:** ...

## D04 — Descubrimiento débil

**Recomendación:** seleccionar episodios offline con reglas causales congeladas antes de labels; sin acceso al B operativo. Registrar también no seleccionados para medir cobertura y sesgo.

**OWNER elige:** PENDIENTE  
**Unidad de análisis:** episodio / barra / otra: ...  
**Principal sesgo a prevenir:** ...

## D05 — Estrategias

**Recomendación:** baseline ruptura + primera candidata `failed breakout + reentry`; evaluar pullback solo tras demostrar diversidad. Mantener mean reversion y compression como hipótesis pospuestas; no adoptar muchas familias a la vez.

**OWNER elige:** PENDIENTE  
**Primera familia complementaria:** ...  
**Qué la falsaría:** ...

## D06 — Regímenes

**Recomendación:** GMM/HMM inicialmente laterales para consumidor experimental; sin controles de A por régimen. HMM filtrado forward-only; snapshots, fit y publicación anteriores al consumo; ausencias explícitas.

**OWNER elige:** PENDIENTE  
**Condición de futura revisión:** ...

## D07 — Contrato B (BLOQUEADO)

Se conoce un adaptador histórico que acepta eventos tipados; no se ha demostrado compatibilidad con evaluaciones por vela. No crear puente por coerción de tipos. B experimental necesitaría contrato/labels/calibración distintos.

**OWNER elige política objetivo:** PENDIENTE  
**Aprobación técnica:** BLOCKED hasta reconciliar código productor-consumidor actual  
**Preguntas al auditor:** ¿qué recibe B realmente? ¿qué validaciones exige? ¿qué estados rechaza?

## D08 — Dataset

**Recomendación:** modelo lógico de entidades separadas, identidades estables, hash de fuente, reloj de disponibilidad, particiones y linaje. Features point-in-time; labels futuros siempre aislados.

**OWNER elige:** PENDIENTE  
**Entidad que NO debe mezclarse:** ...

## D09 — Compatibilidad/migración (BLOQUEADO)

**Recomendación:** extensión aditiva, namespace de versiones nuevo; preservar IDs y baseline. El diseño anterior de uniones laterales por ID de evento no cubre evaluaciones sin evento.

**OWNER elige política objetivo:** PENDIENTE  
**Aprobación técnica:** BLOCKED hasta cotejar los contratos posteriores y pruebas adversariales.

## D10 — Orden

**Recomendación:** 1. revisión de contratos; 2. esquema+oráculos; 3. ensayos sintéticos; 4. motor de evaluación aislado; 5. selector offline; 6. validación económica con permiso independiente; 7. decisión posterior de integración B. El orden solo habilita trabajo cuando el OWNER lo autorice.

**OWNER elige:** PENDIENTE  
**Primer lote que autorizaría en el futuro:** ...  
**Gates imprescindibles:** ...

---

## Registro resumido de selecciones

| Fecha | ID | Elección OWNER | Justificación | Evidencia pendiente | Próxima acción |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

**Pregunta que más importa:** ¿queremos que A encuentre más *observaciones informativas*, más *hipótesis de episodios*, o más *candidatos elegibles*? Son objetivos distintos y deben medirse con denominadores distintos.
