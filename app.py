import json
import time

import pandas as pd
import streamlit as st
from google import genai
from google.genai import errors, types
from pypdf import PdfReader

MODELOS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]  # si el primero falla, prueba el segundo
CAMPOS = ["proveedor", "numero_parte", "cantidad", "precio_unitario",
          "plazo_entrega", "fecha_validez"]
NO_ENCONTRADO = "No encontrado"

PROMPT = """Eres un asistente que lee cotizaciones de proveedores para un equipo de compras.
Del texto de abajo extrae una fila por cada artículo cotizado, con estos campos exactos:
proveedor, numero_parte, cantidad, precio_unitario, plazo_entrega, fecha_validez.

Reglas:
- Devuelve SOLO una lista JSON de objetos, sin texto adicional.
- Si un dato no aparece en el texto, escribe "No encontrado". No lo inventes ni lo deduzcas.
- Si el texto no parece una cotización, devuelve una lista vacía: [].
- Copia los valores tal como aparecen en el documento.

Texto de la cotización:
{texto}
"""


def leer_pdf(archivo) -> str:
    """Devuelve el texto de todas las páginas del PDF."""
    lector = PdfReader(archivo)
    paginas = [(p.extract_text() or "").strip() for p in lector.pages]
    return "\n\n".join(t for t in paginas if t)


def extraer_filas(texto: str) -> list:
    """Pide a Gemini los datos de la cotización; si el modelo está saturado, prueba otro."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ultimo_error = None
    for modelo in MODELOS:
        for intento in range(2):
            try:
                respuesta = client.models.generate_content(
                    model=modelo,
                    contents=PROMPT.format(texto=texto[:20000]),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json", temperature=0
                    ),
                )
                return json.loads(respuesta.text)
            except errors.APIError as e:
                if e.code in (429, 503):
                    ultimo_error = e
                    time.sleep(2)
                else:
                    raise
    raise ultimo_error


st.set_page_config(page_title="Lector de cotizaciones", page_icon="📄")
st.title("Lector de cotizaciones 📄")
st.write("Sube una cotización en PDF y te devuelvo una tabla con los datos clave, "
         "lista para descargar en CSV.")
st.caption("Usa solo documentos de ejemplo: el texto se envía a la API de Gemini.")

archivo = st.file_uploader("Cotización en PDF", type=["pdf"])

if archivo is not None:
    if st.session_state.get("nombre") != archivo.name:
        st.session_state.pop("df", None)
        st.session_state["nombre"] = archivo.name

    try:
        texto = leer_pdf(archivo)
    except Exception:
        st.error("No he podido abrir el archivo. Comprueba que es un PDF válido.")
        st.stop()

    if not texto:
        st.warning("Este PDF no tiene texto legible, parece una imagen escaneada. "
                   "Prueba con un PDF generado desde un programa.")
        st.stop()

    with st.expander("Ver el texto extraído del PDF"):
        st.text(texto)

    if st.button("Extraer datos"):
        filas = None
        with st.spinner("Leyendo la cotización..."):
            try:
                filas = extraer_filas(texto)
            except (KeyError, FileNotFoundError):
                st.error("Falta la clave de la IA en la configuración de la app.")
            except errors.APIError as e:
                if e.code == 429:
                    st.warning("Se ha agotado la cuota gratuita por ahora. "
                               "Espera un minuto y vuelve a intentarlo.")
                else:
                    st.error(f"El servicio de IA no ha respondido (error {e.code}). "
                             "Inténtalo de nuevo en unos minutos.")
            except json.JSONDecodeError:
                st.error("La IA devolvió algo que no he podido leer. Inténtalo de nuevo.")
            except Exception:
                st.error("Algo ha fallado al procesar la cotización. Inténtalo de nuevo.")

        if filas is not None:
            if not isinstance(filas, list) or not filas or not all(isinstance(f, dict) for f in filas):
                st.warning("No he encontrado datos de cotización en este documento. "
                           "¿Seguro que es una cotización?")
            else:
                st.session_state["df"] = (
                    pd.DataFrame(filas).reindex(columns=CAMPOS).fillna(NO_ENCONTRADO)
                )

    if "df" in st.session_state:
        df = st.session_state["df"]
        st.dataframe(df, hide_index=True)
        st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name="cotizacion.csv", mime="text/csv")
