# NEXUS MITTENS · The Broken Gambit

Juego de ajedrez en español con personaje original, motor Stockfish 19 NNUE y comentarios derivados de la posición. Estado de la misión completa **INCOMPLETE**.

## Jugar

Descomprime el proyecto. Desde su directorio ejecuta:

```sh
python -m http.server 8765 --directory app
```

En Windows también puedes usar `py -m http.server 8765 --directory app`. Abre http://localhost:8765. El perfil Móvil viene instalado. Selecciona tus piezas antes de iniciar una partida. Pulsa origen y destino o arrastra. Los relojes cuentan tiempo de juego visible. Rendirse o acordar tablas termina la partida. Desde el cuaderno puedes revisar posiciones y las variantes de tus jugadas analizadas.

Para publicar, sirve el contenido de `app/` mediante HTTPS y entrega los archivos WASM con el tipo `application/wasm`. La primera visita descarga la aplicación y el motor ligero. La caché queda disponible cuando termina la instalación del service worker. En Safari, abre Compartir y Añadir a pantalla de inicio. La expulsión del almacenamiento local puede borrar caché y partida. Exporta PGN para conservarla.

Para preparar Maximum Intelligence en el servidor, ejecuta `npm ci` y `npm run maximum` antes del despliegue. Esto copia las variantes completas de uno y varios hilos. Selecciona Mittens Killer en ajustes. Cada cliente carga la variante elegida en su primera búsqueda. Para varios hilos configura las cabeceras `Cross-Origin-Opener-Policy: same-origin` y `Cross-Origin-Embedder-Policy: require-corp`. Sin aislamiento se utiliza un hilo. El perfil no reduce el parámetro Skill Level. La profundidad y el tiempo limitan la búsqueda conjuntamente.

## Generación opcional

Por defecto funciona el generador procedural offline. Para usar un modelo local de texto instala Ollama por separado, descarga el modelo con `ollama pull qwen2.5:0.5b` y arranca su servidor. Ejecuta `python provider-server.py`, abre http://127.0.0.1:8765 y elige Proveedor configurado. El adaptador también acepta proveedores de chat compatibles con OpenAI mediante las variables del servidor `NEXUS_ENDPOINT`, `NEXUS_MODEL` y `NEXUS_API_KEY`. La configuración externa transmite el evento y tres jugadas recientes al proveedor elegido. El servidor de referencia se limita a loopback y a 30 solicitudes/hora por proceso. El tiempo máximo de espera desde el cliente es de nueve segundos. El comentario procedural aparece primero. Las respuestas se insertan como texto. El modelo carece de acceso al controlador de movimientos. Integración real con modelos descargados o proveedores comerciales **NOT_RUN**.

## Motor, arquitectura y método

La etiqueta oficial sf_19 resolvió a edb0d9db6731067ec50ce619ff372b463bc4dd5d. El port publicado 19.0.1 corresponde a 0d5dd7944f88c817c07a26bc4fb1905d5f9c46d6. El port describe redes de distinto tamaño en Lite (aprox. 1,7 MB) y Full (aprox. 94 MB), SIMD y aislamiento para múltiples hilos. El mantenedor indica compatibilidad con navegadores modernos e iOS 16+ en sistemas admitidos. Las pruebas de este proyecto cubren Chromium Linux. Lc0 utiliza una red y un backend de inferencia independiente y su rendimiento depende de la aceleración disponible. Qwen2.5-0.5B-Instruct es una alternativa pequeña bajo Apache-2.0. No se distribuyen sus pesos. WebLLM ofrece ejecución mediante WebGPU, pendiente de integración.

