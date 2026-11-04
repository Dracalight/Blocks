# 09 · Plan cuando regreses y prompt para continuar

## Orden preciso, sin nueva investigación general

**P0 — Reconciliar contratos y procedencia en fuente PRIVADA.** Traer últimos commits y auditorías; verificar realmente la entrada de B, versiones de A, claves de Dataset y GMM/HMM. Resolver los bloqueos de D07/D09. Este trabajo NO se realiza publicando el código en esta rama.

**P1 — Cerrar las decisiones OWNER D01–D10.** Convertir `PROPOSED` en `OWNER_SELECTED` solo cuando se elija y se documenten argumentos. Esta aprobación no concede permisos de implementación.

**P2 — Especificar contratos prospectivos privados.** MarketAssessment, FamilyEvidence, ResearchEpisode y join observation/snapshot. Definir selector, tiempos, IDs, cambios de versión, caducidad y casos límite.

**P3 — Revisar independientemente** las especificaciones y fixtures T01–T16, especialmente causalidad, compatibilidad con baseline y fronteras del B operativo.

**P4 — Solicitar autorización nueva para implementación experimental** (solo si P0–P3 pasan). No construir Dataset A ni entrenar modelos hasta protocolos y permisos propios.

## Prompt listo para una futura sesión (copiar, sin publicar fuentes privadas aquí)

> Continúa el rediseño de Agent A Next desde mi cuaderno público de decisiones en la rama `research/school-decision-workspace-20261105` de `Dracalight/Blocks`. Lee `README.md`, `docs/02_DECISIONES_OWNER.md` y `docs/08_BITACORA_IPAD.md` y utiliza las decisiones OWNER allí registradas. La rama contiene solo documentación sanitizada y **no es** el repositorio de código. Usa una conexión autenticada al repositorio técnico privado para reconciliar contrato efectivo de Agent B, Dataset A y GMM/HMM; no copies contenidos privados a Blocks. El diseño provisional es híbrido M15 con evaluación continua, eventos confirmados preservados y Discovery offline sobre episodios; score continuo por familia, NEUTRAL separado de ABSTAIN, HMM forward-only, GMM/HMM laterales. Los gates D07/D09 están pendientes y la implementación NO está autorizada. Haz solo cierre documental y propuesta de contratos, con SHA y evidencia de cualquier fuente privada revisada. Si no tienes acceso al repositorio privado, marca únicamente ese punto bloqueado; no reconstruyas como hecho código no inspeccionado.

## Resultado que debería volver contigo a casa

- Un cuaderno con decisiones seleccionadas y justificadas.
- Una lista corta de asuntos técnicos que necesitan un checkout autenticado.
- Una matriz de riesgos y pruebas que otro auditor pueda ejecutar después.
- Nada fusionado a `main`, ningún cambio al juego ni a trading.

**Si se necesita compartir resultados sensibles:** hacerlo únicamente en el repositorio privado o en un archivo/adjunto privado; este cuaderno público no es el lugar.
