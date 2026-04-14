import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Configuração da API Key via Secrets do Replit
api_key = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)

BASE_URL = "https://wiki.pokexgames.com/index.php"

def buscar_na_wiki(query):
    search_url = f"{BASE_URL}?search={query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, timeout=10)
        if "index.php/" in response.url:
            return extrair_conteudo(response.url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link = soup.find('div', class_='mw-search-result-heading')
        
        if first_link and first_link.find('a'):
            full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
            return extrair_conteudo(full_link)
    except Exception as e:
        return f"Erro na busca: {e}"
    
    return "Não encontrei uma página específica na Wiki."

def extrair_conteudo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    content = soup.find('div', id='mw-content-text')
    return content.get_text(separator='\n', strip=True)[:7000] if content else "Página sem conteúdo visível."

def chat_pxg():
    print("\n--- Assistente PXG Wiki (Versão Atualizada) ---")
    print("Digite sua dúvida sobre PXG (ou 'sair' para encerrar):")
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break
        
        print("Consultando Wiki oficial...")
        contexto_wiki = buscar_na_wiki(user_input)
        
        prompt = f"""
        Você é um tutor especializado no jogo PokeXGames (PXG).
        Contexto extraído da Wiki:
        {contexto_wiki}
        
        Pergunta do jogador: {user_input}
        
        Instruções: Use os dados acima para responder de forma clara. Se houver tabelas de drops ou moves, formate-as bem.
        """
        
        try:
            # Usando o modelo gemini-2.0-flash que é mais rápido e moderno
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            print(f"\nIA PXG: {response.text}")
        except Exception as e:
            print(f"\nErro ao gerar resposta: {e}")

if __name__ == "__main__":
    chat_pxg()
