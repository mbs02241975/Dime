import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Visual 2026", page_icon="📏", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    @media print { [data-testid="stSidebar"], header, .stButton, .stFileUploader { display: none !important; } }
    .relatorio-box { padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #fff; }
    </style>
""", unsafe_allow_html=True)

# 2. Interface Lateral
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Cole sua Gemini API Key:", type="password")

st.title("📏 Dimensionador Automático")

arquivo = st.file_uploader("Suba o projeto (PDF ou Imagem)", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo:
    dados_arquivo = arquivo.read()
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        if arquivo.type == "application/pdf": st.info("📄 PDF pronto para análise.")
        else: st.image(Image.open(io.BytesIO(dados_arquivo)), use_container_width=True)

    if st.button("🚀 Gerar Relatório"):
        if not api_key:
            st.error("Insira a API Key.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # --- TRUQUE PARA EVITAR O ERRO 404 ---
                # Listamos os modelos e pegamos o primeiro que seja 'flash'
                modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                modelo_escolhido = next((m for m in modelos_disponiveis if 'flash' in m), modelos_disponiveis[0])
                
                st.sidebar.write(f"🤖 Usando: {modelo_escolhido}")
                model = genai.GenerativeModel(modelo_escolhido)
                # -------------------------------------

                with st.spinner("IA calculando materiais..."):
                    prompt = "Aja como orçamentista de comunicação visual. Extraia Cliente e Referência. Liste itens e calcule m² (adesivos/lonas), metros lineares (perfis) e m³. Formate em tabela Markdown."
                    
                    resposta = model.generate_content([
                        {"mime_type": arquivo.type, "data": dados_arquivo},
                        prompt
                    ])
                    
                    with col2:
                        st.subheader("📋 Resultado")
                        st.markdown(f'<div class="relatorio-box">{resposta.text}</div>', unsafe_allow_html=True)
                        st.success("✅ Sucesso! Use Ctrl+P para imprimir.")

            except Exception as e:
                st.error(f"Erro: {e}")

else:
    st.info("Aguardando arquivo...")
