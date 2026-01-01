import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# Configuración de página
st.set_page_config(page_title="Asistente ECE", layout="wide")
st.title("🛠️ Sistema de Elaboración y Revisión de Estándares")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key de Gemini:", type="password")
    modo = st.radio("Función:", ["Revisión de Documentos", "Creación desde Cero"])
    st.divider()
    st.info("Asegúrate de que tu API Key esté activa en Google AI Studio.")

# Detener si no hay API Key
if not api_key:
    st.warning("⚠️ Ingresa tu API Key para continuar.")
    st.stop()

# Configuración Robusta del Modelo
try:
    genai.configure(api_key=api_key)
    # Intentamos con el modelo más común, si falla, el código avisará
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")

def extraer_texto(archivo):
    try:
        pdf = PyPDF2.PdfReader(archivo)
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
        return texto.strip()
    except Exception as e:
        st.error(f"Error al leer PDF: {e}")
        return None

def generar_word(texto):
    doc = Document()
    doc.add_heading('Resultado de Competencias Laborales', 0)
    doc.add_paragraph(texto)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- INTERFAZ ---
archivo_estandar = st.file_uploader("1. Sube el Estándar de Competencia (PDF)", type="pdf")

if archivo_estandar:
    texto_estandar = extraer_texto(archivo_estandar)
    
    if texto_estandar:
        st.success("✅ Estándar cargado.")

        if modo == "Revisión de Documentos":
            archivo_doc = st.file_uploader("2. Sube el Documento a Revisar (PDF)", type="pdf")
            if archivo_doc and st.button("🔍 Auditar"):
                texto_u = extraer_texto(archivo_doc)
                with st.spinner("Analizando..."):
                    try:
                        p = f"Compara este documento con el estándar: {texto_estandar[:3000]}. Documento: {texto_u[:3000]}. Crea una tabla de cumplimiento (Elemento, Estado, Observación, Mejora)."
                        res = model.generate_content(p)
                        st.markdown(res.text)
                        st.download_button("Descargar Word", generar_word(res.text), "Auditoria.docx")
                    except Exception as e:
                        st.error("Error de conexión con la IA. Verifica que tu API Key sea correcta o intenta más tarde.")

        elif modo == "Creación desde Cero":
            if st.button("📝 Generar Preguntas"):
                with st.spinner("Preparando entrevista..."):
                    try:
                        p_preg = f"Basado en este estándar: {texto_estandar[:3000]}, haz 5 preguntas para redactar los productos requeridos."
                        res = model.generate_content(p_preg)
                        st.session_state['entrevista'] = res.text
                    except Exception as e:
                        st.error("La IA no pudo generar preguntas. Verifica tu API Key.")

            if 'entrevista' in st.session_state:
                st.markdown("### Contesta lo siguiente:")
                st.info(st.session_state['entrevista'])
                respuestas = st.text_area("Tus respuestas:")
                
                if st.button("✨ Generar Producto Final"):
                    if respuestas:
                        with st.spinner("Redactando..."):
                            try:
                                p_fin = f"Crea una TABLA técnica profesional con Productos, Desempeños y Valores usando este estándar: {texto_estandar[:2000]} y estas respuestas: {respuestas}"
                                final = model.generate_content(p_fin)
                                st.markdown(final.text)
                                st.download_button("Descargar Word", generar_word(final.text), "Producto_Final.docx")
                            except Exception as e:
                                st.error("Error al redactar el documento.")
                    else:
                        st.warning("Escribe las respuestas primero.")
else:
    st.info("Esperando PDF del Estándar...")
