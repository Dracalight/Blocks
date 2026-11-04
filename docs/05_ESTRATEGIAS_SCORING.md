# 05 · Estrategias, hipótesis y scoring

## Prioridades de investigación, no de implementación

| Familia | Papel | Qué tendría que demostrarse | Riesgo principal |
|---|---|---|---|
| Breakout continuation | **Baseline protegido** | Reproducción exacta de lógica e identidades; mantener grupo control | Cambio accidental de contrato o sesgo de selección |
| Failed breakout + reentry | **1ª complementaria** | Rechazo de ruptura causal, retorno a rango predeterminado y señal distinta de continuación | Reversiones aparentes identificadas solo a posteriori |
| Pullback continuation | **2ª opcional** | Contexto de tendencia causal, retroceso e indicio de reanudación con aporte independiente | Solapamiento con momentum y grados de libertad |
| Session range breakout | Pospuesta | Valor de horarios y límites por sesión, calendario y DST correctos | Redundancia con breakout y sesgos horarios |
| Trend/momentum | Contexto/pospuesta | Evidencia incremental frente a continuación | Colinealidad, extrapolación de estudios de otros horizontes |
| Mean reversion | Pospuesta | Condición causal de rango y estabilidad tras costes | Operar contra tendencias |
| Volatility compression/expansion | Contexto | Aportación de volatilidad a un patrón direccional | Volatilidad no equivale a BUY/SELL |
| Range trading | Pospuesta | Niveles anteriores, repetición y dependencia del régimen | Uso retrospectivo de límites |

No incluir todas a la vez. Los estudios históricos de FX no prueban rentabilidad de reglas M15 específicas.

## Vector preferido

Para familia `f`, conservar `bullish_evidence_f` y `bearish_evidence_f` separados, cada uno opcional en [0,1], más `reason_codes`, `readiness` y calidad. **Son medidas estructurales, no probabilidades de acierto.** No sumarlas a través de familias sin demostrar comparabilidad.

- **Dirección global:** derivada opcional, solo si la política `g(vector, calidad)` está aprobada.
- **Incertidumbre:** independiente de dirección; `UNKNOWN` si no hay estimador validado. Calidad no es automáticamente confianza.
- **Score UI 1–5:** cuantización secundaria; conservar valor original y versión de la transformación.
- **Conflictos:** guardar señales alcistas/bajistas a la vez. `UNRESOLVED` no significa `NEUTRAL`.
- **Parámetros:** reglas, ventanas, pesos, normalizaciones y umbrales se preregistran antes de observar outcomes.

## Comparaciones útiles desde el iPad

**Opción 1 — Score único 1–5:** fácil de leer, difícil de auditar, pierde resolución y es ambiguo con dos familias opuestas.

**Opción 2 — Score continuo firmado:** compacto, pero también oculta incertidumbre y desacuerdos; arriesga normalizar incorrectamente familia vs familia.

**Opción 3 — Vector por familia + score visual derivado:** conserva información y facilita falsación, requiere contrato más rico. **Recomendación provisional.**

## Preguntas que requieren decisión OWNER

1. ¿Deseas ver el score 1–5 en la interfaz, aun si internamente no se usa para B?
2. ¿Debe una misma vela poder contener evidencia BUY y SELL distintas sin derivar un lado global?
3. ¿Te interesa priorizar la diversificación de hipótesis sobre la frecuencia de señales?
4. ¿Qué evidencia exigirías para admitir una tercera familia?

No confundir estas respuestas con autorización para entrenar o desplegar modelos.
