import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Insumos - Impressão", page_icon="📏", layout="wide")

# 2. Função para criar o link de impressão (Gera um HTML limpo)
def preparar_impressao(conteudo_html):
    html_folha = f"""
    <html>
    <head>
        <title>Relatório de Produção</title>
        <style>
            body {{ font-family: sans-serif; padding: 40px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1, h2 {{ color: #333; }}
            .no-print {{ display: none; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        {conteudo_html}
        <script>window.print();</script>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_folha.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration:none;"><button style="background-color:#4CAF50; color:white; padding:15px 25px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">📂 Abrir Relatório para Impressão Completa</button></a>'

# 3. Interface
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

st.title("📏 Dimensionador com Impressão A4")

arquivo = st.file_uploader("Suba o projeto", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo:
    dados_arquivo = arquivo.read()
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        if arquivo.type == "application/pdf": st.info("📄 PDF pronto.")
        else: st.image(Image.open(io.BytesIO(dados_arquivo)), use_container_width=True)

    if st.button("🚀 Gerar e Formatar Relatório"):
        if not api_key:
            st.error("Insira a API Key.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                modelo_ok = next((m for m in modelos if 'flash' in m), modelos[0])
                model = genai.GenerativeModel(modelo_ok)

                with st.spinner("Calculando..."):
                    # Pedimos explicitamente para a IA retornar HTML para facilitar a impressão
                    prompt = """
                    Analise o projeto e crie um RELATÓRIO DE PRODUÇÃO EM HTML.
                    Use as tags <h1> para o título, <h3> para o cabeçalho (Cliente, Ref) e <table> para os materiais.
                    Calcule m², metros lineares e m³ conforme as anotações.
                    Não use CSS complexo, apenas HTML puro e limpo.
                    """
                    
                    resposta = model.generate_content([{"mime_type": arquivo.type, "data": dados_arquivo}, prompt])
                    conteudo_final = resposta.text.replace("```html", "").replace("```", "")
                    
                    with col2:
                        st.subheader("📋 Prévia do Relatório")
                        # Mostra no app
                        st.markdown(conteudo_final, unsafe_allow_html=True)
                        
                        st.write("---")
                        # Botão que abre a nova aba para imprimir
                        botao_html = preparar_impressao(conteudo_final)
                        st.markdown(botao_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erro: {e}")
else:
    st.info("Aguardando arquivo...")
