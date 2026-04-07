import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configuração da página para um visual mais limpo
st.set_page_config(page_title="Dimensionador Visual", page_icon="📏", layout="wide")

# CSS para esconder elementos desnecessários na hora de imprimir
st.markdown("""
    <style>
    @media print {
        .stButton, .stFileUploader, .stSidebar, header, .stCallout {
            display: none !important;
        }
        .main { width: 100% !important; padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# Interface Lateral
st.sidebar.title("🚀 Configuração")
# Dica: No Streamlit Cloud, você pode salvar isso em 'Secrets' como GEMINI_API_KEY
user_key = st.sidebar.text_input("Nova Gemini API Key:", type="password")

st.title("📏 Calculador Automático de Materiais")
st.write("Transforme PDFs, fotos de rascunhos ou projetos em relatórios de insumos prontos para impressão.")

# Upload do arquivo
arquivo_projeto = st.file_uploader("Suba seu PDF, Foto ou Rascunho", type=['pdf', 'jpg', 'jpeg', 'png'])

if arquivo_projeto:
    conteudo_arquivo = arquivo_projeto.read()
    
    col_previa, col_resultado = st.columns([1, 1.2])
    
    with col_previa:
        st.subheader("🖼️ Arquivo Carregado")
        if arquivo_projeto.type == "application/pdf":
            st.info("📄 PDF detectado. A inteligência analisará todas as páginas do documento.")
        else:
            imagem = Image.open(io.BytesIO(conteudo_arquivo))
            st.image(imagem, caption="Visualização do Projeto", use_container_width=True)

    if st.sidebar.button("Calcular Materiais"):
        if not user_key:
            st.error("⚠️ Por favor, insira uma API Key válida na barra lateral.")
        else:
            try:
                # Configuração da IA
                genai.configure(api_key=user_key)
                # Usando o nome do modelo mais estável para evitar o erro 404
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                with st.spinner("Analisando dimensões e rascunhos..."):
                    # Prompt especializado para o seu negócio
                    prompt_tecnico = """
                    Aja como um especialista em orçamento para comunicação visual.
                    Sua tarefa é ler este arquivo (que pode ser um PDF técnico ou um rascunho manual) e:
                    
                    1. IDENTIFICAR: O cabeçalho com nome do cliente, referência e data.
                    2. CALCULAR: 
                       - Área total em $m^2$ para adesivos, lonas ou placas.
                       - Comprimento em metros (m) para perfis de alumínio, metalon ou fitas LED.
                       - Volume em $m^3$ se houver estruturas volumétricas (como totens).
                    3. FORMATAR: Crie um relatório limpo com o cabeçalho no topo e uma TABELA de itens.
                    
                    Se o rascunho estiver difícil de ler, use sua inteligência para deduzir as medidas mais lógicas baseadas no contexto (ex: um banner de '300x100' provavelmente é 3m x 1m).
                    """
                    
                    # Preparação do conteúdo para a API
                    partes_mensagem = [
                        {"mime_type": arquivo_projeto.type, "data": conteudo_arquivo},
                        prompt_tecnico
                    ]
                    
                    relatorio = model.generate_content(partes_mensagem)
                    
                    with col_resultado:
                        st.subheader("📋 Relatório de Insumos")
                        st.markdown(relatorio.text)
                        
                        # Botão de impressão (JavaScript)
                        st.button("🖨️ Imprimir agora", on_click=lambda: st.write('<script>window.print();</script>', unsafe_allow_html=True))
                        
            except Exception as e:
                st.error(f"Ocorreu um erro técnico: {e}")
                st.info("Dica: Verifique se sua nova chave tem permissão para o modelo Gemini 1.5 Flash.")

else:
    st.info("💡 Dica: Você pode tirar uma foto de um rascunho de papel e subir aqui para converter em relatório.")
