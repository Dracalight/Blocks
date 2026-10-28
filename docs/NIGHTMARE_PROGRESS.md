# Nightmare: checkpoint de implementación

La tecla 4 selecciona NIGHTMARE. Enter o R inician una introducción de 0,8 segundos de tiempo lógico y después una partida de bloques con la gravedad inicial y el límite de Chaos. Un desplazamiento y cambio de escala interpolan la entrada con ese reloj, en un hilo exclusivamente visual. P pausa también la introducción y la reanuda desde el mismo punto. El fondo y la pantalla de entrada son SVG originales de alto contraste; el arte y la geometría de las piezas no cambian.

El calendario inicial alterna Double Garbage y Hold Jam tras al menos 20 segundos de juego y seis fijaciones sin amenaza activa, e incorpora Garbage Debt después de 60 segundos. Double Garbage anuncia cuatro fijaciones, indica las filas y permite cancelar una por cada dos líneas; Hold Jam se anuncia dos fijaciones antes y dura siete fijaciones. Garbage Debt da 12 fijaciones para reducir dos filas, una por cada dos líneas; la deuda vencida se anuncia dos fijaciones antes de entrar y ya no se puede cancelar. La basura se inserta con el procedimiento existente y se detiene si ocurre Game Over. Son implementaciones iniciales, sujetas a pruebas de juego y balance.

Desde 120 segundos, el calendario puede anunciar una de dos cadenas deterministas: Double Garbage → Hold Jam o Hold Jam → Garbage Debt. Ambos nombres se muestran desde el inicio y la segunda etapa tiene dos fijaciones de aviso. Una instantánea del evento al comenzar cada fijación impide descontar varias etapas en la misma pieza. Hold Jam puede solaparse con la deuda de la cadena, y el HUD muestra ambos estados en zonas diferentes. No comienza otra amenaza mientras haya una comprometida. Si hay al menos ocho celdas ocupadas en las cuatro filas superiores, se aplaza la siguiente amenaza y se muestra `PRESSURE DELAYED`; las amenazas ya anunciadas no se borran. Estos umbrales son provisionales y no sustituyen pruebas de jugabilidad.

El blindaje integrado usa dos etapas: una fila completa intacta se agrieta sin puntuar y se elimina automáticamente en la siguiente fijación, sin necesidad de acceder a un hueco. La variante y sus límites se describen en [el análisis de blindaje](NIGHTMARE_ARMOR_SPIKE.md).

Este es un **checkpoint incompleto**: todavía no hay selección Endless/Trials, oleadas, Glitch Protocol ni el catálogo de animaciones. La entrada animada es inicial y los avisos son estáticos. No representa el modo terminado ni está listo para merge.

Las comprobaciones Python cubren la pausa de la introducción, el límite de gravedad, un T-spin double con tres esquinas ocupadas, los contadores de Double Garbage y Hold Jam, cancelación parcial y total de basura, vencimiento de deuda, las dos cadenas, aplazamiento por altura y top-out durante una cadena. El planificador oficial funciona sin renderer y no constituye una prueba visual. Siguen pendientes evaluación visual, gameplay prolongado y teclado físico en iPad.

En esta ejecución se abrió el editor oficial de Scratch, que mostró `Your Browser Does Not Support WebGL`; no se pudo cargar el proyecto ni validar visualmente la animación o el HUD. No se midió el rendimiento gráfico ni se probó audio.

Los SVG del fondo Nightmare, la introducción, la alerta de blindaje y los bloques intacto y agrietado se extrajeron del SB3 y renderizaron con Inkscape para inspección estática. Esa revisión no ejecuta Scratch ni verifica escalado, superposición de HUD, movimiento o interacción real.

Se utiliza el contrato design-taste-frontend aportado por el OWNER: su skill original no estaba instalada. El arte provisional usa fondo oscuro, texto claro y ámbar de advertencia, con trazos rectos y tipografía técnica.
