import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuração de Página e Estilos
st.set_page_config(page_title="Dimensionador Visual 2026", page_icon="📏", layout="wide")

# CSS para evitar erros de renderização e preparar o layout de impressão
st.markdown("""
    <style>
    /* Esconde elementos do Streamlit na impressão (Ctrl+P) */
    @media print {
        [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, .stFileUploader {
            display: none !important;
        }
        .main .block-container { max-width: 100% !important; padding: 0 !important; }
    }
    .relatorio-box {
        padding: 25px;
        border: 2px solid #eee;
        border-radius: 15px;
        background-color: #ffffff;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Barra Lateral (Segurança e Configuração)
st.sidebar.title("🛠️ Painel de Controle")
api_key = st.sidebar.text_input("Cole sua Gemini API Key:", type="password")
st.sidebar.markdown("---")
st.sidebar.info("💡 Dica: No plano gratuito, evite subir muitos arquivos simultâneos.")

# 3. Área Principal
st.title("📏 Dimensionador Automático de Comunicação Visual")
st.write("Converta rascunhos, fotos e PDFs em tabelas de insumos instantâneas.")

arquivo = st.file_uploader("Suba o arquivo do projeto", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo:
    # Lendo o arquivo uma única vez para evitar erros de ponteiro
    dados_arquivo = arquivo.read()
    
    col_previa, col_analise = st.columns([1, 1.3])
    
    with col_previa:
        st.subheader("🖼️ Prévia do Arquivo")
        if arquivo.type == "application/pdf":
            st.success("✅ PDF carregado. A IA lerá todas as especificações.")
        else:
            img = Image.open(io.BytesIO(dados_arquivo))
            st.image(img, use_container_width=True)

    # Botão de Ação
    if st.button("🚀 Gerar Orçamento e Materiais"):
        if not api_key:
            st.warning("⚠️ Você precisa inserir a chave API na lateral.")
        else:
            try:
                # Configurando a versão mais atual do modelo disponível em 2026
                genai.configure(api_key=api_key)
                # 'gemini-1.5-flash' é o mais estável, mas o código tenta o mais recente disponível
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner("Inteligência Artificial analisando medidas..."):
                    prompt = """
                    Você é um especialista em produção de comunicação visual.
                    Instruções:
                    1. Identifique Cliente, Data e Referência no topo.
                    2. Extraia todos os itens e calcule:
                       - Metragem Quadrada ($m^2$): Lonas, adesivos, ACM, chapas (Largura x Altura).
                       - Metragem Linear ($m$): Cantoneiras, eletrodutos, fitas LED, metalon.
                       - Volume ($m^3$): Para totens ou estruturas de grande porte.
                    3. Formate tudo em uma TABELA MARKDOWN clara.
                    
                    Se for um rascunho à mão, interprete os números e dimensões com base no contexto do produto.
                    """
                    
                    # Envio multimodal (imagem/pdf + texto)
                    resposta = model.generate_content([
                        {"mime_type": arquivo.type, "data": dados_arquivo},
                        prompt
                    ])
                    
                    with col_analise:
                        st.subheader("📋 Relatório Final")
                        # Usando um container simples para evitar o erro de 'removeChild'
                        st.markdown(f'<div class="relatorio-box">{resposta.text}</div>', unsafe_allow_html=True)
                        st.success("Tudo pronto! Use Ctrl + P para salvar ou imprimir este relatório.")

            except Exception as e:
                st.error(f"Erro no sistema: {e}")
                st.info("Tente usar o modelo 'gemini-1.5-flash' se o erro for 404.")

else:
    st.info("Aguardando arquivo para iniciar...")
