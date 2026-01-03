TEAMS = {
  "alaves": {
    "canonical": "Alavés",
    "football_data": ["Deportivo Alavés"],
    "soccerdata": ["Alaves"]
  },
  "athletic": {
    "canonical": "Athletic",
    "football_data": ["Athletic Club"],
    "soccerdata": ["Athletic Bilbao"]
  },
  "atletico": {
    "canonical": "Atlético",
    "football_data": ["Club Atlético de Madrid"],
    "soccerdata": ["Atletico Madrid"]
  },
  "barcelona": {
    "canonical": "Barcelona",
    "football_data": ["FC Barcelona"],
    "soccerdata": ["Barcelona"]
  },
  "betis": {
    "canonical": "Betis",
    "football_data": ["Real Betis Balompié"],
    "soccerdata": ["Real Betis"]
  },
  "celta": {
    "canonical": "Celta",
    "football_data": ["RC Celta de Vigo"],
    "soccerdata": ["Celta Vigo"]
  },
  "elche": {
    "canonical": "Elche",
    "football_data": ["Elche CF"],
    "soccerdata": ["Elche"]
  },
  "espanyol": {
    "canonical": "Espanyol",
    "football_data": ["RCD Espanyol de Barcelona"],
    "soccerdata": ["Espanyol"]
  },
  "getafe": {
    "canonical": "Getafe",
    "football_data": ["Getafe CF"],
    "soccerdata": ["Getafe"]
  },
  "girona": {
    "canonical": "Girona",
    "football_data": ["Girona FC"],
    "soccerdata": ["Girona"]
  },
  "levante": {
    "canonical": "Levante",
    "football_data": ["Levante UD"],
    "soccerdata": ["Levante"]
  },
  "mallorca": {
    "canonical": "Mallorca",
    "football_data": ["RCD Mallorca"],
    "soccerdata": ["Mallorca"]
  },
  "osasuna": {
    "canonical": "Osasuna",
    "football_data": ["CA Osasuna"],
    "soccerdata": ["Osasuna"]
  },
  "rayo": {
    "canonical": "Rayo",
    "football_data": ["Rayo Vallecano de Madrid"],
    "soccerdata": ["Rayo Vallecano"]
  },
  "real_madrid": {
    "canonical": "Real Madrid",
    "football_data": ["Real Madrid CF"],
    "soccerdata": ["Real Madrid"]
  },
  "real_oviedo": {
    "canonical": "Real Oviedo",
    "football_data": ["Real Oviedo"],
    "soccerdata": ["Real Oviedo"]
  },
  "real_sociedad": {
    "canonical": "Real Sociedad",
    "football_data": ["Real Sociedad de Fútbol"],
    "soccerdata": ["Real Sociedad"]
  },
  "sevilla": {
    "canonical": "Sevilla",
    "football_data": ["Sevilla FC"],
    "soccerdata": ["Sevilla"]
  },
  "valencia": {
    "canonical": "Valencia",
    "football_data": ["Valencia CF"],
    "soccerdata": ["Valencia"]
  },
  "villarreal": {
    "canonical": "Villarreal",
    "football_data": ["Villarreal CF"],
    "soccerdata": ["Villarreal"]
  }
}

def construir_indice():
  index = {}

  for key, data in TEAMS.items():
    for nombre in data["football_data"]:
      index[nombre.lower()] = key
    for nombre in data["soccerdata"]:
      index[nombre.lower()] = key

  return index

TEAM_INDEX = construir_indice()

def normalizar_equipo(nombre: str) -> str | None:
  if not nombre:
      return None
  return TEAM_INDEX.get(nombre.lower())