Fuentes originales: [Stockfish](https://github.com/official-stockfish/Stockfish/releases/tag/sf_19), [Stockfish.js](https://github.com/nmrugg/stockfish.js/tree/v19.0.1), [Lc0](https://github.com/LeelaChessZero/lc0), [Qwen](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), [WebLLM](https://github.com/mlc-ai/web-llm), [chess.js](https://github.com/jhlywa/chess.js).

La configuración reproducible, el binario y los recursos de cómputo del Mittens original no se han podido verificar. Comparación directa **NO_VERIFICABLE**.

- Chess.js mantiene el historial legal. El controlador game.js conserva PGN, ajustes, análisis pendiente y revisión en localStorage. El cliente está escrito en JavaScript con módulos ES.
- engine.js inicia un Worker por búsqueda, negocia UCI, configura Hash y MultiPV 2, envía el historial completo y procesa score, pv y bestmove. La cancelación termina el Worker. Una generación de sesión descarta resultados antiguos. Crear un Worker en cada búsqueda descarta la tabla Hash anterior.
- analyzer.js orienta ambas evaluaciones al jugador. La pérdida es max(0, antes − después) en centipeones. Los mates se ordenan mediante ±(10000 − distancia). La estimación logística 1/(1+exp(−cp/180)) es heurística. Los movimientos con mate, forzados y las preferencias del motor tienen prioridad. BEST coincide con la primera línea. GREAT añade una diferencia de 120 cp sobre la alternativa. BRILLIANT exige que la respuesta principal capture en destino, una diferencia material ofrecida de al menos dos peones, primera elección, ventaja restante de 100 cp, segunda línea al menos 100 cp inferior y continuación de cuatro medias jugadas. Son criterios propios sujetos al horizonte de búsqueda.
- MISSED_OPPORTUNITY registra caídas desde más de 200 hasta menos de 50 cp. Para jugadas restantes, los umbrales de BLUNDER, MISTAKE e INACCURACY son 200, 100 y 50 cp. EXCELLENT admite hasta 15 cp y GOOD cubre el resto. Precisión media = promedio de 100 × exp(−pérdida/150) sobre los movimientos analizados del jugador.
- project combina acontecimiento, personalidad e intensidad. El tablero de revisión reproduce la línea principal desde la posición anterior. El service worker versiona el cliente y su motor.

## Validación

Ejecuta `npm test`. Con la aplicación en localhost:8765, Python Playwright y Chromium instalado en /usr/bin/chromium, ejecuta `python tests/browser.py` y `python tests/performance.py`. El test de navegador también genera los iconos desde el SVG original.

| Estado | Cobertura |
|---|---|
| PASS | Siete pruebas automatizadas de reglas, ida y vuelta PGN, análisis y comentario |
| PASS | Respuestas reales de Stockfish ligero en Chromium, recarga con sesión persistida y otra jugada sin red |
| PASS | Stockfish completo de un hilo devolvió e2e4 y dos variantes desde la posición inicial |
| PASS | Cuatro partidas completas automatizadas Lite contra Lite, cuatro tablas |
| NOT_VERIFIED | Windows, iPhone 13 Pro Max, iPad, instalación desde Safari, temperatura, consumo máximo del Worker, estabilidad prolongada |
| NOT_RUN | Comparación con Komodo o versiones anteriores, prueba multihilo, modelos de texto reales |
| INCOMPLETE | Archivo de múltiples partidas, expresiones faciales diferenciadas para todos los estados, gráfica de evaluación, resumen generativo final, identificación fiable de remontadas y amenazas ignoradas, descarga del modelo dentro del navegador y batería completa de regresión |

Los archivos en results/ contienen las salidas observadas. El microbenchmark registra una búsqueda, tiempo medio para 1000 comentarios procedurales, tiempo de selección hasta el siguiente frame y heap principal. Es una muestra de Chromium headless Linux. La cifra de memoria excluye el Worker.

El harness `node tests/match.js [ejecutableA] [ejecutableB]` acepta motores UCI instalados legalmente. Requiere `npm ci` para el motor predeterminado. Configura MOVE_MS para cambiar el presupuesto (40 ms predeterminados), un hilo y 16 MiB de Hash. Intercambia colores en dos aperturas. Las cuatro tablas de autocontrol producen una diferencia descriptiva de 0 Elo con incertidumbre sin acotar en esta muestra. La dependencia entre aperturas emparejadas limita la interpretación del intervalo. No se evaluó la fuerza relativa frente a Mittens.

## Licencias y distribución

Código y recursos originales del juego bajo GPL-3.0-only. Stockfish.js y Stockfish bajo GPLv3. Se incluye el árbol fuente de la etiqueta exacta con sus scripts de compilación en source/stockfish-js-v19.0.1.tar.gz. Consulta su README y build.js para Emscripten y las descargas de redes necesarias. Chess.js 1.4.0 bajo BSD-2-Clause. Avisos y textos en app/licenses/. Al redistribuir la aplicación mantén accesibles las fuentes correspondientes y avisos junto a los binarios. El proyecto usa gráficos propios.
