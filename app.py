from flask import Flask, render_template, request
import os
import json
from lib_py.solar_prediction_alt import SolarPredictionModel

app = Flask(__name__)

dirname = os.path.dirname(__file__)
DATA_PATH = os.path.join(dirname, "data", "data.json")
PARAMS_FILEPATH = os.path.join(dirname, "ml_model", "params.json")

solar_model = SolarPredictionModel()
solar_model.load_json_data(DATA_PATH)

with open(PARAMS_FILEPATH, "r") as f:
    all_location_params = json.load(f)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        location = request.form["location"]
        area = float(request.form["area"])
        ausrichtungswinkel = float(request.form["ausrichtungswinkel"])
        neigungswinkel = float(request.form["neigungswinkel"])

        params = all_location_params[location]

        energy_production = solar_model.calculate_energy_production(
            area, params["total_global_irradiation"], ausrichtungswinkel, neigungswinkel
        )

        if energy_production is not None:
            result = f"{energy_production:.2f}"
            return render_template("index.html", result=result)
        else:
            error = f"Ungültige Winkelwerte. Der Ausrichtungswinkel muss im Bereich zwischen -180° und 180° liegen, der Neigungswinkel im Bereich zwischen 0° und 90°."
            return render_template("index.html", energy_production=energy_production, error=error)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


