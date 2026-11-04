# 03 · Contratos prospectivos: modelo lógico de Agent A Next

**No es un esquema vigente ni código.** Especificación para revisar desde el iPad.

```text
MarketObservation(M15 closed, PIT, calidad)
      │
      ▼
MarketAssessment(evidencia por familia + calidad + incertidumbre)
      ├────► ConfirmedEvent (baseline legado, sin alterar IDs)
      └────► ResearchEpisodeSelector (offline, solo prefijos)
                       │
                       ▼
                DiscoveryEpisode
                       │
                       ▼
                 labels futuros en almacén separado
ConfirmedEvent ────────► B existente, tras verificación contractual
DiscoveryEpisode ──────► B experimental OFFLINE, nunca automático
Observation ───────────► GMM / HMM snapshots laterales, cuando autorizados
```

## Entidades y granos

| Entidad | Grano | Identidad conceptual | Contrato mínimo |
|---|---|---|---|
| MarketObservation | Fuente + símbolo + vela M15 | hash de stream, tiempo y versión | OHLC/base, origen, available_at, calidad, segmento, procedencia |
| MarketAssessment | Observación + versión A | hash distinto de evento | estado, scores por familia, incertidumbre, decision_at, input-prefix hash |
| FamilyEvidence | Evaluación + familia + versión | clave estable por familia | b, s, razones, disponibilidad, configuración, ready |
| ConfirmedEvent | Evento estratégico histórico | **preservar identity original** | lado, episodio y condiciones existentes |
| DiscoveryEpisode | Selector + inicio causal + lado + versión | namespace propio, NO event_id legado | inicio, expiry, reason, selector_sha, exclusiones |
| RegimeFeature | Observación + modelo/snapshot + política | snapshot y reloj PIT | probabilidades, estado READY/MISSING/LATE/NOT_PIT |
| Label | Candidato + experimento | namespace de labels separado | horizonte, barreras, tiempo de resolución, outcome posterior |
| BDecision | Modelo B + población + candidato | namespace por población | aceptado/rechazado, versión, razones, timestamp |

**Reglas:** un mismo ID y payload distinto -> ERROR/CONFLICTO; no sobrescribir. Ninguna entidad de A recibe resultados económicos futuros. De un `MarketAssessment` **no se deriva automáticamente** un evento negociable. Las relaciones son por ID, nunca por orden de fila.

## Semántica de estados

- `INVALID`: integridad o invariantes incumplidos; no interpretar como una dirección.
- `NOT_READY`: fuente válida pero falta warmup o contexto; no inferir score cero.
- `NEUTRAL`: evaluación válida con evidencia direccional no material, según política fijada.
- `ABSTAIN/UNRESOLVED`: existe evidencia pero no se decide por incertidumbre/conflicto o política ausente.
- `CANDIDATE_CONFIRMED`: estrategia estructural cumple la condición tipada y causal.
- `DISCOVERY_SELECTED`: episodio investigable; **no es señal operativa**.
- `B_REJECT`: rechazo posterior sobre una propuesta elegible; no es una clase de mercado.
- `MISSING_REGIME`: ausencia de feature lateral, sin destruir una evaluación válida.

## Tiempos

`bar_open_at < bar_close_at <= available_at <= decision_at`; los datos usados por decisión deben tener `input_available_at <= decision_at`. No inventar tiempos de recepción a partir de OHLC. Datos BID/ASK más frecuentes pueden almacenarse para realismo, pero no cambian la frecuencia de decisiones M15.

## Asuntos abiertos para OWNER

1. ¿Política por contradicción BUY vs SELL? Mantener ambos componentes hasta decidir; no promediar scores no comparables.
2. ¿Se emite evaluación en warmup? Puede conservarse un registro técnico con `NOT_READY`, sin score válido.
3. ¿Cuántos eventos de familias por misma vela? Especificar identidad por familia y manejo de simultaneidad.
4. ¿Cómo se enlaza contexto GMM/HMM a observación sin romper join legado por evento?
5. ¿Qué parte del lifecycle de episodio queda inmutable y cuál es nueva y versionada?

**Criterio de revisión:** cualquier campo propuesto debe justificar temporalidad, procedencia, consumidor, validez, identidad y función de falsación.
