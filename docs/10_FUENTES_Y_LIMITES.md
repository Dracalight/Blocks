# 10 · Procedencia y seguridad

## De dónde sale este cuaderno

Síntesis redactada a partir de la decisión arquitectura R3 aportada por OWNER en un artefacto de conversación y de la discusión previa. Se usan aquí **ideas abstractas**; este árbol no incluye las fuentes completas, código interno, informes originales ni identificadores privados del repositorio técnico.

Los informes originales de una ronda R2 anterior se reportaron no recuperables. Un paquete posterior R3 enumeró diez documentos y recomendó `HYBRID_WITH_DISCOVERY`, con auditoría de código parcial. Se resumieron conceptos de evaluación continua, baseline, Discovery offline, GMM/HMM y Dataset. **No constituye auditoría científica independiente.**

## Estados que no pueden prometerse

- `SOURCE_AUDIT`: PARTIAL en el paquete R3.
- `DESIGN_DECISION_READINESS`: READY_FOR_OWNER_REVIEW (documentación).
- `DATASET_A_DESIGN_COMPATIBILITY`: PROSPECTIVE_DESIGN_READY (conceptual, no probado).
- `IMPLEMENTATION_AUTHORIZATION`: NOT_AUTHORIZED.
- `RESEARCH_RESULTS`: NO SE INCLUYEN ENSAYOS ECONÓMICOS.
- `PUBLICATION_SCOPE`: este branch, archivos Markdown sanitizados solamente.

La verificación futura debe ocurrir en el sistema autorizado. Fechas, SHA y resultados de auditoría de código se mantienen en el repositorio privado; evita copiarlos aquí.

## Política de seguridad para un repo público

**NO PUBLICAR:** ficheros de la escuela, fotos privadas, contraseñas/API keys/tokens, nombres de personas, balances, órdenes, datos personales, documentos de trabajo privados, ZIP científico íntegro, datos RAW/CAL/holdout, path a secretos, modelos ni observaciones de cuenta.

**SÍ PUBLICAR:** preguntas metodológicas abstractas, comparaciones de arquitectura sin información propietaria, casillas de decisión, criterios de pruebas sintéticas sin datos reales y notas generales sin identificadores personales.

## Calidad de evidencia

- `OBSERVED`: lectura real de código/documento o prueba reproducible, con fecha y evidencia conservada en entorno apropiado.
- `REPORTED`: resultado descrito por otro agente sin reproducción propia.
- `PROPOSED`: política o diseño aún no aprobado.
- `NOT_RUN`: prueba nunca ejecutada.
- `BLOCKED`: falta condición necesaria o autorización.
- `OWNER_SELECTED`: elección de diseño, no prueba estadística.

## Nota sobre el árbol Git

El árbol actual de esta rama se creó **desde cero**, por lo que solo contiene los documentos Markdown listados. La historia del commit desciende de `main` por compatibilidad con las herramientas de GitHub: no deducir que el historial previo haya sido borrado; no fusionar esta rama con la de desarrollo del juego.

## Para referencias técnicas

Consultar la fuente privada con permisos autorizados; no pegar contenido en issues/PR públicos. Priorizar fuente exacta, versión, line numbers y hashes verificados allí. La bibliografía futura debe marcar qué evidencia es aplicable a FX M15 y qué es extrapolación de otros horizontes.
