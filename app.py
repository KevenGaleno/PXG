import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Configuração da Página
st.set_page_config(page_title="PXG Wiki Helper", page_icon="🎮")
st.title("🎮 PXG Wiki AI Assistant")

# --- LÓGICA DE API KEY ---
# Tenta buscar nos Secrets do Streamlit ou do Replit primeiro
api_key = os.environ.get('GOOGLE_API_KEY') or st.secrets.get("GOOGLE_API_KEY")

# Se não encontrar nos segredos, cria um campo na barra lateral para o usuário inserir
if not api_key:
    st.sidebar.warning("API Key não detectada nos segredos do sistema.")
    api_key = st.sidebar.text_input("Insira sua Google API Key:", type="password")
    if not api_key:
        st.info("💡 Por favor, insira sua API Key na barra lateral para começar ou configure os Secrets do projeto.")
        st.stop()

# Inicializa o cliente da IA com a chave obtida
client = genai.Client(api_key=api_key)
BASE_URL = "https://wiki.pokexgames.com/index.php"

# --- FUNÇÕES DE BUSCA ---
def buscar_na_wiki(query):
    search_query = query.replace(' ', '+')
    search_url = f"{BASE_URL}?search={search_query}"
    try:
        response = requests.get(search_url, timeout=10)
        # Se redirecionar direto para a página
        if "index.php/" in response.url and not "search=" in response.url:
            return extrair_conteudo(response.url)
        
        # Se cair nos resultados da busca
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link = soup.find('div', class_='mw-search-result-heading')
        if first_link and first_link.find('a'):
            full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
            return extrair_conteudo(full_link)
    except Exception as e:
        return f"Erro ao acessar a Wiki: {e}"
    return "Não encontrei informações específicas na Wiki sobre este termo."

def extrair_conteudo(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Limpeza de elementos desnecessários
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'table.navbox']):
            element.decompose()  # <--- ESTA LINHA PRECISA DE 4 ESPAÇOS A MAIS QUE O FOR
        
        content = soup.find('div', id='mw-content-text')
        return content.get_text(separator='\n', strip=True)[:8000] if content else "Página sem conteúdo legível."
    except:
        return "Erro ao extrair dados da página."
