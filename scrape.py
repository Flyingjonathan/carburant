#!/usr/bin/env python3
"""Releve quotidien du prix de la Super 95 (E10) entre Waremme et Herstal.

Lit deux pages de liste de carbu.com, garde les pompes suivies et ecrit :
  - prix.json       : petit fichier lu par bOS (ComfortClick) et par la page de suivi
  - historique.json : un resume par jour (min, max, moyenne)
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RESERVOIR_L = 50  # Skoda Kamiq
PAGES = [
    "https://carbu.com/belgique//index.php/liste-stations-service/E10/Remicourt/4350/BE_lg_953",
    "https://carbu.com/belgique//index.php/liste-stations-service/E10/Herstal/4040/BE_lg_836",
]
# id carbu.com, zone, nom, adresse (dans l'ordre du trajet)
POMPES = [
    ("2051", "Waremme", "Shell Express Waremme", "Chaussée Romaine 218-220, 4300 Waremme"),
    ("869", "Waremme", "Lukoil Waremme", "Rue Saint-Eloi 2, 4300 Waremme"),
    ("1632", "Waremme", "Q8 Easy Waremme", "Place de Gérardmer 55, 4300 Waremme"),
    ("307", "Waremme", "Q8 Waremme", "Rue de Huy 157, 4300 Waremme"),
    ("2781", "E40", "TotalEnergies Waremme (aire E40, direction Liège)", "Autoroute E40 Bruxelles-Liège, 4300 Waremme"),
    ("3225", "Remicourt", "Esso Remicourt", "Chaussée Verte 10, 4350 Remicourt"),
    ("3905", "Awans", "Q8 Awans", "Route de Bruxelles 170, 4340 Awans"),
    ("2786", "Awans", "TotalEnergies Hognoul", "Chaussée de Bruxelles 58, 4342 Hognoul"),
    ("3745", "Loncin / Ans", "DATS 24 Loncin", "Rue Edouard Colson 316, 4431 Loncin"),
    ("1633", "Loncin / Ans", "Q8 Easy Ans", "Rue Jean Jaurès 33, 4430 Ans"),
    ("163", "Loncin / Ans", "DATS 24 Ans", "Rue des Français 88, 4430 Ans"),
    ("2053", "Loncin / Ans", "Shell Express Ans", "Chaussée du Roi Albert 7, 4430 Ans"),
    ("1684", "Rocourt", "Q8 Easy Rocourt", "Chaussée de Tongres 90, 4000 Rocourt"),
    ("2105", "Rocourt", "Shell Express Rocourt", "Chaussée de Tongres 338, 4000 Rocourt"),
    ("380", "Rocourt", "Q8 Rocourt", "Chaussée de Tongres 625, 4000 Rocourt"),
    ("2396", "Vottem", "Texaco Vottem", "Rue Bonnier du Chêne 97, 4041 Vottem"),
    ("4144", "Vottem", "Taverniers (Esso) Vottem", "Sous la Ville 2, 4041 Vottem"),
    ("2055", "Herstal", "Shell Express Herstal", "Rue P.-J. Antoine 6, 4040 Herstal"),
    ("4005", "Herstal", "Shell Express Herstal (Basse Campagne)", "Rue Basse Campagne, 4040 Herstal"),
    ("871", "Herstal", "Lukoil Herstal", "Boulevard Zénobe Gramme 51, 4040 Herstal"),
    ("143", "Herstal", "DATS 24 Herstal", "Boulevard Zénobe Gramme 17, 4040 Herstal"),
    ("1592", "Herstal", "Station Piron", "Rue de Hermée 196, 4040 Herstal"),
    ("2789", "Herstal", "TotalEnergies Herstal", "Rue P.-J. Antoine 22, 4040 Herstal"),
    ("17166", "Herstal", "Q8 Herstal (Hermée)", "Rue de Hermée 207, 4040 Herstal"),
    ("20876", "Herstal", "Shell Herstal", "Rue de Hermée 201, 4040 Herstal"),
    ("347", "Herstal", "TotalEnergies Herstal Amitié", "Rue de l'Amitié 91, 4040 Herstal"),
    ("348", "Herstal", "Q8 Herstal (Crucifix)", "Rue du Crucifix 40, 4040 Herstal"),
]
TAG = re.compile(r'data-id="(\d+)"[^>]*?data-fuelname="([^"]*)"[^>]*?data-price="([0-9.]+)"', re.S)


def lire_prix():
    """Renvoie {id: prix} pour toutes les pompes trouvees sur les pages de liste."""
    prix = {}
    for url in PAGES:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            "Accept-Language": "fr-BE,fr;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=60) as rep:
            html = rep.read().decode("utf-8", "replace")
        for ident, carburant, valeur in TAG.findall(html):
            if "95" in carburant and ident not in prix:
                prix[ident] = float(valeur)
    return prix


def construire(prix, veille, maintenant):
    """Construit le contenu de prix.json. veille = {id: prix} du dernier jour different."""
    pompes = []
    for ident, zone, nom, adresse in POMPES:
        if ident not in prix:
            continue
        p = round(prix[ident], 3)
        variation = round(p - veille[ident], 3) if ident in veille else 0.0
        pompes.append({"id": ident, "zone": zone, "nom": nom, "adresse": adresse,
                       "prix": p, "plein": round(p * RESERVOIR_L, 2), "variation": variation})
    valeurs = [x["prix"] for x in pompes]
    bas, haut = min(valeurs), max(valeurs)
    moins = [x for x in pompes if x["prix"] == bas]
    plus = [x for x in pompes if x["prix"] == haut]
    veille_vals = [veille[x["id"]] for x in pompes if x["id"] in veille]
    tendance = round(bas - min(veille_vals), 3) if veille_vals else 0.0
    sortie = {
        "maj": maintenant.strftime("%d/%m/%Y %H:%M"),
        "date": maintenant.strftime("%Y-%m-%d"),
        "carburant": "Super 95 (E10)",
        "source": "carbu.com",
        "reservoir_l": RESERVOIR_L,
        "nb_pompes": len(pompes),
        "min_prix": bas, "min_nom": moins[0]["nom"], "min_adresse": moins[0]["adresse"], "min_nb": len(moins),
        "max_prix": haut, "max_nom": plus[0]["nom"], "max_adresse": plus[0]["adresse"], "max_nb": len(plus),
        "moyenne": round(sum(valeurs) / len(valeurs), 3),
        "ecart_litre": round(haut - bas, 3),
        "tendance_min": tendance,
        "tendance_texte": "en hausse" if tendance > 0 else "en baisse" if tendance < 0 else "stable",
    }
    for pct in (100, 75, 50, 25):
        litres = RESERVOIR_L * pct / 100
        sortie[f"plein_{pct}_litres"] = litres
        sortie[f"plein_{pct}_bas"] = round(litres * bas, 2)
        sortie[f"plein_{pct}_haut"] = round(litres * haut, 2)
        sortie[f"plein_{pct}_gain"] = round(litres * (haut - bas), 2)
    sortie["top"] = sorted(pompes, key=lambda x: x["prix"])[:5]
    sortie["pompes"] = pompes
    return sortie


def main():
    racine = Path(__file__).parent
    f_prix, f_hist = racine / "prix.json", racine / "historique.json"
    maintenant = datetime.now(ZoneInfo("Europe/Brussels"))
    ancien = json.loads(f_prix.read_text("utf-8")) if f_prix.exists() else {}
    hist = json.loads(f_hist.read_text("utf-8")) if f_hist.exists() else []

    prix = lire_prix()
    suivies = {i for i, *_ in POMPES}
    trouves = {k: v for k, v in prix.items() if k in suivies}
    if len(trouves) < 10:
        print(f"Trop peu de prix lus ({len(trouves)}) : fichiers inchanges.", file=sys.stderr)
        return 1

    # Prix de la veille : ceux du fichier actuel s'il date d'un autre jour, sinon ceux qu'il avait gardes.
    if ancien.get("date") and ancien["date"] != maintenant.strftime("%Y-%m-%d"):
        veille = {x["id"]: x["prix"] for x in ancien.get("pompes", [])}
    else:
        veille = ancien.get("veille", {})
    sortie = construire(trouves, veille, maintenant)
    sortie["veille"] = veille
    f_prix.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", "utf-8")

    hist = [h for h in hist if h["date"] != sortie["date"]]
    hist.append({"date": sortie["date"], "min": sortie["min_prix"], "max": sortie["max_prix"],
                 "moyenne": sortie["moyenne"], "gain_plein": sortie["plein_100_gain"]})
    f_hist.write_text(json.dumps(hist[-400:], ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{sortie['nb_pompes']} pompes, min {sortie['min_prix']} ({sortie['min_nom']}), max {sortie['max_prix']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
