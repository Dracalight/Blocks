# 01 · Estado consolidado, sin inventar progreso

## Problema principal

El generador estratégico actual emite eventos direccionales confirmados. Eso deja fuera observaciones M15 con evidencia direccional parcial. Se busca **investigar si existe información útil en esos casos**, sin convertir cada vela en una orden ni alterar la población de meta-labeling del baseline.

## Resultado de la síntesis R3

- **Recomendación conceptual:** `HYBRID_WITH_DISCOVERY`.
- **Frecuencia inicial:** una evaluación por vela M15 **válida y disponible**; no decisiones intravela.
- **Evaluación:** vector de evidencia por familia, score continuo (no probabilidad), incertidumbre y abstención diferenciadas.
- **Baseline:** conservar eventos estructurales de ruptura, identidad y semántica históricas.
- **Discovery:** selección **offline, causal y versionada** de episodios débiles; jamás enviarlos al B operativo como si fueran eventos ya aprobados.
- **Regímenes:** contexto probabilístico GMM/HMM lateral, opcional, point-in-time; filtrado HMM forward-only.
- **Dataset prospectivo:** separar observaciones, evaluaciones, evidencia, eventos, candidatos exploratorios, regímenes, labels y decisiones.
- **Estrategias:** ruptura baseline; investigar primero fallos de ruptura/reentrada; pullback como hipótesis opcional. Ninguna tiene rentabilidad demostrada en la propuesta.

## Estados heredados, no reescribir como PASS

| Tema | Estado inicial para este cuaderno | Qué falta |
|---|---|---|
| Dirección arquitectónica | Propuesta R3 lista para deliberación OWNER | D01–D10 y revisión independiente |
| Código vigente de A | Inspección histórica parcial | Reconciliar con últimos commits |
| Interfaz efectiva de B | No acreditada | Leer productor/consumidor/validadores actuales |
| Dataset y contratos C1–C5 | Compatibilidad conceptual, NO demostrada | Reconciliación documental y de claves |
| Unión de GMM/HMM a evaluaciones por vela | No resuelta | Contrato nuevo sin romper unión por evento |
| Selector Discovery | Concepto aceptable, reglas sin congelar | Definición causal, IDs, episodios, solapamiento |
| Validación económica | No realizada / no autorizada | Prerregistro, entorno y permisos futuros |
| Implementación | NOT_AUTHORIZED | Decisión expresa posterior |
| Trading LIVE | NO AUTORIZADO | Fuera de alcance |

**No confundir** “se escribió un plan” con “se probó”, “se aceptó” o “se autorizó”.

## Acuerdos para la conversación desde el iPad

- No modificar la estrategia original de ruptura.
- No cambiar la temporalidad a M1 porque haya datos M1 o ticks.
- No asumir que más candidatos implican mayor alpha.
- No mezclar labels de poblaciones heterogéneas.
- No confundir NEUTRAL (evidencia direccional no material) con ABSTAIN (decisión suspendida por conflicto/incertidumbre).
- No ajustar pesos, sesiones ni umbrales después de observar outcomes del conjunto que se pretende evaluar.
- No prometer que GMM/HMM aportan valor si aún no fueron validados.

**Primera tarea concreta:** elegir las políticas provisionales de D01, D02 y D04 en el archivo 02. El resto del dossier ya explica las alternativas.
