# carburant

Relevé quotidien du prix de la Super 95 (E10) dans 27 pompes entre Waremme et Herstal, d'après carbu.com.

- `prix.json` : le relevé du jour (pompe la moins chère, la plus chère, coût du plein d'une Skoda Kamiq de 50 L, détail par pompe). Lu par bOS (ComfortClick).
- `historique.json` : un résumé par jour.
- `scrape.py` : le script de relevé, lancé chaque matin vers 05:50 (heure belge) par GitHub Actions.

Adresse du fichier pour bOS : https://raw.githubusercontent.com/Flyingjonathan/carburant/main/prix.json
