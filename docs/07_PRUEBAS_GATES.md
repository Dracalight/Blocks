# 07 · Matriz de pruebas y decisiones de admisión

**Estado actual de todas las pruebas nuevas: PLANNED — NOT RUN.** No convertirlas en PASS sin ejecución y evidencia.

## Casos sintéticos obligatorios

| ID | Prueba | Criterio PASS | FAIL |
|---|---|---|---|
| T01 | Replay idéntico | bytes/semántica/IDs deterministas con mismo prefijo/config | cambia salida |
| T02 | Extensión futura | añadir velas futuras no cambia evaluaciones/eventos históricos | cambia prefijo histórico |
| T03 | Mutar futuro | reemplazar datos tras t no altera decisión en t | leakage |
| T04 | Disponibilidad | input `available_at > decision_at` se rechaza | se utiliza |
| T05 | Cierre / warmup | velas inválidas/no listas no reciben score direccional válido | NEUTRAL falso |
| T06 | Retry idempotente | mismo ID+payload es no-op; mismo ID+payload distinto conflicto | sobrescritura |
| T07 | Reinicio/segmento | replay íntegro y fragmentado son equivalentes | divergencia no explicada |
| T08 | Episodios | una formación persistente no crea múltiples independientes por vela | duplicación |
| T09 | Baseline | ids/semántica de eventos confirmados permanecen intactos | regresión legado |
| T10 | B frontera | B operativo rechaza `MarketAssessment`/Discovery sin contrato nuevo | coerción silenciosa |
| T11 | Regímenes | salida GMM/HMM late, missing, NOT_PIT excluida causalmente | consumo retroactivo |
| T12 | HMM | smoothing prohibido y checkpoint incompatible bloqueado | retrospectiva o mezcla de estados |
| T13 | Join | unir por keys y versión, nunca posición de fila | asociación falsa |
| T14 | Outcomes | no hay labels, PnL, TP/SL futuros en features de A | contaminación |
| T15 | Conflicto | evidencia BUY+SELL contradictoria conserva ejes o se abstiene | NEUTRAL silencioso |
| T16 | Universo | registrar seleccionados y no seleccionados, denominadores y exclusiones | sesgo no medible |

## Gates futuros

**G0 — Revisión documental:** decisiones OWNER, bibliografía, fuentes de código actuales y límites claramente separados.

**G1 — Contrato:** esquemas y política exacta de reloj, identidad, estados, versión, claves y disponibilidad revisados independientemente.

**G2 — Fixtures:** pruebas T01–T16 causales en laboratorio sintético aislado con oráculos independientes, sin datos protegidos.

**G3 — Implementación experimental:** autorización separada de OWNER para construir una versión aislada; preserva baseline.

**G4 — Experimentos económicos:** otra autorización explícita, preregistro de familias, parámetros, universo, labels, costes, selección y ventanas. Walk-forward temporal y purga/embargo ante solapamiento, controles negativos y múltiples pruebas.

**G5 — Integración B/operación:** revisión independiente y autorización distinta; prohibido LIVE por defecto.

**Estados posibles:** PLANNED, BLOCKED_ENV, FAIL, PASS_WITH_EVIDENCE. Ningún informe por sí solo implica permiso para subir de gate.

## Registro de resultado (copiar para cada prueba real)

```text
Test ID:
Código SHA / archivo:
Fixture y versión:
Entorno:
Comando exacto:
Salida:
Criterio observado:
PASS/FAIL/BLOCKED:
Evidencia SHA/link:
Limitaciones:
Revisor independiente:
```
