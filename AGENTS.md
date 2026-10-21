# AGENTS.md

## Qué es este proyecto
App en Streamlit que lee cotizaciones de proveedores en PDF y extrae sus datos clave en una tabla. Proyecto individual del reto del módulo Python para IA.

## Cómo se ejecuta
- Instalar: `pip install -r requirements.txt`
- Ejecutar: `streamlit run app.py`

## Convenciones
- Python con type hints y docstrings cortos.
- Mensajes de la interfaz en español, claros para alguien sin perfil técnico.
- Funciones pequeñas: una para leer el PDF, otra para extraer los datos, otra para mostrar resultados.
- Si un dato no aparece en el documento, devolver "No encontrado". Nunca inventarlo.
- Los errores se muestran con st.error o st.warning, no con trazas en rojo.

## No tocar
- Nunca escribir claves de API en el código. Usar st.secrets.
- No subir ni usar documentos reales, solo cotizaciones de ejemplo inventadas.
- No guardar los archivos que sube el usuario.
- No añadir dependencias sin avisar.
