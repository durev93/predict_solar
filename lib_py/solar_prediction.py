import os
import json
import numpy as np
import pandas as pd
from datetime import date

class SolarPredictionModel:
    def __init__(self):
        self.locations = [
            "kassel", "stuttgart", "muenchen", "berlin",
            "frankfurt", "hamburg", "bonn", "leipzig"
        ]
        self.monthly_mean = None
        self.monthly_std = None
        self.std = None
        self.json_data = None
        self.current_location = None

    def fit(self, filepath, locations):
        for location in locations:
            df = self._import_data(filepath, location)
            self._set_global_irradiation_params(df)

    def predict_global_irradiation(self, date: date) -> float:
        mean = self.monthly_mean[date.month]
        return np.random.normal(mean, self.std)

    def export_global_irradiation_params(self, filepath, total_global_irradiation):
        params = dict(
            total_global_irradiation=total_global_irradiation
        )
        with open(filepath, "w") as f: 
            f.write(json.dumps(params) + '\n')

    def import_global_irradiation_params(self, filepath):
        with open(filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                params = json.loads(line)
                total_global_irradiation = params["total_global_irradiation"]

                print(f'{{"total_global_irradiation": {total_global_irradiation}}}')

    def _import_data(self, filepath, location):
        file_name = f"global_irradiation_{location}.csv"
        file_path = os.path.join(filepath, file_name)
        df = pd.read_csv(file_path, sep="\t\t", engine='python')
        df['month'] = pd.to_datetime(df['month'], format='%b').dt.month
        self.current_location = location
        return df

    def _set_global_irradiation_params(self, df):  
        self.monthly_mean = df.groupby("month")["H(h)_m"].mean().to_dict()
        self.monthly_std = df.groupby("month")["H(h)_m"].std().to_dict()
        self.std = df["H(h)_m"].std()

    def load_json_data(self, json_data_path):
        with open(json_data_path, "r") as file:
            self.json_data = json.load(file)

    def find_value(self, ausrichtungswinkel, neigungswinkel):
        if -180 <= ausrichtungswinkel <= 180 and 0 <= neigungswinkel <= 90:
            ausrichtungswinkel = abs(ausrichtungswinkel)
            rounded_ausrichtungswinkel = round(ausrichtungswinkel / 10) * 10
            rounded_neigungswinkel = round(neigungswinkel / 10) * 10 if neigungswinkel != 35 else 35

            key = f"({rounded_ausrichtungswinkel}, {rounded_neigungswinkel})"
            if key in self.json_data["data"]:
                return self.json_data["data"][key]
            else:
                return None 
        else:
            return None

    def calculate_energy_production(self, area_sqm, total_global_irradiation, ausrichtungswinkel, neigungswinkel):
        value_percent = self.find_value(ausrichtungswinkel, neigungswinkel)
        if value_percent is not None:
            return area_sqm * total_global_irradiation * (value_percent / 100.0) * 0.2253
        else:
            return None

def main():
    INPUT_PATH = os.path.join("..", "input")
    OUTPUT_PATH = os.path.join("..", "output")
    DATA_PATH = os.path.join("..", 'data.json')
    PARAMS_FILEPATH = os.path.join(OUTPUT_PATH, "params.json")

    solar_model = SolarPredictionModel()

    today = date.today()
    all_location_params = {}

    for i, location in enumerate(solar_model.locations):
        total_global_irradiation = 0
        solar_model.fit(INPUT_PATH, locations=[location])

        for month_offset in range(12):
            current_date = today.replace(month=(today.month + month_offset) % 12 + 1)
            prediction = solar_model.predict_global_irradiation(current_date)
            total_global_irradiation += prediction

        location_params = {
            "total_global_irradiation": total_global_irradiation
        }

        all_location_params[location] = location_params

    with open(PARAMS_FILEPATH, "w") as f:
        json.dump(all_location_params, f, indent=2)

    solar_model.load_json_data(DATA_PATH)
    
    area_sqm = 1

    for location, params in all_location_params.items():
        ausrichtungswinkel = 0
        neigungswinkel = 35

        energy_production = solar_model.calculate_energy_production(
            area_sqm, params["total_global_irradiation"], ausrichtungswinkel, neigungswinkel,
        )

        if energy_production is not None:
            print(f"Energieerzeugnis für die nächsten 12 Monate in {location} bei einer Solarfläche von {area_sqm} m2: {energy_production:.2f} kWh")
        else:
            print(f"Ungültige Winkelwerte für {location}. Der Ausrichtungswinkel muss im Bereich zwischen -180° und 180° liegen, der Neigungswinkel im Bereich zwischen 0° und 90°.")

if __name__ == "__main__":
    main()