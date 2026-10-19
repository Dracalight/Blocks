# Versionado y distribución

Cada versión publicada de NEXUS BLOCKS debe identificar claramente el juego y su versión en el proyecto Scratch (.sb3), el ZIP distribuible y la publicación de GitHub.

## Regla

- Usa el ID estable del juego: `NEXUS-BLOCKS`. El ID identifica el juego y no cambia entre versiones.
- Asigna a cada versión un número SemVer `MAJOR.MINOR.PATCH`; la primera versión formal será `0.1.0`.
- Usa el mismo número para el proyecto .sb3, el ZIP y la etiqueta de Git. Por ejemplo: `NEXUS-BLOCKS-v0.1.0.sb3`, `NEXUS-BLOCKS-v0.1.0.zip` y etiqueta `v0.1.0`.
- Incluye el ID y la versión en las notas de publicación y en `CHANGELOG.md`. No reutilices una versión publicada: cada publicación nueva incrementa el número.
- Actualiza los enlaces de descarga del README para que apunten a los artefactos de esa versión, no a un ZIP ambiguo de `main`.

## Cómo incrementar

- **PATCH** (`0.1.1`): correcciones compatibles sin añadir funcionalidad significativa.
- **MINOR** (`0.2.0`): nuevas funciones compatibles mientras el juego siga en etapa inicial `0.y.z`.
- **MAJOR** (`1.0.0`): primera versión estable o cambio incompatible después de `1.0.0`.

Antes de publicar, verifica el proyecto con los comandos de validación y pruebas indicados en el README. Publica el .sb3 y el ZIP juntos bajo la misma etiqueta para que ambos representen exactamente la misma versión.
