## Datenquelle globale Strahlung
-https://re.jrc.ec.europa.eu/pvg_tools/en/#MR

## Winkelkoordinaten
-https://photovoltaik.org/solarstrom/solarenergie/neigungswinkel



## Setup

1. Pakete installieren: `pip install -r requirements.txt`
2. Lade Datenquelle in `input/global_irradiation_{location}.csv`
3. Lade Winkelkoordinaten in `data/data.json`
4. Nutze `SolarPredictionModel` aus `lib_py.solar_prediction` für Training und Prediction
5. Nutze `SolarPredictionModel` in `app.py` für Schnittstelle zu Solarvorhersage-Anwendung
6. Nutze `index.html` für Webinterface Solarvorhersage-Anwendung

## Link Webanwendung
https://evelinedura.eu.pythonanywhere.com