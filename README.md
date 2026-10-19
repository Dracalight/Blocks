# NEXUS BLOCKS: ENDLESS

Videojuego arcade de bloques descendentes desarrollado íntegramente para **Scratch 3** (`.sb3`), diseñado específicamente para funcionar con fluidez en el navegador de un **iPad escolar** (controles táctiles ergonómicos en pantalla horizontal) y en ordenadores de escritorio o portátiles (controles de teclado), sin instalar software adicional, sin requerir inicio de sesión y sin depender de extensiones externas ni de modificaciones tipo TurboWarp.

## Contenido del Repositorio

| Ruta | Descripción |
| :--- | :--- |
| `NEXUS-BLOCKS-ENDLESS.sb3` | Archivo de proyecto Scratch 3 terminado, listo para abrir y jugar en el editor oficial de Scratch. |
| `README.md` | Guía general del proyecto, instrucciones de importación en iPad/PC y resumen de modos de juego. |
| `docs/CONTROLS.md` | Mapa detallado de controles táctiles para iPad y atajos de teclado. |
| `docs/ARCHITECTURE.md` | Documentación técnica de la arquitectura interna (variables, listas, bloques personalizados y renderizado). |
| `docs/TESTS.md` | Informe de validación estructural (`.sb3`), pruebas automatizadas del grafo de bloques y limitaciones de entorno. |
| `CHANGELOG.md` | Historial de versiones por etapas (Etapa 1: Mecánicas Clásicas y Relax; Etapa 2: Chaos Mode, Sprint 40L y UI táctil). |
| `tools/build_sb3.py` | Generador programático determinista que sintetiza los sonidos WAV, gráficos SVG y el árbol `project.json` de Scratch 3. |
| `tools/validate_sb3.py` | Validador de esquema `.sb3` e intérprete de máquina virtual Scratch 3 que ejecuta las 11 pruebas obligatorias. |

## Cómo Descargar e Importar el Juego en Scratch 3 (iPad o PC)

1. Descarga el archivo **`NEXUS-BLOCKS-ENDLESS.sb3`** en tu iPad (se guardará en la app **Archivos / Descargas**) o en tu ordenador.
2. Abre Safari o Chrome y entra en el editor oficial de Scratch 3: **https://scratch.mit.edu/projects/editor/** (no necesitas iniciar sesión ni tener cuenta).
3. En la barra superior azul de Scratch, toca o haz clic en **Archivo (File)** y selecciona **Subir desde tu computador (Load from your computer)**.
4. Elige el archivo **`NEXUS-BLOCKS-ENDLESS.sb3`** que descargaste y acepta reemplazar el proyecto vacío actual.
5. Activa el botón de **Pantalla completa (Full Screen Control)** en la esquina superior derecha del escenario y pulsa la **Bandera Verde** para comenzar.

## Modos de Juego y Dificultades

### 4 Modos de Juego Seleccionables
* **ENDLESS CLASSIC**: Experiencia arcade clásica e infinita con incremento progresivo de velocidad cada 10 líneas completadas.
* **RELAX**: Caída inicial suave (`0.95 s` por fila) y progresión gradual para practicar colocaciones y giros sin presión.
* **CHAOS MODE**: Eventos temporales previsibles cada 15 segundos con aviso previo de 3 segundos en el monitor `Evento_Caos` (`AVISO: EVENTO EN 3s`), alternando entre **TURBO x2 PUNTOS** (velocidad incrementada con doble puntuación), **GRAVEDAD LUNAR** (caída flotante más lenta) y **BONO LINEA +500** (+500 puntos extra al limpiar líneas).
* **SPRINT 40L**: Reto contrarreloj (`Tiempo_Sprint`) cuyo objetivo es completar 40 líneas en el menor tiempo posible hasta activar la pantalla de victoria.

### 4 Niveles de Dificultad
* **Fácil**: Velocidad base inicial de `0.85 s` por fila, ideal para aprender los controles táctiles.
* **Normal**: Velocidad base inicial de `0.60 s` por fila, equilibrio estándar arcade.
* **Difícil**: Velocidad base inicial de `0.38 s` por fila, pensada para jugadores con experiencia.
* **Pesadilla**: Velocidad base inicial de `0.22 s` por fila, con límite técnico de seguridad fijado en `0.06 s` para evitar errores de temporización en Scratch 3.

## Reconstrucción y Ejecución de Pruebas desde Línea de Comandos

Si deseas regenerar el archivo `.sb3` desde el código fuente o ejecutar la batería de pruebas automatizadas:

```bash
python3 tools/build_sb3.py
python3 tools/validate_sb3.py
```
