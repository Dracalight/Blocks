# 04 · Descubrimiento de oportunidades débiles — protocolo para decidir

## Problema

Si los eventos confirmados son escasos, B no ve condiciones casi confirmadas. Enviar *cada* M15 como candidato transformaría su población y sus labels. Recomendación a deliberar: **episodios causales seleccionados offline**, con experimento independiente.

## Selector prospectivo — definición mínima (sin parametrizar hasta el prerregistro)

1. **Universo elegible U:** observaciones M15 disponibles, íntegras y con warmup; registrar denominador total. No seleccionar retrospectivamente solo velas "interesantes".
2. **Estado de formación:** evidencia de una familia se acerca a una condición estructural, usando exclusivamente prefijo hasta t. Ejemplo hipotético: aproximación a frontera previa o rechazo incompleto.
3. **Apertura del episodio:** regla fija con familia, lado, condición de entrada y `selected_at`; sin mirar resultados futuros.
4. **Episodio activo:** registrar continuidad y contradicción; evitar duplicar un nuevo candidato por cada vela.
5. **Cierre:** caducidad por tiempo/barras, confirmación, invalidación, cambio de segmento o política de conflicto; todos preregistrados.
6. **Exclusiones:** gaps, fuente atrasada, falta de warmup, relojes incompatibles, episodios en conflicto, selección múltiple según política.
7. **Congelación:** sellar población seleccionada y no seleccionada, IDs, versiones, hashes y razones ANTES de formar labels.
8. **Labels posteriores:** solo en un pipeline separado, con horizonte, costes, oportunidad de entrada, barreras/timeout, concurrencia y particiones independientes.
9. **Análisis:** tasa de cobertura vs U y eventos baseline, duplicados, episodios solapados, dependencia efectiva, estabilidad por ventanas y falsos positivos.

## Ejemplo conceptual (NO una regla aprobada)

- Cierre M15 t: precio cerca de canal previo, sin ruptura confirmada -> evidencia de proximidad.
- Cierre t+1: sigue cerca -> **mismo** episodio, no nuevo ejemplo independiente.
- Cierre t+2: cae dentro del rango -> invalida o cambia estado según regla prospectiva.
- Un label que use precios posteriores a t no puede cambiar qué habría sido seleccionado en t.

## Decisiones pendientes antes de programar selector

| Elemento | Alternativas | Propuesta inicial |
|---|---|---|
| Inicio | cercanía umbral / formación de patrón / puntuación causal | permitir regla por familia, registrada en contrato |
| Dirección | fuerte / tentativa / ambos lados | lado explícito; conflicto = abstención o episodio doble si protocolo aprueba |
| Caducidad | N barras / condición structural / cierre sesión | combinación determinista fijada antes del test |
| Reemisión | cada vela / solo transición / cooldown | solo transición y control de deduplicación |
| Solapamiento | aceptar todo / clusterizar / prioridad | medir y agrupar episodios, evitar IID ficticio |
| Labels | copiar labels de eventos / contrato propio | **contrato propio, nunca copiar** |
| B | reutilizar modelo operativo / experimento offline | **offline, calibración y target propios** |

## Fallos que deberían detener la investigación

- Cambiar una selección histórica al añadir datos futuros.
- Seleccionar el comienzo del episodio después de observar que fue rentable.
- Recalcular el mismo ID con otro contenido sin versión.
- Unir eventos y episodios por posición de fila.
- Mezclar negativos y no seleccionados.
- Reutilizar B operativo bajo cambio de población sin reentrenamiento/calibración/aceptación.
- Etiquetar solo los casos con resultado TP o SL sin registrar timeouts y exclusiones según protocolo.

**Pregunta para el iPad:** ¿qué riesgo te preocupa más: perder oportunidades, generar ruido en B, o no poder distinguir una estrategia fuerte de una oportunidad apenas naciente? Anota el orden y la justificación en D04.
