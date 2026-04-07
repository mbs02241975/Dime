import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Insumos - C&A", page_icon="📏", layout="wide")

# 2. Interface Lateral
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

st.title("📏 Dimensionador de Produção")

arquivo = st.file_uploader("Suba o projeto (PDF ou Imagem)", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo:
    dados_arquivo = arquivo.read()
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        if arquivo.type == "application/pdf": st.info("📄 PDF pronto para análise.")
        else: st.image(Image.open(io.BytesIO(dados_arquivo)), use_container_width=True)

    if st.button("🚀 Gerar Relatório"):
        if not api_key:
            st.error("Insira a API Key.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                modelo_ok = next((m for m in modelos if 'flash' in m), modelos[0])
                model = genai.GenerativeModel(modelo_ok)

                with st.spinner("IA Processando o Projeto C&A..."):
                    prompt = """
                    Analise o projeto e crie um RELATÓRIO DE PRODUÇÃO EM HTML.
                    REGRAS:
                    - Retorne APENAS o código HTML, sem as tags de bloco de código (```html).
                    - Use <h1> para o título principal.
                    - Use tabelas HTML com bordas (border='1') para os itens.
                    - Calcule m², metros lineares e m³.
                    - Inclua uma seção de 'Notas' ao final.
                    - Estilize o HTML com uma fonte limpa (Arial/Sans-serif).
                    """
                    
                    resposta = model.generate_content([{"mime_type": arquivo.type, "data": dados_arquivo}, prompt])
                    
                    # Limpeza de possíveis formatações de texto da IA
                    conteudo_html = resposta.text.replace("```html", "").replace("```", "").strip()
                    
                    # Montagem do HTML completo para o arquivo de impressão
                    html_completo = f"""
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 30px; }}
                            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; font-size: 12px; }}
                            th {{ background-color: #eee; }}
                            h1 {{ color: #d32f2f; }}
                        </style>
                    </head>
                    <body>
                        {conteudo_html}
                    </body>
                    </html>
                    """

                    with col2:
                        st.subheader("📋 Relatório Gerado")
                        # Renderiza o HTML na tela do Streamlit corretamente
                        st.components.v1.html(html_completo, height=600, scrolling=True)
                        
                        st.write("---")
                        
                        # Botão de Download (Substitui o abrir janela que dava erro)
                        st.download_button(
                            label="📥 Baixar Relatório para Imprimir",
                            data=html_completo,
                            file_name="relatorio_producao.html",
                            mime="text/html"
                        )
                        st.success("Clique no botão acima para baixar o arquivo. Depois, abra-o e use Ctrl+P.")

            except Exception as e:
                st.error(f"Erro: {e}")
else:
    st.info("Aguardando arquivo para iniciar...")
