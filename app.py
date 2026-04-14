import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import re

st.set_page_config(page_title="PokéX Wiki IA", page_icon="🎮", layout="wide")

# Tema
st.markdown("""
<style>
.main {background-color: #0E1117}
</style>
""", unsafe_allow_html=True)

st.title("🤖 PokéX Wiki IA - Busca REAL")
st.markdown("*Teste: 'NW', 'shiny', 'mega', 'PvP', 'IVs'*")

class PokexScraper:
    def __init__(self):
        self.base = "https://wiki.pokexgames.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def debug_busca(self, termo):
        """DEBUG - mostra o que a wiki retorna"""
        try:
            url = f"{self.base}/index.php?search={quote(termo)}"
            print(f"🔍 URL: {url}")
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # DEBUG: todos links com title=
            links = soup.find_all('a', href=re.compile(r'title='))
            print(f"📋 Encontrou {len(links)} links:")
            for i, link in enumerate(links[:5]):
                print(f"  {i+1}. {link.text.strip()} -> {link['href']}")
            
            return links
        except Exception as e:
            print(f"ERRO: {e}")
            return []
    
    def buscar_real(self, termo):
        """Busca robusta - acha QUALQUER coisa"""
        try:
            # Método 1: Search direto
            search_url = f"{self.base}/index.php?search={quote(termo)}"
            resp = requests.get(search_url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            resultados = []
            
            # Tenta múltiplos seletores
            containers = (
                soup.find_all('div', class_=re.compile('result')) or
                soup.find_all('li') or
                soup.find_all('div', class_='searchresult') or
                soup.find_all('a', href=re.compile(r'title='))
            )
            
            for item in containers[:5]:
                link = item.find('a', href=True)
                if link and 'title=' in link['href']:
                    pagina_url = urljoin(self.base, link['href'])
                    conteudo = self.get_conteudo(pagina_url)
                    if conteudo:
                        resultados.append({
                            'titulo': link.get_text().strip()[:100],
                            'url': pagina_url,
                            'conteudo': conteudo[:600]
                        })
            
            # Método 2: Guess página direta
            if not resultados:
                guess_pages = [
                    f"{self.base}/index.php/{quote(termo.replace(' ', '_'))}",
                    f"{self.base}/index.php/{quote(termo.title())}"
                ]
                for guess in guess_pages:
                    conteudo = self.get_conteudo(guess)
                    if conteudo:
                        resultados.append({
                            'titulo': f"Página: {termo}",
                            'url': guess,
                            'conteudo': conteudo[:600]
                        })
                        break
            
            return resultados
            
        except Exception as e:
            return [{'titulo': 'Erro técnico', 'conteudo': f'Falha na conexão: {str(e)}'}]
    
    def get_conteudo(self, url):
        """Extrai conteúdo de qualquer página wiki"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Múltiplos seletores de conteúdo
            conteudo = (
                soup.find('div', id='mw-content-text') or
                soup.find('div', class_='mw-parser-output') or
                soup.find('article') or
                soup.find('main') or
                soup.find('div', class_='content')
            )
            
            if conteudo:
                texto = conteudo.get_text(separator=' ', strip=True)
                texto = re.sub(r'\s+', ' ', texto)
                return texto[:1000] + "..." if len(texto) > 1000 else texto
            return ""
        except:
            return ""

# UI
ai = PokexScraper()
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if query := st.chat_input("🔍 'como funciona a NW', 'shiny', etc..."):
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        st.info(f"🔎 Buscando '{query}' na wiki...")
        resultados = ai.buscar_real(query)
        
        if resultados:
            for result in resultados:
                with st.expander(result['titulo']):
                    st.markdown(result['conteudo'])
                    st.markdown(f"[🔗 {result['url'][:50]}...]({result['url']})")
        else:
            st.error("❌ Zero resultados. Tente termos exatos da wiki!")
        
        # Debug info
        st.caption("Debug: Teste 'Página_principal' ou navegue wiki primeiro")

# Botões teste
col1, col2, col3 = st.columns(3)
if col1.button("🧪 Teste NW"):
    st.session_state.messages.append({"role": "user", "content": "NW"})
    st.rerun()
if col2.button("⭐ Shiny"):
    st.session_state.messages.append({"role": "user", "content": "shiny"})
    st.rerun()
if col3.button("💎 Mega"):
    st.session_state.messages.append({"role": "user", "content": "mega pedra"})
    st.rerun()
