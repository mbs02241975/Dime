import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configuração da página
st.set_page_config(page_title="Calculador Visual Pro", page_icon="📏", layout="wide")

# Estilo CSS para esconder elementos na impressão
st.markdown("""
    <style>
    @media print {
        .stButton, .stFileUploader, .stSidebar, header {
            display: none !important;
        }
        .main {
            width: 100% !important;
            padding: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Interface Lateral (Configurações)
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Insira sua Gemini API Key:", type="password")
st.sidebar.info("Obtenha sua chave gratuita no [Google AI Studio](https://aistudio.google.com/)")

st.title("📏 Dimensionador de Projetos - Com. Visual")
st.write("Suba um PDF, foto ou rascunho para calcular materiais automaticamente.")

# Upload de arquivo
uploaded_file = st.file_uploader("Arraste o arquivo aqui (PDF, JPG, PNG)", type=['pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file:
    # Preparar a imagem/arquivo para o Gemini
    image_data = uploaded_file.read()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Visualização")
        if uploaded_file.type == "application/pdf":
            st.warning("📄 PDF carregado. A IA analisará o documento completo.")
        else:
            st.image(image_data, use_container_width=True)

    if st.button("🚀 Calcular e Gerar Relatório"):
        if not api_key:
            st.error("Por favor, insira a API Key na barra lateral.")
        else:
            try:
                genai.configure(api_key=api_key)
                # Trecho para listar modelos (apenas para teste)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                with st.spinner("Analisando projeto e calculando insumos..."):
                    # Prompt especializado para Comunicação Visual
                    prompt = """
                    Analise este arquivo de projeto de comunicação visual. 
                    1. Extraia os dados do cabeçalho: Nome do Cliente, Referência do Projeto e Data (se houver).
                    2. Identifique todos os itens/peças.
                    3. Calcule as quantidades necessárias:
                       - Metros quadrados (m²) para adesivos, lonas, chapas.
                       - Metros lineares (m) para perfis, metalon, fiação.
                       - Metros cúbicos (m³) se houver volumes grandes (ex: totens com preenchimento).
                    4. Apresente o resultado final em um formato de RELATÓRIO PROFISSIONAL E LIMPO.
                    Use tabelas Markdown para os itens e destaque os totais.
                    """
                    
                    # Envio para a IA (Trata PDF ou Imagem)
                    content = [{"mime_type": uploaded_file.type, "data": image_data}, prompt]
                    response = model.generate_content(content)
                    
                    with col2:
                        st.subheader("📋 Relatório de Materiais")
                        st.markdown(response.text)
                        
                        # Botão de Impressão (Aciona o print do navegador)
                        st.button("🖨️ Imprimir Relatório", on_click=lambda: st.write('<script>window.print();</script>', unsafe_allow_html=True))
                        
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

else:
    st.info("Aguardando upload de projeto para iniciar.")
