import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuração da Página
st.set_page_config(page_title="Dimensionador Visual Pro", page_icon="📏", layout="wide")

# 2. CSS para melhorar a visualização e preparar para impressão (Ctrl + P)
st.markdown("""
    <style>
    @media print {
        .stButton, .stFileUploader, .stSidebar, header, .stCallout, [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
    }
    .report-container {
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Interface Lateral
st.sidebar.title("⚙️ Configurações")
st.sidebar.write("Configure sua chave para começar.")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")
st.sidebar.info("Obtenha sua chave no [Google AI Studio](https://aistudio.google.com/)")

# 4. Corpo do Aplicativo
st.title("📏 Dimensionador Automático de Insumos")
st.write("Envie fotos de rascunhos, imagens de projetos ou PDFs para calcular as quantidades.")

arquivo = st.file_uploader("Carregar Projeto (PDF, JPG, PNG)", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo:
    conteudo_bytes = arquivo.read()
    
    col_img, col_relat = st.columns([1, 1.2])
    
    with col_img:
        st.subheader("🖼️ Visualização")
        if arquivo.type == "application/pdf":
            st.info("📄 Documento PDF carregado com sucesso.")
        else:
            img_exibicao = Image.open(io.BytesIO(conteudo_bytes))
            st.image(img_exibicao, caption="Projeto enviado", use_container_width=True)

    # Botão para processar
    if st.button("🚀 Gerar Relatório de Materiais"):
        if not api_key:
            st.error("⚠️ Insira a API Key na barra lateral antes de continuar.")
        else:
            try:
                # Configurando a IA com o modelo mais estável
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                with st.spinner("Analisando rascunhos e calculando medidas..."):
                    prompt = """
                    Você é um orçamentista técnico de comunicação visual. 
                    Analise o arquivo enviado e:
                    1. Extraia o cabeçalho: Cliente, Referência e Data.
                    2. Liste os itens encontrados e calcule:
                       - Metragem quadrada (m²) para lonas, adesivos e chapas (Ex: 2x1m = 2m²).
                       - Metros lineares (m) para perfis, estruturas e acabamentos.
                       - Metros cúbicos (m³) apenas se houver volumes 3D.
                    3. Se for um rascunho manual, interprete as anotações da melhor forma possível.
                    
                    Formate a resposta como um RELATÓRIO DE PRODUÇÃO, usando tabelas para os materiais.
                    """
                    
                    # Preparando dados para envio
                    partes = [{"mime_type": arquivo.type, "data": conteudo_bytes}, prompt]
                    resultado = model.generate_content(partes)
                    
                    with col_relat:
                        st.subheader("📋 Relatório Gerado")
                        st.markdown(f'<div class="report-container">{resultado.text}</div>', unsafe_allow_html=True)
                        st.success("✅ Relatório pronto! Para imprimir, use Ctrl + P no teclado.")
                        
            except Exception as e:
                st.error(f"Erro no processamento: {e}")
                st.info("Dica: Verifique se sua API Key é válida e se você tem acesso ao modelo Gemini 1.5 Flash.")

else:
    st.info("Aguardando upload de um arquivo para iniciar o cálculo.")
