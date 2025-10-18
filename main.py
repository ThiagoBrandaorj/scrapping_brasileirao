import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Headers para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_atletico_mineiro():
    # URL completa com domínio
    url = "https://www.transfermarkt.com.br/clube-atletico-mineiro/startseite/verein/330"
    
    try:
        # Fazer a requisição
        print("Acessando a página do Atlético Mineiro...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse do HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Página carregada com sucesso!")
        
        # Extrair informações básicas do clube
        print("\n=== INFORMAÇÕES DO CLUBE ===")
        
        # Nome do clube
        club_name = soup.find('h1', class_='data-header__headline-wrapper')
        if club_name:
            print(f"Clube: {club_name.get_text(strip=True)}")
        
        # Informações do squad
        squad_info = soup.find_all('div', class_='data-header__box--small')
        for info in squad_info:
            text = info.get_text(strip=True)
            if 'Squad size:' in text:
                print(f"Tamanho do elenco: {text.split(':')[-1].strip()}")
            elif 'Age:' in text:
                print(f"Idade média: {text.split(':')[-1].strip()}")
        
        # Valor de mercado do squad
        market_value = soup.find('a', {'id': 'wettbewerbsstartseite'})
        if market_value:
            value_text = market_value.find_next('div', class_='data-header__box--big')
            if value_text:
                print(f"Valor de mercado: {value_text.get_text(strip=True)}")
        
        # Extrair jogadores do elenco
        print("\n=== PRINCIPAIS JOGADORES ===")
        players_table = soup.find('table', class_='items')
        
        if players_table:
            players = []
            rows = players_table.find_all('tr', class_=['odd', 'even'])
            
            for i, row in enumerate(rows):
                try:
                    # Nome do jogador
                    name_cell = row.find('td', class_='hauptlink')
                    if not name_cell:
                        continue
                        
                    name_link = name_cell.find('a')
                    if not name_link:
                        continue
                        
                    name = name_link.get_text(strip=True)
                    
                    # Idade
                    age_cell = row.find_all('td', class_='zentriert')
                    age = age_cell[1].get_text(strip=True) if len(age_cell) > 1 else "N/A"
                    
                    # Valor de mercado
                    value_cell = row.find('td', class_='rechts hauptlink')
                    value = value_cell.get_text(strip=True) if value_cell else "N/A"

                    # Altura - vamos tentar pegar da página principal primeiro
                    player_height = "N/A"
                    
                    # Ir até a página do jogador para pegar a altura
                    player_url = name_link.get('href')
                    if player_url:
                        # Construir URL completa se necessário
                        if not player_url.startswith('http'):
                            player_url = f"https://www.transfermarkt.com.br{player_url}"
                        
                        try:
                            print(f"  Acessando página do jogador {i+1}: {name}")
                            player_response = requests.get(player_url, headers=headers)
                            player_response.raise_for_status()
                            player_soup = BeautifulSoup(player_response.content, 'html.parser')
                            
                            # Extrair altura do jogador
                            height_element = player_soup.find('span', itemprop='height')
                            if height_element:
                                player_height = height_element.get_text(strip=True)
                            
                            time.sleep(1)  # Respeitar o servidor
                            
                        except Exception as e:
                            print(f"    Erro ao acessar página do {name}: {e}")
                            player_height = "Erro"
                    
                    player_data = {
                        'Nome': name,
                        'Idade': age,
                        'Valor': value,
                        'Altura': player_height
                    }
                    
                    players.append(player_data)
                    print(f"✓ {name} | {age} anos | {value} | {player_height}")

                except Exception as e:
                    print(f"Erro ao processar jogador {i+1}: {e}")
                    continue
        
        print(f"\nTotal de {len(players)} jogadores extraídos")
        
        # Salvar em DataFrame
        df = pd.DataFrame(players)
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None
    except Exception as e:
        print(f"Erro durante o scraping: {e}")
        return None

def main():
    print("Iniciando scraping do Atlético Mineiro...")
    print("Aguardando carregamento da página...")
    
    # Executar o scraping
    df = scrape_atletico_mineiro()
    
    if df is not None and not df.empty:
        # Salvar em CSV
        df.to_csv('atletico_mineiro_elenco.csv', index=False, encoding='utf-8')
        print("\nDados salvos em 'atletico_mineiro_elenco.csv'")
        
        # Mostrar preview dos dados
        print("\nPreview dos dados:")
        print(df.head())
    
    print("\nScraping concluído!")

if __name__ == "__main__":
    main()