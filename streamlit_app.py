import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Asistente de Competencias Laborales", layout="wide")

st.title("🛠️ Sistema de Elaboración y Revisión de Estándares")
st.markdown("Carga un estándar en PDF para comenzar a trabajar.")

# Sidebar para configuración
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key de Gemini:", type="password")
    modo = st.radio("Selecciona una función:", ["Revisión de Documentos", "Creación desde Cero (Entrevista)"])
    st.info("Nota: Primero debes subir el PDF del Estándar en la pantalla principal.")

if not api_key:
    st.warning("⚠️ Por favor, ingresa tu API Key de Google AI Studio para activar el cerebro de la app.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def extraer_texto_pdf(archivo_pdf):
    try:
        lector = PyPDF2.PdfReader(archivo_pdf)
        texto = ""
        for pagina in lector.pages:
            texto += pagina.extract_text()
        return texto
    except:
        return ""

def crear_word(contenido):
    doc = Document()
    doc.add_heading('Resultado del Análisis de Competencias', 0)
    doc.add_paragraph(contenido)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- FLUJO PRINCIPAL ---
archivo_estandar = st.file_uploader("📂 1. Sube el Estándar de Competencia (PDF)", type="pdf")

if archivo_estandar:
    texto_estandar = extraer_texto_pdf(archivo_estandar)
    st.success("✅ Estándar cargado y listo.")

    if modo == "Revisión de Documentos":
        archivo_usuario = st.file_uploader("📄 2. Sube el Documento que quieres que revise (PDF)", type="pdf")
        
        if archivo_usuario:
            texto_usuario = extraer_texto_pdf(archivo_usuario)
            if st.button("🔍 Iniciar Auditoría"):
                with st.spinner("Analizando cumplimiento..."):
                    prompt_revision = f"Actúa como auditor de CONOCER. Compara este documento: {texto_usuario[:4000]} contra este estándar: {texto_estandar[:4000]}. Genera una tabla con Elemento, Estado (Cumple/No), Observación y Sugerencia."
                    response = model.generate_content(prompt_revision)
                    st.markdown(response.text)
                    st.download_button("Descargar Informe en Word", crear_word(response.text), "Revision.docx")

    elif modo == "Creación desde Cero (Entrevista)":
        if st.button("📝 Generar Preguntas de Diagnóstico"):
            with st.spinner("Leyendo estándar..."):
                prompt_preguntas = f"Basado en este estándar: {texto_estandar[:4000]}, genera 5 preguntas clave para que el usuario me dé información para redactar los productos y desempeños."
                preguntas = model.generate_content(prompt_preguntas)
                st.session_state['preguntas'] = preguntas.text

        if 'preguntas' in st.session_state:
            st.markdown("### Responde estas preguntas:")
            st.info(st.session_state['preguntas'])
            respuestas_usuario = st.text_area("Escribe aquí tus respuestas detalladas:")
            
            if st.button("✨ Redactar Documento Final"):
                if respuestas_usuario:
                    with st.spinner("Redactando tabla técnica..."):
                        prompt_final = f"Basado en el estándar {texto_estandar[:2000]} y estas respuestas: {respuestas_usuario}, crea una TABLA técnica que incluya Productos, Desempeños y Actitudes. Formato profesional."
                        resultado_final = model.generate_content(prompt_final)
                        st.markdown(resultado_final.text)
                        st.download_button("Descargar Documento en Word", crear_word(resultado_final.text), "Producto_Final.docx")
                else:
                    st.error("Por favor, escribe tus respuestas primero.")
else:
    st.info("Esperando que subas el archivo PDF del Estándar para comenzar...")
