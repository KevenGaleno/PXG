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
    # Tratamento para buscas comuns de PXG
    search_query = query.replace(' ', '+')
    search_url = f"{BASE_URL}?search={search_query}"
    
    try:
        response = requests.get(search_url, timeout=10)
        
        # Se a busca redirecionar direto para a página (ex: "Nightmare World")
        if "index.php/" in response.url and not "search=" in response.url:
            return extrair_conteudo(response.url)
        
        # Caso caia na lista de resultados da busca
        soup = BeautifulSoup(response.text, 'html.parser')
        first_link = soup.find('div', class_='mw-search-result-heading')
        
        if first_link and first_link.find('a'):
            full_link = "https://wiki.pokexgames.com" + first_link.find('a')['href']
            return extrair_conteudo(full_link)
            
    except Exception as e:
        return f"Erro ao acessar a Wiki: {e}"
    
    return "A Wiki não retornou uma página específica para esta busca."

def extrair_conteudo(url):
    """Extrai e limpa o texto da página da Wiki."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove elementos inúteis para a IA
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'table.navbox']):
            element.decompose()
        
        content = soup.find('div', id='mw-content-text')
        if content:
            # Pega os primeiros 8000 caracteres para não estourar o limite
            return content.get_text(separator='\n', strip=True)[:8000]
    except:
        pass
    return "Não foi possível ler o conteúdo da página."

def chat_pxg():
    print("\n" + "="*40)
    print("   ASSISTENTE PXG WIKI ATIVO (v2.0)")
    print("="*40)
    print("Digite sua dúvida ou 'sair'.")
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break
        
        print(f"🔍 Pesquisando na Wiki sobre: '{user_input}'...")
        contexto = buscar_na_wiki(user_input)
        
        prompt = f"""
        Você é um tutor do jogo PokeXGames (PXG). Sua base de conhecimento é apenas o texto da Wiki fornecido abaixo.
        
        REGRAS:
        1. Responda de forma direta e amigável.
        2. Se houver tabelas de itens, drops ou níveis no contexto, organize-as bem.
        3. Se o contexto não mencionar a resposta, diga: "Não encontrei detalhes específicos sobre isso na Wiki do PXG."
        
        CONTEXTO DA WIKI:
        {contexto}
        
        PERGUNTA DO JOGADOR: {user_input}
        """
        
        try:
            # Usando o modelo 2.0 Flash (mais moderno e evita o erro 404)
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            print(f"\nIA PXG: {response.text}")
        except Exception as e:
            print(f"\n❌ Erro na IA: {e}")

if __name__ == "__main__":
    chat_pxg()
