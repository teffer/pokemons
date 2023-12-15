import requests   

url = f'https://pokeapi.co/api/v2/pokemon/25'
response = requests.get(url)
if response.status_code == 200:
    pokemon_list = []
    answer_data = response.json()
    pokemons_list = answer_data.get('results', [])
    current_pokemon_data = requests.get(url).json()
    health = current_pokemon_data.get('stats', [])[0]['base_stat']
    attack = current_pokemon_data.get('stats', [])[1]['base_stat']
    image = current_pokemon_data.get('sprites', {}).get('front_default', '')
print(image)