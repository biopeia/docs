# Auditoría documental de Biopeia

Diátaxis · Arquitectura documental · Revisión del 16 de octubre de 2026

## 1. Diagnóstico: la documentación necesita separar sus propósitos, no sus fuentes

Tras revisar las dos publicaciones y la estructura de biopeia/docs, se recomienda una reorganización importante del corpus documental y del sistema de publicaciones.

No se recomienda dividir la documentación entre nuevos repositorios ni convertir los PDF en documentos editados independientemente.

La arquitectura correcta debe conservar tres responsabilidades:

- **Corpus canónico:** contiene los documentos originales, cada uno con una finalidad comunicativa definida.
- **Registros estructurados:** describen componentes, contratos, estados, evidencias, dependencias y trazabilidad.
- **Publicaciones:** seleccionan, ordenan y presentan la información canónica sin convertirse en una nueva autoridad.

Esta separación ya está establecida expresamente en `publication/README.md`. Conviene conservarla como fundamento de la reorganización.

### Estado documental observado

- **BIOPEIA MASTER:** 237 páginas · 57 capítulos documentales
- **TECHNICAL REFERENCE:** 88 páginas · 3 capítulos documentales y 11 secciones generadas
- **CATÁLOGO CANÓNICO:** 41 componentes registrados
- **CONTRATOS TRANSDOMINIO:** 11 contratos documentados

Ambas publicaciones se generaron desde la revisión `docs@7642ebe`, con los mismos registros y revisiones de dominio. Son working editions, no publicaciones oficiales consolidadas.

### Hallazgos principales

| ID     | Hallazgo | Prioridad |
| ------ | -------- | --------- |
| DOC-01 | El corpus principal mezcla explicación científica, descripción técnica y auditoría de implementación. | Alta |
| DOC-02 | La referencia incluye al menos un capítulo explicativo completo que también aparece en Master. | Media |
| DOC-03 | Tutoriales y guías How-to no están representados en las publicaciones existentes. | Alta |
| DOC-04 | La publicación principal agrupa Modality y Observation pese a sus responsabilidades independientes. | Media |
| DOC-05 | Las auditorías de código están condicionadas por revisiones concretas, pero se presentan dentro de una obra de arquitectura general. | Alta |
| DOC-06 | El modelo de registros permite trazabilidad técnica, pero no clasifica explícitamente cada documento según los cuatro propósitos de Diátaxis. | Alta |
| DOC-07 | La cobertura de referencias sigue siendo parcial: 9 parámetros y 3 métricas registrados. | Media |

La cuestión central es que Biopeia necesita distinguir con claridad lo que se ha decidido, lo que se ha implementado, lo que se ha observado y lo que todavía constituye una hipótesis.

Diátaxis permite ordenar cómo se comunica esa información, pero no sustituye los mecanismos de evidencia y gobierno que Biopeia ya tiene.

## 2. Arquitectura documental propuesta

La estructura recomendada mantiene cuatro cuadrantes Diátaxis y una capa transversal de gobierno y trazabilidad.

- **biopeia/docs:** Única fuente documental canónica
- **Tutoriales:** Aprender haciendo. Experiencias guiadas y reproducibles.
- **How-to:** Resolver tareas. Operación, integración y diagnóstico.
- **Referencia:** Consultar especificaciones. Catálogos, contratos y parámetros.
- **Explicación:** Comprender fundamentos. Arquitectura, ciencia y decisiones.
- **Capa transversal:** Registros, ADR, diseños, auditorías versionadas, procedencia, estados de evidencia y validadores. Alimenta los cuatro cuadrantes sin constituir un quinto tipo Diátaxis.
- **Publicaciones generadas:** Manual científico · Referencia técnica · Manual operativo · Introducción guiada.

### Estructura objetivo del repositorio

```text
docs/
├── tutorials/
│   ├── getting-started/
│   └── experiments/
├── how-to/
│   ├── operator/
│   ├── developer/
│   └── research/
├── reference/
│   ├── architecture/
│   ├── components/
│   ├── contracts/
│   ├── domains/
│   ├── schemas/
│   ├── parameters/
│   ├── metrics/
│   ├── evidence/
│   └── terminology/
├── explanation/
│   ├── biopeia/
│   ├── scientific-foundations/
│   ├── organism/
│   ├── embodiment/
│   ├── environment/
│   ├── world/
│   ├── modality/
│   ├── observation/
│   ├── lab/
│   └── cross-domain/
├── technical/
│   ├── adr/
│   ├── design/
│   └── migration/
├── audits/
│   └── implementation/
├── research/
├── registry/
├── publication/
│   ├── publications/
│   ├── style/
│   └── assets/
├── tools/
└── tests/
```

