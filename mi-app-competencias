import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Asistente de Competencias Laborales", layout="wide")

st.title("🛠️ Sistema de Elaboración y Revisión de Estándares")
st.markdown("Carga un estándar en PDF para comenzar a revisar o crear documentos técnicos.")

# Sidebar para configuración
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key de Gemini:", type="password")
    modo = st.radio("Selecciona una función:", ["Revisión de Documentos", "Creación desde Cero (Entrevista)"])

if not api_key:
    st.warning("Por favor, ingresa tu API Key de Google AI Studio en la barra lateral para continuar.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def extraer_texto_pdf(archivo_pdf):
    lector = PyPDF2.PdfReader(archivo_pdf)
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    return texto

def crear_word(contenido):
    doc = Document()
    doc.add_heading('Resultado del Análisis de Competencias', 0)
    doc.add_paragraph(contenido)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- FLUJO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    archivo_estandar = st.file_uploader("1. Sube el Estándar de Competencia (PDF)", type="pdf")

if archivo_estandar:
    texto_estandar = extraer_texto_pdf(archivo_estandar)
    st.success("Estándar cargado correctamente.")

    if modo == "Revisión de Documentos":
        with col2:
            archivo_usuario = st.file_uploader("2. Sube el Documento a Revisar (PDF)", type="pdf")
        
        if archivo_usuario:
            texto_usuario = extraer_texto_pdf(archivo_usuario)
            if st.button("Iniciar Auditoría"):
                with st.spinner("Analizando cumplimiento..."):
                    prompt_revision = f"""
                    Actúa como un auditor experto en estándares de competencia laboral. 
                    Compara el DOCUMENTO DEL USUARIO con el ESTÁNDAR DE COMPETENCIA proporcionado.
                    
                    ESTÁNDAR: {texto_estandar[:4000]}
                    DOCUMENTO USUARIO: {texto_usuario[:4000]}
                    
                    Genera una respuesta que contenga ÚNICAMENTE una tabla con:
                    1. Elemento del Estándar (Productos/Desempeños).
                    2. Estado (Cumple / No Cumple / Parcial).
                    3. Observación técnica del por qué.
                    4. Sugerencia de corrección profesional.
                    """
                    response = model.generate_content(prompt_revision)
                    st.markdown("### Tabla de Resultados")
                    st.markdown(response.text)
                    
                    # Botón de descarga
                    word_data = crear_word(response.text)
                    st.download_button("Descargar Informe en Word", word_data, "Revision_Competencias.docx")

    elif modo == "Creación desde Cero (Entrevista)":
        st.info("La IA analizará el estándar y te hará preguntas para generar el producto.")
        if st.button("Generar Preguntas de Diagnóstico"):
            with st.spinner("Generando entrevista..."):
                prompt_preguntas = f"Basado en este estándar: {texto_estandar[:4000]}, genera 5 preguntas clave para que el usuario me dé la información necesaria para redactar los 'Productos' y cumplir con 'Desempeños y Valores'."
                preguntas = model.generate_content(prompt_preguntas)
                st.session_state['preguntas'] = preguntas.text

        if 'preguntas' in st.session_state:
            st.markdown(st.session_state['preguntas'])
            respuestas_usuario = st.text_area("Pega aquí tus respuestas a las preguntas anteriores:")
            
            if st.button("Redactar Documento Final"):
                with st.spinner("Redactando documento técnico..."):
                    prompt_final = f"""
                    Utilizando el ESTÁNDAR: {texto_estandar[:2000]} 
                    Y las RESPUESTAS DEL USUARIO: {respuestas_usuario}
                    
                    Redacta un documento técnico formal. Organiza la información en una TABLA profesional que incluya los apartados de:
                    - Productos (con su descripción técnica)
                    - Desempeños asociados
                    - Actitudes/Hábitos/Valores aplicados
                    Asegúrate de que cumpla con cada punto solicitado por el estándar.
                    """
                    resultado_final = model.generate_content(prompt_final)
                    st.markdown("### Documento Sugerido")
                    st.markdown(resultado_final.text)
                    
                    word_data = crear_word(resultado_final.text)
                    st.download_button("Descargar Documento en Word", word_data, "Producto_Competencias.docx")
