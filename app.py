import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Configuração da Página
st.set_page_config(page_title="PXG Wiki Helper", page_icon="🎮")
st.title("🎮 PXG Wiki AI Assistant")

# Configuração da API Key (No Streamlit Cloud, use Advanced Settings > Secrets)
api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    st.error("API Key não encontrada! Configure a variável GOOGLE_API_KEY.")
    st.stop()

client = genai.Client(api_key=api_key)
BASE_URL = "https://wiki.pokexgames.com/index.php"

# Funções de busca (as mesmas que você já usa)
def buscar_na_wiki(query):
    search_query = query.replace(' ', '+')
    search_url = f"{BASE_URL}?search={search_query}"
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
        return "Erro ao acessar a Wiki."
    return "Não encontrado."

def extrair_conteudo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    content = soup.find('div', id='mw-content-text')
    return content.get_text(separator='\n', strip=True)[:8000] if content else "Vazio."

# Interface de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do Usuário
if prompt := st.chat_input("Pergunte algo sobre PXG..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a Wiki..."):
            contexto = buscar_na_wiki(prompt)
            
            ai_prompt = f"Você é um tutor de PXG. Use o contexto da Wiki: {contexto}. Pergunta: {prompt}"
            
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=ai_prompt
            )
            
            full_response = response.text
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
