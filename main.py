import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Configuração da API Key (Certifique-se de que está nos Secrets do Replit)
api_key = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)

BASE_URL = "https://wiki.pokexgames.com/index.php"

def buscar_na_wiki(query):
    """Procura o termo na Wiki e retorna o conteúdo da página."""
    search_url = f"{BASE_URL}?search={query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, timeout=10)
        # Se redirecionar direto para a página do assunto
        if "index.php/" in response.url:
            return extrair_conteudo(response.url)
        
        # Se cair na lista de resultados
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link = soup.find('div', class_='mw-search-result-heading')
        
        if first_link and first_link.find('a'):
            full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
            return extrair_conteudo(full_link)
    except Exception as e:
        return f"Erro na conexão: {e}"
    
    return "Não encontrei nada específico sobre isso na Wiki."

def extrair_conteudo(url):
    """Limpa o HTML e pega o texto útil."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove lixo visual
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    content = soup.find('div', id='mw-content-text')
    return content.get_text(separator='\n', strip=True)[:8000] if content else "Página vazia."

def chat_pxg():
    print("\n--- Assistente PXG Wiki Ativo (Versão Atualizada) ---")
    print("O que você quer saber sobre o PXG hoje?")
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break
        
        print("Buscando na Wiki...")
        contexto = buscar_na_wiki(user_input)
        
        # Instrução para a IA
        prompt = f"""
        Você é um assistente especializado no jogo PokeXGames.
        Abaixo estão dados extraídos da Wiki oficial sobre o que o usuário perguntou.
        Responda de forma organizada (use tabelas se houver drops ou status).
        Se a informação não estiver no texto abaixo, avise que não encontrou na Wiki.

        CONTEÚDO DA WIKI:
        {contexto}

        PERGUNTA DO JOGADOR: {user_input}
        """
        
        try:
            # Usando o modelo mais recente e performático
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            print(f"\nIA PXG: {response.text}")
        except Exception as e:
            print(f"\nErro ao processar: {e}")

if __name__ == "__main__":
    chat_pxg()