Esta es una estructura objetivo, no una descripción de carpetas que ya existan íntegramente.

Hay dos decisiones importantes:

1. **Los ADR y los diseños permanecen en `technical/`**, porque ya tienen un régimen propio de aprobación y autoridad. Diátaxis determina cómo se explican o consultan, pero no altera ese régimen.
2. **Las auditorías de implementación conservan su carácter de evidencia versionada en `audits/`**. Sus conclusiones se enlazarán desde las explicaciones y referencias pertinentes, evitando confundir una instantánea de código con una descripción conceptual duradera.

La estructura por dominios conserva los siete dominios actuales. Frontend continúa siendo una aplicación independiente y pasiva, externa a ellos.

## 3. Reorganización de los contenidos existentes

No realizar una migración automática indiscriminada de todos los documentos de `explanation/` a `reference/`.

Muchos documentos empiezan explicando qué hace un mecanismo y después incluyen sus tipos, límites, algoritmos, pruebas y hallazgos.

Por ejemplo, `explanation/organism/cognitive-graph.md` contiene una explicación del grafo, pero también reglas de validación, límites numéricos y comportamiento preciso de las activaciones. En cambio, `explanation/world/recovery.md` sigue el proceso real de recuperación del código revisado.

La clasificación debe hacerse por sección y propósito, no únicamente por el nombre del archivo.

### Propuesta por bloque documental

| Contenido actual | Tratamiento recomendado |
| ---------------- | ----------------------- |
| Arquitectura ejecutiva y naturaleza de Biopeia | Mantener en Explanation. |
| Hipótesis científicas candidatas | Mantener como explicación investigadora, con aprobación independiente de cada hipótesis. |
| Madurez de capacidades | Generar vistas derivadas del registro de evidencias, sin convertirlas en nueva fuente. |
| Ciclo causal transdominio | Separar explicación conceptual, contrato técnico y descripción de implementación. |
| 22 capítulos de Organism | Revisar y dividir selectivamente en explicación, referencia y auditoría de implementación. |
| 5 capítulos de Embodiment | Separar fundamentos físicos, descripción de morfología y parámetros concretos. |
| 5 capítulos de Environment | Mantener explicaciones sobre escenarios y recursos; extraer contratos y esquemas técnicos. |
| 12 capítulos de World | Separar causalidad, persistencia, operación M1, recuperación y registros técnicos. |
| Modality y Observation | Mantener publicaciones y capítulos diferenciados por autoridad y responsabilidad. |
| 4 capítulos de Lab | Separar fundamentos del aparato científico, procedimientos operativos y contratos. |
| Catálogo de componentes | Referencia generada, con fichas individuales navegables. |
| Catálogo de contratos | Referencia generada y enlazada con los documentos propietarios. |
| ADR y diseños | Mantener los registros originales y publicar índices derivados. |

### Tres ejemplos concretos de división

- **Organism — Grafo cognitivo (`explanation/organism/cognitive-graph.md`):**
  Conservar la explicación del funcionamiento y sus límites conceptuales. Extraer a Reference los tipos de nodos, aristas, invariantes y parámetros verificables. Mantener la evidencia de las revisiones y ejecuciones en la capa de auditoría. No convertir etiquetas como predictor o concept en afirmaciones de capacidad científica.
- **World — Recuperación causal (`explanation/world/recovery.md`):**
  Crear una explicación de las garantías de recuperación, una referencia del contrato técnico y una guía operativa para recuperar un corte confirmado. La guía debe construirse únicamente a partir de interfaces operativas realmente disponibles.
- **World — Bootstrap M1 (`explanation/world/m1-process-bootstrap.md`):**
  Llevar la sintaxis CLI, los requisitos de preflight y el esquema de perfil a Reference. Crear un How-to de ejecución de M1, con comprobaciones y diagnóstico. Reservar el Tutorial para una sesión completa con datos de ejemplo, versión y resultados esperados verificados.

**Regla de migración:** no eliminar ni sustituir un documento original hasta verificar que sus afirmaciones, citas, limitaciones, evidencias y dependencias han quedado correctamente preservadas.

## 4. Problemas concretos del sistema de publicación

### 4.1. El validador actual no admite todavía el Diátaxis completo

En `tools/publication/model.py`, la constante `CHAPTER_ROOTS` restringe las fuentes:

```python
CHAPTER_ROOTS = ("explanation/", "reference/")
```

Añadir `tutorials/` y `how-to/` requiere actualizar el generador para reconocerlas como fuentes publicables y exigir su cobertura.
Además, `registry/schema.yaml` declara:

```yaml
layout:
  canonical_docs: explanation/
  canonical_refs: explanation/
  adrs: technical/adr/
  design: technical/design/
```

