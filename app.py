import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Configuração da Página
st.set_page_config(page_title="PXG Wiki Helper", page_icon="🎮")
st.title("🎮 PXG Wiki AI Assistant")

# --- LÓGICA DE API KEY ---
api_key = os.environ.get('GOOGLE_API_KEY') or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.warning("⚠️ API Key não encontrada nos segredos.")
    api_key = st.sidebar.text_input("Insira sua Google API Key:", type="password")
    if not api_key:
        st.info("Aguardando chave para liberar o chat...")

# --- FUNÇÕES DE BUSCA ---
def buscar_na_wiki(query):
    search_query = query.replace(' ', '+')
    search_url = f"https://wiki.pokexgames.com/index.php?search={search_query}"
    try:
        response = requests.get(search_url, timeout=10)
        if "index.php/" in response.url and not "search=" in response.url:
            return extrair_conteudo(response.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link = soup.find('div', class_='mw-search-result-heading')
        if first_link and first_link.find('a'):
            full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
            return extrair_conteudo(full_link)
    except:
        return "Erro na busca."
    return "Não encontrado."

def extrair_conteudo(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Removendo elementos (Versão em uma linha para evitar erro de indentação)
        [s.decompose() for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'table.navbox'])]
        content = soup.find('div', id='mw-content-text')
        return content.get_text(separator='\n', strip=True)[:8000] if content else "Vazio."
    except:
        return "Erro ao extrair."

# --- INTERFACE DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pergunte algo sobre PXG..."):
    if not api_key:
        st.error("Você precisa de uma API Key para enviar mensagens!")
    else:
        client = genai.Client(api_key=api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando Wiki..."):
                contexto = buscar_na_wiki(prompt)
                ai_prompt = f"Você é um tutor de PXG. Contexto da Wiki: {contexto}. Pergunta: {prompt}"
                try:
                    response = client.models.generate_content(model="gemini-2.0-flash", contents=ai_prompt)
                    full_response = response.text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
