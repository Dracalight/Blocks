# Nightmare: checkpoint de implementación

La tecla 4 selecciona NIGHTMARE. Enter o R inician una introducción de 0,8 segundos de tiempo lógico y después una partida de bloques con la gravedad inicial y el límite de Chaos. P pausa también la introducción y la reanuda desde el mismo punto. El fondo y la pantalla de entrada son SVG originales de alto contraste; el arte y la geometría de las piezas no cambian.

El calendario inicial alterna Double Garbage y Hold Jam tras al menos 20 segundos de juego y seis fijaciones sin amenaza activa, e incorpora Garbage Debt después de 60 segundos. Double Garbage anuncia cuatro fijaciones, indica las filas y permite cancelar una por cada dos líneas; Hold Jam se anuncia dos fijaciones antes y dura siete fijaciones. Garbage Debt da 12 fijaciones para reducir dos filas, una por cada dos líneas; la deuda vencida se anuncia dos fijaciones antes de entrar y ya no se puede cancelar. La basura se inserta con el procedimiento existente y se detiene si ocurre Game Over. Son implementaciones iniciales, sujetas a pruebas de juego y balance.

Este es un **checkpoint incompleto**: todavía no hay selección Endless/Trials, Chaos Chain, blindaje, oleadas, Glitch Protocol ni el catálogo de animaciones. La introducción y los avisos son estáticos y provisionales. No representa el modo terminado ni está listo para merge.

Las comprobaciones Python cubren la pausa de la introducción, el límite de gravedad, un T-spin double con tres esquinas ocupadas, los contadores de Double Garbage y Hold Jam, cancelación parcial y total de basura y el vencimiento de la deuda. El planificador oficial prueba selección, entrada, pausa y resolución de basura doble; funciona sin renderer y no constituye una prueba visual. Siguen pendientes evaluación visual, combinaciones, gameplay prolongado y teclado físico en iPad.

Se utiliza el contrato design-taste-frontend aportado por el OWNER: su skill original no estaba instalada. El arte provisional usa fondo oscuro, texto claro y ámbar de advertencia, con trazos rectos y tipografía técnica.
