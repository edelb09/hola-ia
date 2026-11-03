# Lector de cotizaciones

Sube una cotización de un proveedor en PDF y obtén una tabla con los datos clave, lista para descargar en CSV.

**App:** https://hola-ia-gxmaappgwdq4xzuhq9jpebu.streamlit.app/

> Usa solo documentos de ejemplo. El texto del PDF se envía a la API de Gemini, así que no subas cotizaciones reales ni confidenciales.

## Problema y usuario

Una persona del equipo de compras de una empresa industrial recibe varias cotizaciones en PDF cada semana, y cada proveedor usa su propio formato. Hoy abre cada PDF, busca proveedor, partes, cantidades, precios y plazos, y los copia a mano a una hoja de cálculo. Lleva tiempo y se cuelan errores de transcripción.

**Qué resuelve la IA:** leer documentos con formatos distintos y devolver siempre los mismos campos.
**Qué queda fuera:** decidir a qué proveedor comprar, comparar ofertas, validar contra el sistema de compras, leer PDFs escaneados (no hay OCR) y guardar documentos.

## Qué hace

1. Subes un PDF con texto y puedes ver el texto que se ha podido leer.
2. Pulsas **Extraer datos** y la IA devuelve una fila por artículo con siete campos: proveedor, número de parte, descripción, cantidad, precio unitario, plazo de entrega y fecha de validez.
3. Descargas la tabla como CSV.

Si un dato no aparece en el documento, la celda dice **"No encontrado"**. La app nunca lo inventa.

## Cómo usarla

1. Abre la app.
2. Arrastra un PDF de cotización de ejemplo (inventado, nunca uno real).
3. Pulsa **Extraer datos** y revisa la tabla.
4. Pulsa **Descargar CSV**.

## La pieza de IA

- **API de Gemini** con el SDK `google-genai`. Modelo principal `gemini-3.8-flash` y `gemini-3.5-flash-lite` de respaldo.
- La respuesta se pide en **JSON** y con `temperature=0` para que sea lo más repetible posible.
- **Por qué esta pieza:** cada proveedor redacta su cotización de forma distinta y con reglas fijas habría que reescribir la lectura para cada uno. Un RAG no hace falta, porque una cotización es corta y cabe entera en el prompt.

### Qué pasa si falla

| Situación | Qué ve el usuario |
| --- | --- |
| Error 429 (cuota) o 503 (modelo saturado) | La app reintenta dos veces con cada modelo y prueba el de respaldo; si todo falla, un mensaje claro |
| Otro error de la API | "El servicio de IA no ha respondido (error N)" |
| Falta la clave en la configuración | "Falta la clave de la IA en la configuración de la app" |
| La IA devuelve algo ilegible | "La IA devolvió algo que no he podido leer" |
| PDF escaneado (sin texto) | Aviso claro, sin llamar a la IA |
| Archivo que no es una cotización | Aviso, sin tabla |

## Estructura del repositorio

```
hola-ia/
├── app.py             # la app de Streamlit
├── requirements.txt   # streamlit, pypdf, pandas, google-genai
├── AGENTS.md          # contexto y reglas para agentes de programación
├── README.md          # este archivo
└── .gitignore         # protege .streamlit/secrets.toml y .env
```

## Clave de la API

La clave **no está en el código ni en el repositorio**. Se guarda en los secretos de la plataforma y se lee con `st.secrets["GEMINI_API_KEY"]`.

- **En Streamlit Community Cloud:** Settings, Secrets, formato TOML:
  ```toml
  GEMINI_API_KEY = "tu-clave"
  ```
- **En local:** el mismo formato en `.streamlit/secrets.toml` (ese archivo está en el `.gitignore`).

## Ejecutarla en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo se ha construido (proceso con IA)

- **Contexto del agente:** [AGENTS.md](AGENTS.md).
- **Qué se delegó en la IA:** el borrador de la especificación y del `AGENTS.md`, el código completo de `app.py`, la lógica de reintentos con modelo de respaldo y las etiquetas de las columnas.
- **Qué se revisó a mano:** cada fila de la tabla contra el PDF de ejemplo, que un dato ausente salga como "No encontrado", un `NameError` que escondía el mensaje genérico de error y un cambio en `CAMPOS` que habría dejado todas las celdas vacías.

### Registro de prompts (los que más cambiaron el rumbo)

1. *"estuve pensando agarrar un proyecto sobre un agente que lea QUOTES, PDF [...], si consideras que otra idea es mejor sugiere"*. Se eligió el lector de cotizaciones y se descartó un gestor de proyectos.
2. *"[...] but gave me this: El servicio de IA no ha respondido (error 503)"*. El modelo estaba saturado: se añadieron reintentos y un modelo de respaldo.
3. *"now it gives me this: Algo ha fallado al procesar la cotización"* + el `app.py` completo. El mensaje genérico escondía un `NameError` (`MODELO` frente a `MODELOS`).
4. *"lets add description"*. Nueva columna de descripción.
5. *"I changed CAMPOS to this: CAMPOS = ["Proveedor", ...]"*. Habría roto la tabla: las claves deben coincidir con las del prompt, y las mayúsculas van en un diccionario de etiquetas solo para mostrar.

## Prueba y mejora

Probada como usuario con una cotización de ejemplo inventada de cuatro líneas (partes A-100, A-220, A-310 y SV-12). Salieron las cuatro filas con cantidades y precios correctos, y el plazo de entrega como "No encontrado" porque el documento no lo trae. De la prueba salieron tres cambios: reintentos y modelo de respaldo ante el error 503, la columna de descripción y cabeceras legibles.

## Pitch

1. En los equipos de compras, alguien pasa a mano a una hoja de cálculo los datos de cada cotización en PDF, y cada proveedor usa un formato distinto.
2. Lector de cotizaciones recibe el PDF y devuelve una tabla con proveedor, parte, descripción, cantidad, precio, plazo y validez, lista para descargar en CSV.
3. La IA lee documentos con formatos distintos y devuelve siempre los mismos campos, algo que con reglas fijas habría que reescribir para cada proveedor, y cuando un dato no está dice "No encontrado" en vez de inventarlo.
4. Al probarla con una cotización de ejemplo, el modelo de Google se saturó y la app falló; ahora reintenta, usa un segundo modelo y muestra mensajes claros.
5. Lo siguiente es comparar varias cotizaciones del mismo producto: mi cotización de ejemplo tiene cuatro líneas y $12,045 de subtotal, así que con tres proveedores serían doce líneas que hoy se comparan a ojo.

## Límites

- Solo lee PDFs con texto; los escaneados no se procesan.
- Es una herramienta de apoyo: hay que revisar la tabla antes de usarla.
- La capa gratuita de Gemini tiene límites; si se agota, la app lo avisa.
