import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

url = "https://www.bbc.com/sport/football/scores-fixtures"
all_matches = []

try:
    print(f"Scraping: {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except Exception as e:
    print(f"❌ Failed to fetch URL: {e}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')

# Find all competition sections
competition_sections = soup.select('.ssrcss-7k0bq5-HeaderWrapper')

if not competition_sections:
    print("⚠️ No competitions found - check if BBC changed their layout")
    exit()

for comp_section in competition_sections:
    try:
        # Get competition name
        competition = comp_section.select_one('.ssrcss-12l0oeb-GroupHeader').text.strip()
        
        # Get all matches in this competition
        matches = comp_section.find_next('ul', class_='ssrcss-1w89ukb-StackLayout').select('li.ssrcss-18nzily-HeadToHeadWrapper')
        
        for match in matches:
            try:
                # Extract match details
                home_team = match.select_one('.ssrcss-1ucldln-StyledTeam-HomeTeam .ssrcss-1p14tic-DesktopValue').text.strip()
                away_team = match.select_one('.ssrcss-1d12j2y-StyledTeam-AwayTeam .ssrcss-1p14tic-DesktopValue').text.strip()
                
                # Handle both live matches and upcoming fixtures
                score = match.select_one('.ssrcss-natiry-StyledScore')
                if score:
                    home_score = score.select_one('.ssrcss-qsbptj-HomeScore').text.strip()
                    away_score = score.select_one('.ssrcss-fri5a2-AwayScore').text.strip()
                    match_status = "FT" if match.select_one('.ssrcss-msb9pu-StyledPeriod') else match.select_one('.ssrcss-1v84ueh-StyledPeriod').text.strip()
                    match_time = f"{home_score}-{away_score} ({match_status})"
                else:
                    match_time = match.select_one('.ssrcss-bkk8ek-StyledTime').text.strip()
                
                all_matches.append({
                    'Competition': competition,
                    'Time': match_time,
                    'Home Team': home_team,
                    'Away Team': away_team
                })
            except Exception as e:
                print(f"⚠️ Skipping match in {competition}: {e}")
                continue
                
    except Exception as e:
        print(f"⚠️ Error processing competition section: {e}")
        continue

if all_matches:
    df = pd.DataFrame(all_matches)
    # Save to desktop to avoid permission issues
    output_path = 'bbc_football_fixtures.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✅ Success! Saved {len(df)} matches to {output_path}")
    print("\nSample fixtures:")
    print(df.head())
else:
    print("❌ No matches found. The BBC page structure may have changed.")