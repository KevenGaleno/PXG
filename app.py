import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import re

st.set_page_config(page_title="PokéX Wiki IA", page_icon="🎮", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding:3rem; background:linear-gradient(45deg,#FF6B6B,#4ECDC4); 
color:white; border-radius:25px; margin-bottom:2rem'>
    <h1 style='margin:0;'>🤖 PokéX Wiki IA</h1>
    <p style='margin:0;'>Busca <b>REAL</b> na wiki.pokexgames.com</p>
</div>
""", unsafe_allow_html=True)

class PokexWikiAI:
    def __init__(self):
        self.base_url = "https://wiki.pokexgames.com"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def buscar_wiki(self, termo):
        try:
            search_url = f"{self.base_url}/index.php?search={quote(termo)}"
            resp = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            resultados = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'title=' in href and termo.lower() in link.get_text().lower():
                    pagina_url = urljoin(self.base_url, href)
                    conteudo = self.extrair_conteudo(pagina_url)
                    if conteudo:
                        resultados.append({
                            'titulo': link.get_text().strip(),
                            'url': pagina_url,
                            'conteudo': conteudo
                        })
                    if len(resultados) >= 2:
                        break
            return resultados
        except:
            return []
    
    def extrair_conteudo(self, url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            conteudo = soup.find('div', {'id': 'mw-content-text'})
            if conteudo:
                texto = re.sub(r'\s+', ' ', conteudo.get_text()).strip()
                return texto[:1000] + "..." if len(texto) > 1000 else texto
            return ""
        except:
            return ""

# Inicializar
if 'ai' not in st.session_state:
    st.session_state.ai = PokexWikiAI()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("🔍 Digite: 'como funciona a NW', 'shiny', 'mega pedra'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔎 Buscando na Wiki PokéX..."):
            resultados = st.session_state.ai.buscar_wiki(prompt)
        
        if resultados:
            for i, result in enumerate(resultados):
                st.markdown(f"**{result['titulo']}**")
                st.markdown(f"📄 {result['conteudo']}")
                st.markdown(f"[🔗 Abrir na Wiki]({result['url']})")
                st.markdown("---")
        else:
            st.markdown("❓ Não encontrei na wiki. Tente: 'NW', 'shiny', 'PvP', 'mega pedra'")
    
    st.session_state.messages.append({"role": "assistant", "content": "Resposta gerada"})

# Sidebar dicas
with st.sidebar:
    st.markdown("### 💡 **Teste estes:**")
    testes = ["como funciona a NW", "shiny", "mega pedra", "PvP", "IVs"]
    for teste in testes:
        if st.button(teste):
            st.session_state.messages.append({"role": "user", "content": teste})
            st.rerun()
