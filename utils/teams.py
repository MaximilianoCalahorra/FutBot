import unicodedata
import re

TEAMS = {
  # La Liga:
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
  },
  
  # Premier League:
  "arsenal": {
    "canonical": "Arsenal",
    "football_data": ["Arsenal FC"],
    "soccerdata": ["Arsenal"]
  },
  "aston_villa": {
    "canonical": "Aston Villa",
    "football_data": ["Aston Villa FC"],
    "soccerdata": ["Aston Villa"]
  },
  "bournemouth": {
    "canonical": "Bournemouth",
    "football_data": ["AFC Bournemouth"],
    "soccerdata": ["AFC Bournemouth"]
  },
  "brentford": {
    "canonical": "Brentford",
    "football_data": ["Brentford FC"],
    "soccerdata": ["Brentford"]
  },
  "brighton": {
    "canonical": "Brighton",
    "football_data": ["Brighton & Hove Albion FC"],
    "soccerdata": ["Brighton & Hove Albion"]
  },
  "burnley": {
    "canonical": "Burnley",
    "football_data": ["Burnley FC"],
    "soccerdata": ["Burnley"]
  },
  "chelsea": {
    "canonical": "Chelsea",
    "football_data": ["Chelsea FC"],
    "soccerdata": ["Chelsea"]
  },
  "crystal_palace": {
    "canonical": "Crystal Palace",
    "football_data": ["Crystal Palace FC"],
    "soccerdata": ["Crystal Palace"]
  },
  "everton": {
    "canonical": "Everton",
    "football_data": ["Everton FC"],
    "soccerdata": ["Everton"]
  },
  "fulham": {
    "canonical": "Fulham",
    "football_data": ["Fulham FC"],
    "soccerdata": ["Fulham"]
  },
  "leeds": {
    "canonical": "Leeds",
    "football_data": ["Leeds United FC"],
    "soccerdata": ["Leeds United"]
  },
  "liverpool": {
    "canonical": "Liverpool",
    "football_data": ["Liverpool FC"],
    "soccerdata": ["Liverpool"]
  },
  "manchester_city": {
    "canonical": "Manchester City",
    "football_data": ["Manchester City FC"],
    "soccerdata": ["Manchester City"]
  },
  "manchester_united": {
    "canonical": "Manchester United",
    "football_data": ["Manchester United FC"],
    "soccerdata": ["Manchester United"]
  },
  "newclastle": {
    "canonical": "Newcastle",
    "football_data": ["Newcastle United FC"],
    "soccerdata": ["Newcastle United"]
  },
  "nottingham_forest": {
    "canonical": "Nottingham Forest",
    "football_data": ["Nottingham Forest FC"],
    "soccerdata": ["Nottingham Forest"]
  },
  "sunderland": {
    "canonical": "Sunderland",
    "football_data": ["Sunderland AFC"],
    "soccerdata": ["Sunderland"]
  },
  "tottenham": {
    "canonical": "Tottenham",
    "football_data": ["Tottenham Hotspur FC"],
    "soccerdata": ["Tottenham Hotspur"]
  },
  "west_ham": {
    "canonical": "West Ham",
    "football_data": ["West Ham United FC"],
    "soccerdata": ["West Ham United"]
  },
  "wolverhampton": {
    "canonical": "Wolverhampton",
    "football_data": ["Wolverhampton Wanderers FC"],
    "soccerdata": ["Wolverhampton Wanderers"]
  },
  
  # Championship:
  "birmingham": {
    "canonical": "Birmingham City",
    "football_data": ["Birmingham City FC"],
    "soccerdata": ["Birmingham City"]
  },
  "blackburn": {
    "canonical": "Blackburn",
    "football_data": ["Blackburn Rovers FC"],
    "soccerdata": ["Blackburn Rovers"]
  },
  "bristol_city": {
    "canonical": "Bristol City",
    "football_data": ["Bristol City FC"],
    "soccerdata": ["Bristol City"]
  },
  "charlton": {
    "canonical": "Charlton",
    "football_data": ["Charlton Athletic FC"],
    "soccerdata": ["Charlton Athletic"]
  },
  "coventry": {
    "canonical": "Coventry",
    "football_data": ["Coventry City FC"],
    "soccerdata": ["Coventry City"]
  },
  "derby_county": {
    "canonical": "Derby County",
    "football_data": ["Derby County FC"],
    "soccerdata": ["Derby County"]
  },
  "hull_city": {
    "canonical": "Hull City",
    "football_data": ["Hull City AFC"],
    "soccerdata": ["Hull City"]
  },
  "ipswich": {
    "canonical": "Ipswich",
    "football_data": ["Ipswich Town FC"],
    "soccerdata": ["Ipswich Town"]
  },
  "leicester": {
    "canonical": "Leicester City",
    "football_data": ["Leicester City FC"],
    "soccerdata": ["Leicester City"]
  },
  "middlesbrough": {
    "canonical": "Middlesbrough",
    "football_data": ["Middlesbrough FC"],
    "soccerdata": ["Middlesbrough"]
  },
  "millwall": {
    "canonical": "Millwall",
    "football_data": ["Millwall FC"],
    "soccerdata": ["Millwall"]
  },
  "norwich": {
    "canonical": "Norwich",
    "football_data": ["Norwich City FC"],
    "soccerdata": ["Norwich City"]
  },
  "oxford_united": {
    "canonical": "Oxford United",
    "football_data": ["Oxford United FC"],
    "soccerdata": ["Oxford United"]
  },
  "portsmouth": {
    "canonical": "Portsmouth",
    "football_data": ["Portsmouth FC"],
    "soccerdata": ["Portsmouth"]
  },
  "preston_ne": {
    "canonical": "Preston NE",
    "football_data": ["Preston North End FC"],
    "soccerdata": ["Preston North End"]
  },
  "qpr": {
    "canonical": "QPR",
    "football_data": ["Queens Park Rangers FC"],
    "soccerdata": ["Queens Park Rangers"]
  },
  "sheffield_united": {
    "canonical": "Sheffield United",
    "football_data": ["Sheffield United FC"],
    "soccerdata": ["Sheffield United"]
  },
  "sheffield_wednesday": {
    "canonical": "Sheffield Wednesday",
    "football_data": ["Sheffield Wednesday FC"],
    "soccerdata": ["Sheffield Wednesday"]
  },
  "southampton": {
    "canonical": "Southampton",
    "football_data": ["Southampton FC"],
    "soccerdata": ["Southampton"]
  },
  "stoke": {
    "canonical": "Stoke",
    "football_data": ["Stoke City FC"],
    "soccerdata": ["Stoke City"]
  },
  "swansea": {
    "canonical": "Swansea",
    "football_data": ["Swansea City AFC"],
    "soccerdata": ["Swansea City"]
  },
  "watford": {
    "canonical": "Watford",
    "football_data": ["Watford FC"],
    "soccerdata": ["Watford"]
  },
  "west_bromwich": {
    "canonical": "West Bromwich",
    "football_data": ["West Bromwich Albion FC"],
    "soccerdata": ["West Bromwich Albion"]
  },
  "wrexham": {
    "canonical": "Wrexham",
    "football_data": ["Wrexham AFC"],
    "soccerdata": ["Wrexham"]
  },
  
  # Bundesliga:
  "augsburg": {
    "canonical": "Augsburg",
    "football_data": ["FC Augsburg"],
    "soccerdata": ["Augsburg"]
  },
  "bayern": {
    "canonical": "Bayern",
    "football_data": ["FC Bayern München"],
    "soccerdata": ["Bayern Munich"]
  },
  "dortmund": {
    "canonical": "Dortmund",
    "football_data": ["Borussia Dortmund"],
    "soccerdata": ["Borussia Dortmund"]
  },
  "frankfurt": {
    "canonical": "Frankfurt",
    "football_data": ["Eintracht Frankfurt"],
    "soccerdata": ["Eintracht Frankfurt"]
  },
  "freiburg": {
    "canonical": "Freiburg",
    "football_data": ["SC Freiburg"],
    "soccerdata": ["Freiburg"]
  },
  "hamburger": {
    "canonical": "Hamburger",
    "football_data": ["Hamburger SV"],
    "soccerdata": ["Hamburg"]
  },
  "heidenheim": {
    "canonical": "Heidenheim",
    "football_data": ["1. FC Heidenheim 1846"],
    "soccerdata": ["Heidenheim"]
  },
  "hoffenheim": {
    "canonical": "Hoffenheim",
    "football_data": ["TSG 1899 Hoffenheim"],
    "soccerdata": ["Hoffenheim"]
  },
  "köln": {
    "canonical": "Köln",
    "football_data": ["1. FC Köln"],
    "soccerdata": ["FC Cologne"]
  },
  "leipzig": {
    "canonical": "Leipzig",
    "football_data": ["RB Leipzig"],
    "soccerdata": ["RB Leipzig"]
  },
  "leverkusen": {
    "canonical": "Leverkusen",
    "football_data": ["Bayer 04 Leverkusen"],
    "soccerdata": ["Bayer Leverkusen"]
  },
  "mainz": {
    "canonical": "Mainz",
    "football_data": ["1. FSV Mainz 05"],
    "soccerdata": ["Mainz"]
  },
  "mönchengladbach": {
    "canonical": "Mönchengladbach",
    "football_data": ["Borussia Mönchengladbach"],
    "soccerdata": ["Borussia M'gladbach"]
  },
  "st_pauli": {
    "canonical": "St. Pauli",
    "football_data": ["FC St. Pauli 1910"],
    "soccerdata": ["St. Pauli"]
  },
  "stuttgart": {
    "canonical": "Stuttgart",
    "football_data": ["VfB Stuttgart"],
    "soccerdata": ["Stuttgart"]
  },
  "union_berlin": {
    "canonical": "Union Berlin",
    "football_data": ["1. FC Union Berlin"],
    "soccerdata": ["Union Berlin"]
  },
  "werder_bremen": {
    "canonical": "Werder Bremen",
    "football_data": ["SV Werder Bremen"],
    "soccerdata": ["Werder Bremen"]
  },
  "wolfsburg": {
    "canonical": "Wolfsburg",
    "football_data": ["VfL Wolfsburg"],
    "soccerdata": ["Wolfsburg"]
  },
  
  # Serie A:
  "atalanta": {
    "canonical": "Atalanta",
    "football_data": ["Atalanta BC"],
    "soccerdata": ["Atalanta"]
  },
  "bologna": {
    "canonical": "Bologna",
    "football_data": ["Bologna FC 1909"],
    "soccerdata": ["Bologna"]
  },
  "cagliari": {
    "canonical": "Cagliari",
    "football_data": ["Cagliari Calcio"],
    "soccerdata": ["Cagliari"]
  },
  "como": {
    "canonical": "Como",
    "football_data": ["Como 1907"],
    "soccerdata": ["Como"]
  },
  "cremonese": {
    "canonical": "Cremonese",
    "football_data": ["US Cremonese"],
    "soccerdata": ["Cremonese"]
  },
  "fiorentina": {
    "canonical": "Fiorentina",
    "football_data": ["ACF Fiorentina"],
    "soccerdata": ["Fiorentina"]
  },
  "genoa": {
    "canonical": "Genoa",
    "football_data": ["Genoa CFC"],
    "soccerdata": ["Genoa"]
  },
  "hellas_verona": {
    "canonical": "Hellas Verona",
    "football_data": ["Hellas Verona FC"],
    "soccerdata": ["Verona"]
  },
  "inter": {
    "canonical": "Inter",
    "football_data": ["FC Internazionale Milano"],
    "soccerdata": ["Inter Milan"]
  },
  "juventus": {
    "canonical": "Juventus",
    "football_data": ["Juventus FC"],
    "soccerdata": ["Juventus"]
  },
  "lazio": {
    "canonical": "Lazio",
    "football_data": ["SS Lazio"],
    "soccerdata": ["Lazio"]
  },
  "lecce": {
    "canonical": "Lecce",
    "football_data": ["US Lecce"],
    "soccerdata": ["Lecce"]
  },
  "milan": {
    "canonical": "Milan",
    "football_data": ["AC Milan"],
    "soccerdata": ["AC Milan"]
  },
  "napoli": {
    "canonical": "Napoli",
    "football_data": ["SSC Napoli"],
    "soccerdata": ["Napoli"]
  },
  "parma": {
    "canonical": "Parma",
    "football_data": ["Parma Calcio 1913"],
    "soccerdata": ["Parma"]
  },
  "pisa": {
    "canonical": "Pisa",
    "football_data": ["AC Pisa 1909"],
    "soccerdata": ["Pisa"]
  },
  "roma": {
    "canonical": "Roma",
    "football_data": ["AS Roma"],
    "soccerdata": ["Roma"]
  },
  "sassuolo": {
    "canonical": "Sassuolo",
    "football_data": ["US Sassuolo Calcio"],
    "soccerdata": ["Sassuolo"]
  },
  "torino": {
    "canonical": "Torino",
    "football_data": ["Torino FC"],
    "soccerdata": ["Torino"]
  },
  "udinese": {
    "canonical": "Udinese",
    "football_data": ["Udinese Calcio"],
    "soccerdata": ["Udinese"]
  },

  # Ligue 1:
  "angers": {
    "canonical": "Angers",
    "football_data": ["Angers SCO"],
    "soccerdata": ["Angers"]
  },
  "auxerre": {
    "canonical": "Auxerre",
    "football_data": ["AJ Auxerre"],
    "soccerdata": ["Auxerre"]
  },
  "brest": {
    "canonical": "Brest",
    "football_data": ["Stade Brestois 29"],
    "soccerdata": ["Brest"]
  },
  "le_havre": {
    "canonical": "Le Havre",
    "football_data": ["Le Havre AC"],
    "soccerdata": ["Le Havre"]
  },
  "lens": {
    "canonical": "Lens",
    "football_data": ["Racing Club de Lens"],
    "soccerdata": ["Lens"]
  },
  "lille": {
    "canonical": "Lille",
    "football_data": ["Lille OSC"],
    "soccerdata": ["Lille"]
  },
  "lorient": {
    "canonical": "Lorient",
    "football_data": ["FC Lorient"],
    "soccerdata": ["Lorient"]
  },
  "lyon": {
    "canonical": "Lyon",
    "football_data": ["Olympique Lyonnais"],
    "soccerdata": ["Lyon"]
  },
  "marsella": {
    "canonical": "Marsella",
    "football_data": ["Olympique de Marseille"],
    "soccerdata": ["Marseille"]
  },
  "metz": {
    "canonical": "Metz",
    "football_data": ["FC Metz"],
    "soccerdata": ["Metz"]
  },
  "monaco": {
    "canonical": "Monaco",
    "football_data": ["AS Monaco FC"],
    "soccerdata": ["Monaco"]
  },
  "nantes": {
    "canonical": "Nantes",
    "football_data": ["FC Nantes"],
    "soccerdata": ["Nantes"]
  },
  "nice": {
    "canonical": "Nice",
    "football_data": ["OGC Nice"],
    "soccerdata": ["Nice"]
  },
  "psg": {
    "canonical": "PSG",
    "football_data": ["Paris Saint-Germain FC"],
    "soccerdata": ["PSG"]
  },
  "paris": {
    "canonical": "Paris FC",
    "football_data": ["Paris FC"],
    "soccerdata": ["Paris FC"]
  },
  "rennes": {
    "canonical": "Rennes",
    "football_data": ["Stade Rennais FC 1901"],
    "soccerdata": ["Rennes"]
  },
  "strasbourg": {
    "canonical": "Strasbourg",
    "football_data": ["RC Strasbourg Alsace"],
    "soccerdata": ["Strasbourg"]
  },
  "toulouse": {
    "canonical": "Toulouse",
    "football_data": ["Toulouse FC"],
    "soccerdata": ["Toulouse"]
  },
  
  # Primeira Liga:
  "alverca": {
    "canonical": "Alverca",
    "football_data": ["FC Alverca"],
    "soccerdata": ["Alverca"]
  },
  "amadora": {
    "canonical": "Amadora",
    "football_data": ["CF Estrela da Amadora"],
    "soccerdata": ["Estrela"]
  },
  "arouca": {
    "canonical": "Arouca",
    "football_data": ["FC Arouca"],
    "soccerdata": ["Arouca"]
  },
  "avs": {
    "canonical": "AVS",
    "football_data": ["AVS"],
    "soccerdata": ["AVS"]
  },
  "benfica": {
    "canonical": "Benfica",
    "football_data": ["Sport Lisboa e Benfica"],
    "soccerdata": ["Benfica"]
  },
  "braga": {
    "canonical": "Braga",
    "football_data": ["Sporting Clube de Braga"],
    "soccerdata": ["Sporting Braga"]
  },
  "casa_pia": {
    "canonical": "Casa Pia",
    "football_data": ["Casa Pia AC"],
    "soccerdata": ["Casa Pia"]
  },
  "estoril_praia": {
    "canonical": "Estoril Praia",
    "football_data": ["GD Estoril Praia"],
    "soccerdata": ["Estoril"]
  },
  "famalicao": {
    "canonical": "Famalicão",
    "football_data": ["FC Famalicão"],
    "soccerdata": ["Famalicao"]
  },
  "gil_vicente": {
    "canonical": "Gil Vicente",
    "football_data": ["Gil Vicente FC"],
    "soccerdata": ["Gil Vicente"]
  },
  "moreirense": {
    "canonical": "Moreirense",
    "football_data": ["Moreirense FC"],
    "soccerdata": ["Moreirense"]
  },
  "nacional": {
    "canonical": "Nacional",
    "football_data": ["CD Nacional"],
    "soccerdata": ["Nacional"]
  },
  "porto": {
    "canonical": "Porto",
    "football_data": ["FC Porto"],
    "soccerdata": ["Porto"]
  },
  "rio_ave": {
    "canonical": "Rio Ave",
    "football_data": ["Rio Ave FC"],
    "soccerdata": ["Rio Ave"]
  },
  "santa_clara": {
    "canonical": "Santa Clara",
    "football_data": ["CD Santa Clara"],
    "soccerdata": ["Santa Clara"]
  },
  "sporting": {
    "canonical": "Sporting",
    "football_data": ["Sporting Clube de Portugal"],
    "soccerdata": ["Sporting Lisbon"]
  },
  "tondela": {
    "canonical": "Tondela",
    "football_data": ["CD Tondela"],
    "soccerdata": ["Tondela"]
  },
  "vitoria": {
    "canonical": "Vitória",
    "football_data": ["Vitória SC"],
    "soccerdata": ["Vitoria Guimaraes"]
  },

  # Eredivisie:
  "ajax": {
    "canonical": "Ajax",
    "football_data": ["AFC Ajax"],
    "soccerdata": ["Ajax"]
  },
  "az": {
    "canonical": "AZ",
    "football_data": ["AZ"],
    "soccerdata": ["AZ"]
  },
  "excelsior": {
    "canonical": "Excelsior",
    "football_data": ["SBV Excelsior"],
    "soccerdata": ["Excelsior"]
  },
  "feyenoord": {
    "canonical": "Feyenoord",
    "football_data": ["Feyenoord Rotterdam"],
    "soccerdata": ["Feyenoord"]
  },
  "go_ahead_eagles": {
    "canonical": "Go Ahead Eagles",
    "football_data": ["Go Ahead Eagles"],
    "soccerdata": ["Go Ahead Eagles"]
  },
  "groningen": {
    "canonical": "Groningen",
    "football_data": ["FC Groningen"],
    "soccerdata": ["Groningen"]
  },
  "heerenveen": {
    "canonical": "Heerenveen",
    "football_data": ["SC Heerenveen"],
    "soccerdata": ["Heerenveen"]
  },
  "heracles": {
    "canonical": "Heracles",
    "football_data": ["Heracles Almelo"],
    "soccerdata": ["Heracles"]
  },
  "nac": {
    "canonical": "NAC",
    "football_data": ["NAC Breda"],
    "soccerdata": ["NAC Breda"]
  },
  "nec": {
    "canonical": "NEC",
    "football_data": ["NEC"],
    "soccerdata": ["NEC"]
  },
  "psv": {
    "canonical": "PSV",
    "football_data": ["PSV"],
    "soccerdata": ["PSV"]
  },
  "sittard": {
    "canonical": "Sittard",
    "football_data": ["Fortuna Sittard"],
    "soccerdata": ["Fortuna Sittard"]
  },
  "sparta": {
    "canonical": "Sparta",
    "football_data": ["Sparta Rotterdam"],
    "soccerdata": ["Sparta Rotterdam"]
  },
  "telstar": {
    "canonical": "Telstar",
    "football_data": ["Telstar 1963"],
    "soccerdata": ["Telstar"]
  },
  "twente": {
    "canonical": "Twente",
    "football_data": ["FC Twente '65"],
    "soccerdata": ["Twente"]
  },
  "utrecht": {
    "canonical": "Utrecht",
    "football_data": ["FC Utrecht"],
    "soccerdata": ["Utrecht"]
  },
  "volendam": {
    "canonical": "Volendam",
    "football_data": ["FC Volendam"],
    "soccerdata": ["Volendam"]
  },
  "zwolle": {
    "canonical": "Zwolle",
    "football_data": ["PEC Zwolle"],
    "soccerdata": ["PEC Zwolle"]
  }
}

def norm(s: str) -> str:
  s = s.strip().lower()
  s = unicodedata.normalize("NFKD", s)
  s = "".join(c for c in s if not unicodedata.combining(c))
  s = s.replace("’", "'")
  s = s.replace("\u00a0", " ")
  s = re.sub(r"\s+", " ", s)
  return s

def construir_indice():
  index = {}

  for key, data in TEAMS.items():
    for nombre in data["football_data"]:
      index[norm(nombre)] = key
    for nombre in data["soccerdata"]:
      index[norm(nombre)] = key

  return index

TEAM_INDEX = construir_indice()

def normalizar_equipo(nombre: str) -> str | None:
  if not nombre:
      return None
  return TEAM_INDEX.get(norm(nombre))