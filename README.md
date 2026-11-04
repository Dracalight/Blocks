# Cuaderno de investigación — Agent A Next | iPad

**Rama documental independiente · 2026-11-05 · Solo investigación y decisiones**

Esta rama contiene **exclusivamente archivos Markdown**: no hay juego, proyectos Scratch, código, builds, recursos de NEXUS BLOCKS ni datos reales de trading en su árbol actual.

> **Aviso de privacidad:** este repositorio es PÚBLICO. Este cuaderno contiene únicamente una síntesis genérica y sanitizada de decisiones arquitectónicas. No añadir código, informes internos, SHA privados, contratos completos, datos, credenciales, resultados de entrenamiento ni material personal. El proyecto técnico original permanece fuera de esta rama.

## Empieza desde el iPad

**Si solo tienes 15 minutos:** abre [02 — Decisiones D01–D10](docs/02_DECISIONES_OWNER.md), revisa D01, D02 y D04, escribe tu elección y registra el progreso en [08 — Bitácora](docs/08_BITACORA_IPAD.md). Todo puede hacerse con Markdown en GitHub; no necesitas ejecutar código.

**Si tienes tiempo para investigar:** lee [03 — Modelo conceptual](docs/03_MODELO_CONCEPTUAL.md) y [04 — Selector de episodios débiles](docs/04_DISCOVERY_OFFLINE.md). Estas son las decisiones más importantes que todavía no están formalizadas.

**Cuando vuelvas a casa:** sigue [09 — Plan de regreso](docs/09_PLAN_DE_REGRESO.md) para contrastar con fuentes privadas antes de implementar. **No fusionar esta rama a `main`.**

## Índice completo

| Archivo | Para qué sirve |
|---|---|
| [01 · Punto de partida](docs/01_ESTADO_ACTUAL.md) | Qué está establecido, qué se propone y qué sigue bloqueado |
| [02 · Decisiones OWNER](docs/02_DECISIONES_OWNER.md) | D01–D10, alternativas, recomendación, estado y preguntas concretas |
| [03 · Modelo conceptual](docs/03_MODELO_CONCEPTUAL.md) | Objetos, estados, identidades, responsabilidades, flujo y antiobjetivos |
| [04 · Discovery offline](docs/04_DISCOVERY_OFFLINE.md) | Cómo investigar oportunidades débiles sin contaminar B |
| [05 · Estrategias y scoring](docs/05_ESTRATEGIAS_SCORING.md) | Priorización, hipótesis falsables, score e incertidumbre |
| [06 · Interfaces y Dataset](docs/06_DATASET_B_REGIMEN.md) | Separación A/B, GMM/HMM, claves, disponibilidad y bloqueos |
| [07 · Matriz de pruebas](docs/07_PRUEBAS_GATES.md) | Tests sintéticos, adversariales, criterios GO/NO-GO |
| [08 · Bitácora editable](docs/08_BITACORA_IPAD.md) | Seguimiento de decisiones e investigaciones desde el iPad |
| [09 · Regreso y continuidad](docs/09_PLAN_DE_REGRESO.md) | Orden exacto de trabajos posteriores, prompts y handoff |
| [10 · Fuentes y seguridad](docs/10_FUENTES_Y_LIMITES.md) | Procedencia, límites y protección de datos públicos/privados |

## Regla para no perder el trabajo

1. En GitHub, verifica que arriba figure esta rama, no `main`.
2. Abre un archivo, toca el lápiz, edítalo y **Commit changes** en esta misma rama.
3. Registra fecha, decisión, razón, dudas y próximos pasos.
4. No abras PR hacia `main` ni fusiones el cuaderno con el código del juego.
5. Si GitHub móvil limita la edición, guarda las notas en el iPad y transcríbelas después. No afirmes que se publicaron si no hay commit visible.

**Estado global:** recomendación conceptual `HYBRID_WITH_DISCOVERY`; auditoría fuente parcial; compatibilidad real con Dataset/B no acreditada; implementación y entrenamiento **NO AUTORIZADOS**.
