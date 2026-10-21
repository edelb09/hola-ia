import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="Lector de cotizaciones", page_icon="📄")
st.title("Lector de Quotes 📄")
st.write("Sube una cotización en PDF y verás el texto que se puede leer de ella. "
         "Esta es la versión 0, todavía sin IA.")
st.caption("Usa solo documentos de ejemplo, nunca cotizaciones reales.")

archivo = st.file_uploader("Cotización en PDF", type=["pdf"])

if archivo is not None:
    try:
        lector = PdfReader(archivo)
        paginas = [(p.extract_text() or "").strip() for p in lector.pages]
    except Exception:
        st.error("No he podido abrir el archivo. Comprueba que es un PDF válido.")
        st.stop()

    texto = "\n\n".join(t for t in paginas if t)

    if not texto:
        st.warning("Este PDF no tiene texto legible, parece una imagen escaneada. "
                   "Prueba con un PDF generado desde un programa.")
    else:
        st.success(f"PDF leído: {len(lector.pages)} página(s).")
        st.text_area("Texto extraído", texto, height=400)
