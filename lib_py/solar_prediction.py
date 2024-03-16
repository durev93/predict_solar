import os
import json
import numpy as np
import pandas as pd
from datetime import date

class SolarPredictionModel:
    def __init__(self):
        self.locations = [
            "berlin", "bonn", "frankfurt", "hamburg", "kassel", "leipzig",  "muenchen", "stuttgart",
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

    def predict_global_irradiation(self, date: date) -> float:
        mean = self.monthly_mean[date.month]
        return np.random.normal(mean, self.std)

    def _load_json_data(self, json_data_path):
        with open(json_data_path, "r") as file:
            self.json_data = json.load(file)

    def _find_value(self, ausrichtungswinkel, neigungswinkel):
        if -180 <= ausrichtungswinkel <= 180 and 0 <= neigungswinkel <= 90:
            ausrichtungswinkel = abs(ausrichtungswinkel)
            rounded_ausrichtungswinkel = round(ausrichtungswinkel / 10) * 10
            rounded_neigungswinkel = round(neigungswinkel / 10) * 10 if neigungswinkel != 35 else 35

            key = f"({rounded_ausrichtungswinkel}, {rounded_neigungswinkel})"
            return self.json_data["data"].get(key, None)
        else:
            return None

    def calculate_energy_production(self, area, total_global_irradiation, ausrichtungswinkel, neigungswinkel):
        value_percent = self._find_value(ausrichtungswinkel, neigungswinkel)
        if value_percent is not None:
            return area * total_global_irradiation * (value_percent / 100.0) * 0.22
        else:
            return None

def main():
    INPUT_PATH = os.path.join("..", "input")
    OUTPUT_PATH = os.path.join("..", "output")
    DATA_PATH = os.path.join("..", "data", "data.json")
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

        location_params = {"total_global_irradiation": total_global_irradiation}
        all_location_params[location] = location_params

    with open(PARAMS_FILEPATH, "w") as f:
        json.dump(all_location_params, f, indent=2)

    solar_model._load_json_data(DATA_PATH)
    
    area = 1

    for location, params in all_location_params.items():
        ausrichtungswinkel = 0
        neigungswinkel = 35

        energy_production = solar_model.calculate_energy_production(
            area, params["total_global_irradiation"], ausrichtungswinkel, neigungswinkel,
        )

        if energy_production is not None:
            print(f"{location}: {energy_production:.2f} kWh")
        else:
            print(f"Ungültige Winkelwerte.")

if __name__ == "__main__":
    main()
