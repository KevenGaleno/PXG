import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configuração da API Key (Adicione nos 'Secrets' do Replit)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

BASE_URL = "https://wiki.pokexgames.com/index.php"

def buscar_na_wiki(query):
    """Realiza uma busca simples na Wiki e tenta encontrar a página mais relevante."""
    search_url = f"{BASE_URL}?search={query.replace(' ', '+')}"
    response = requests.get(search_url)
    
    # Se a busca redirecionar direto para uma página de conteúdo
    if "index.php/" in response.url:
        return extrair_conteudo(response.url)
    
    # Se cair na página de resultados de busca
    soup = BeautifulSoup(response.text, 'html.parser')
    first_link = soup.find('div', class_='mw-search-result-heading')
    
    if first_link and first_link.find('a'):
        full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
        return extrair_conteudo(full_link)
    
    return "Não consegui encontrar uma página específica sobre isso na Wiki."

def extrair_conteudo(url):
    """Extrai o texto principal da página da Wiki."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove elementos desnecessários (scripts, estilos, menus laterais)
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    content = soup.find('div', id='mw-content-text')
    return content.get_text(separator='\n', strip=True) if content else "Conteúdo vazio."

def chat_pxg():
    print("--- Assistente PXG Wiki Ativo ---")
    print("Digite sua dúvida (ou 'sair' para encerrar):")
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break
        
        print("Consultando Wiki...")
        contexto_wiki = buscar_na_wiki(user_input)
        
        prompt = f"""
        Você é um especialista em PokeXGames (PXG).
        Abaixo está o conteúdo extraído da Wiki oficial sobre a pergunta do usuário.
        Use APENAS as informações deste contexto para responder. Se a informação não estiver lá, diga que não encontrou na Wiki.
        
        Contexto da Wiki:
        {contexto_wiki[:5000]} # Limite de caracteres para o prompt
        
        Pergunta do Usuário: {user_input}
        """
        
        response = model.generate_content(prompt)
        print(f"\nIA PXG: {response.text}")

if __name__ == "__main__":
    chat_pxg()