La asociación de `canonical_refs` con `explanation/` debe ajustarse en coordinación con la evolución de los validadores.

### 4.2. Hay duplicación real entre publicaciones

`explanation/cross-domain/observation-presentation-boundary.md` está incluido tanto en Master como en Technical Reference. Debe conservarse como explicación arquitectónica y derivar una ficha técnica con contratos e interfaces verificables.

### 4.3. La generación de índices debe ampliarse

`tools/render_indexes.py` requiere incorporar:

- Navegación independiente para cada cuadrante.
- Índices por dominio y por tarea.
- Referencias cruzadas entre explicación y especificaciones.
- Detección de documentos no clasificados.
- Enlaces a las auditorías que sustentan cada afirmación.
- Comprobación de que los documentos publicados mantienen su revisión y procedencia.

### 4.4. Mecanismos valiosos que se preservan

- Publicaciones generadas desde manifiestos.
- Registros canónicos de componentes y contratos.
- Revisiones de código asociadas a unidades.
- Estados arquitectónicos y de evidencia independientes.
- Publicación determinista DOCX/PDF.
- Verificación estricta de enlaces y referencias.
- Ediciones de trabajo frente a publicaciones oficiales.
- Detección de obsolescencia del código documentado.

## 5. Publicaciones finales recomendadas

- **Volumen I — Biopeia: fundamentos y arquitectura (Explanation):** Visión de Biopeia, arquitectura de los 7 dominios, decisiones constitucionales, fundamentos científicos, hipótesis y compromisos de diseño.
- **Volumen II — Biopeia: referencia técnica (Reference):** Catálogos de componentes, contratos, interfaces, estructuras de estado, esquemas, parámetros, métricas, identificadores y registros de decisiones.
- **Volumen III — Biopeia: manual de operación y desarrollo (How-to):** Procedimientos para preparar experimentos, ejecutar simulaciones, recuperar estados, inspeccionar observaciones, diagnosticar fallos y desarrollar integraciones.
- **Volumen IV — Biopeia: aprendizaje guiado (Tutorials):** Experiencias ejecutables paso a paso desde capacidades demostradas (ej. ejecución M1, identificación de dominios, seguimiento de corte causal).

Capa transversal de auditorías y evidencias versionadas consultables por revisión, dominio y hallazgo.

## 6. Automatización y reglas de gobierno

Clasificación Diátaxis como requisito verificable en CI:

| Metadato | Función |
| -------- | ------- |
| `diataxis_kind` | `tutorial`, `how-to`, `reference` o `explanation` |
| `document_id` | Identidad estable pese a movimientos de carpeta |
| `domain` | Dominio responsable o alcance transdominio |
| `source_of_truth` | Fuente autorizada de los hechos publicados |
| `depends_on` | Documentos y unidades que obligan a revisar el contenido |
| `review_basis` | Revisiones concretas contra las que se ha contrastado |
| `evidence_scope` | Alcance de las afirmaciones respaldadas por evidencia |
| `publication_targets` | Publicaciones en las que puede incluirse |

### Tres garantías irrenunciables

1. **Ninguna refactorización documental cambia una decisión aprobada.** Las ADR y los diseños mantienen sus autoridades originales.
2. **Ninguna reorganización eleva el nivel de evidencia.** Un test no se transforma en demostración científica por cambiar la ubicación de su documentación.
3. **Ninguna publicación pierde procedencia.** El contenido generado sigue vinculado al commit, contrato, unidad o registro que lo fundamenta.

## 7. Plan de ejecución

- **P0 — Formalizar la arquitectura Diátaxis:** Definir los cuatro cuadrantes, clasificación obligatoria, excepciones y relación con registros existentes. (Salida: ADR-0114).
- **P1 — Inventario y clasificación exhaustiva:** Clasificar los 57 capítulos y secciones mixtas; identificar destinos, duplicaciones y contenido no publicado. (Salida: Matriz de migración y cobertura).
- **P2 — Ampliar el modelo documental:** Actualizar esquemas, manifiestos, índices, generador de publicaciones y tests sin romper las publicaciones existentes. (Salida: Validación automatizada).
- **P3 — Refactorizar el corpus:** Separar explicación, referencia y auditoría con especial atención a Organism, World y contratos transdominio. (Salida: Corpus refactorizado con fidelidad al original).
- **P4 — Construir guías y tutoriales:** Crear procedimientos sobre capacidades demostradas y verificadas. (Salida: Suites ejecutables de how-to/tutorial).
- **P5 — Publicar y retirar composiciones anteriores:** Generar los cuatro volúmenes y someter a aprobación editorial. (Salida: Ediciones consolidadas).
