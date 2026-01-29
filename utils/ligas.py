LIGAS = {
  "la_liga": {
    "nombre": "La Liga",
    "football_data": "PD",
    "soccerdata": 297,
    "bandera": "🇪🇸",
    "reglas_posiciones": {
      "champions": range(1, 5),
      "europa": [5],
      "conference": [6],
      "descenso": range(18, 21)
    }
  },
  "premier_league": {
    "nombre": "Premier League",
    "football_data": "PL",
    "soccerdata": 228,
    "bandera": "🇬🇧",
    "reglas_posiciones": {
      "champions": range(1, 5),
      "europa": [5],
      "descenso": range(18, 21)
    }
  },
  "championship": {
    "nombre": "Championship",
    "football_data": "ELC",
    "soccerdata": 229,
    "bandera": "🇬🇧",
    "reglas_posiciones": {
      "ascenso": [1, 2],
      "playoff_ascenso": range(3, 7),
      "descenso": range(22, 25)
    }
  },
  "bundesliga": {
    "nombre": "Bundesliga",
    "football_data": "BL1",
    "soccerdata": 241,
    "bandera": "🇩🇪",
    "reglas_posiciones": {
      "champions": range(1, 5),
      "europa": [5],
      "conference": [6],
      "repechaje_descenso": [16],
      "descenso": [17, 18]
    }
  },
  "serie_a": {
    "nombre": "Serie A",
    "football_data": "SA",
    "soccerdata": 253,
    "bandera": "🇮🇹",
    "reglas_posiciones": {
      "champions": range(1, 5),
      "europa": [5],
      "conference": [6],
      "descenso": range(18, 21)
    }
  },
  "ligue_1": {
    "nombre": "Ligue 1",
    "football_data": "FL1",
    "soccerdata": 235,
    "bandera": "🇫🇷",
    "reglas_posiciones": {
      "champions": range(1, 4),
      "champions_q": [4],
      "europa": [5],
      "conference": [6],
      "repechaje_descenso": [16],
      "descenso": [17, 18]
    }
  },
  "primeira_liga": {
    "nombre": "Primeira Liga",
    "football_data": "PPL",
    "soccerdata": 280,
    "bandera": "🇵🇹",
    "reglas_posiciones": {
      "champions": [1],
      "europa": [2],
      "conference": [3, 4],
      "repechaje_descenso": [16],
      "descenso": [17, 18]
    }
  },
  "eredivisie": {
    "nombre": "Eredivisie",
    "football_data": "DED",
    "soccerdata": 268,
    "bandera": "🇳🇱",
    "reglas_posiciones": {
      "champions": [1, 2],
      "champions_q": [3],
      "europa": [4],
      "conference_q": range(5, 9),
      "repechaje_descenso": [16],
      "descenso": [17, 18]
    }
  }
}

DESCRIPCIONES = {
  "champions": "Champions League",
  "champions_q": "Champions League (Clasificatorias)",
  "europa": "Europa League",
  "conference": "Conference League",
  "conference_q": "Conference League (Clasificatorias)",
  "ascenso": "Ascenso",
  "playoff_ascenso": "Playoffs por el ascenso",
  "repechaje_descenso": "Repechaje por el descenso",
  "descenso": "Descenso",
}