# carburant

Relevé quotidien du prix de la Super 95 (E10) dans 27 pompes entre Waremme et Herstal, d'après carbu.com.

- `prix.json` : le relevé du jour (pompe la moins chère, la plus chère, coût du plein d'une Skoda Kamiq de 50 L, détail par pompe). Lu par bOS (ComfortClick).
- `historique.json` : un résumé par jour.
- `data.json` et `index.html` : le détail par pompe et par jour, et la page qui l'affiche.
- `scrape.py` : le script de relevé, lancé chaque matin vers 05:50 (heure belge) par GitHub Actions.

Adresse du fichier pour bOS : https://raw.githubusercontent.com/Flyingjonathan/carburant/main/prix.json

## Diesel entre Dalhem et Rocourt

Même principe pour le Diesel (B7), dans 27 pompes entre Dalhem et Rocourt (Barchon, Visé, Haccourt, Oupeye, Wandre, Herstal, Vottem, Rocourt).

- `prix_diesel.json` : le relevé du jour (mêmes champs que `prix.json`). Lu par bOS (ComfortClick).
- `historique_diesel.json`, `data_diesel.json` et `diesel.html` : le résumé par jour, le détail par pompe et la page qui l'affiche.
- `scrape_diesel.py` : le script, lancé chaque matin vers 05:55 (heure belge), 5 minutes après le relevé Super 95.

Adresse du fichier pour bOS : https://raw.githubusercontent.com/Flyingjonathan/carburant/main/prix_diesel.json
