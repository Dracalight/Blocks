# 06 · Dataset, B, GMM y HMM — reconciliación necesaria

## Límite fundamental

Las evaluaciones M15 y los eventos confirmados son **poblaciones distintas**. Un consumidor B con contrato de eventos no debe aceptar una evaluación por coerción o renombrado. La vía exploratoria requiere dataset, target y calibración propios, fuera de producción.

## Diseño por capas

1. `MarketObservation` — observación y disponibilidad causal.
2. `MarketAssessment` — resultado de A por vela válida.
3. `FamilyEvidence` — evidencia por hipótesis y versión.
4. `ConfirmedEvent` — conservar IDs y semántica históricos.
5. `DiscoveryEpisode` — candidato offline investigativo (si se aprueba D04).
6. `RegimeFeature` — salida lateral PIT de snapshot GMM/HMM.
7. `OutcomeLabel` — separado, calculado SOLO después y para población/experimento exactos.
8. `BDecision/RiskDecision` — namespaces separados; no hay órdenes en este diseño.

Un timestamp nominal de cierre no prueba que el dato estuviera disponible. Registrar `event_at`, `available_at`, `decision_at`, `recorded_at` y la procedencia.

## Bloqueo de claves

Una interfaz lateral histórica de referencia para GMM/HMM une por **`(event_id, event_scope_sha256)`**. Una evaluación universal M15 no tiene necesariamente `event_id`. No puede reutilizarse esa unión para todas las velas.

**Solución para investigar, NO aprobar aún:** nueva interfaz de régimen indexada por `observation_id` + `snapshot_id` + política temporal; adaptador versionado de observación a contexto, manteniendo la unión histórica sin cambios. Evaluar cardinalidad, snapshots múltiples, identidad de segmento, late delivery, missing feature y rollback.

## GMM

Snapshot immutable; `trained_through` y fit de preprocessing anteriores a publicación y uso. Transformaciones del conjunto completo introducirían leakage. Clusters son números de componentes probabilísticos, no estados económicos verdaderos.

## HMM

Utilizar únicamente filtrado `forward-only` para features LIVE-compatible; prohibir estados suavizados retrospectivamente. `checkpoint` ligado a versión de modelo, prefijo y segmento; gap o cambio incompatible exige reset explícito. Si llega tarde, `LATE`/no elegible, no viajar al pasado.

## Auditoría de B (pendiente)

Reconstruir usando fuente accesible y SHA exactos:
- Entradas efectivas de B, tipos, schema, `event_id`, dirección, timestamps.
- Clasificación de NEUTRAL / INVALID / timeout.
- Reglas que determinan si hay inferencia y autorización.
- Fronteras con risk/execution.
- Historial de modelos y calibración bajo población de eventos.
- Posible vía experimental, pero sin reutilizar calibración existente.

## Compatibilidad con Dataset

No declarar que el diseño es compatible con contratos congelados solo porque el diagrama parezca coherente. Verificar claves, población, identidad, linaje, estados, clock semantics, idempotencia y C1–C5. Problemas documentales de versiones previas deben cerrarse por sus procesos independientes; este cuaderno NO los cierra.
