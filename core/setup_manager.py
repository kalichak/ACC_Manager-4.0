import os
import json
import shutil
import copy

class SetupManager:
    def __init__(self, setups_folder=None):
        if setups_folder:
            self.setups_folder = setups_folder
        else:
            candidates = [
                os.path.join(os.path.expanduser("~"), "OneDrive", "Documentos", "Assetto Corsa Competizione", "Setups"),
                os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa Competizione", "Setups"),
            ]
            self.setups_folder = next((p for p in candidates if os.path.exists(p)), candidates[0])

    def list_all_setups(self):
        setups = []
        if not os.path.exists(self.setups_folder):
            return setups

        for car in sorted(os.listdir(self.setups_folder)):
            car_dir = os.path.join(self.setups_folder, car)
            if not os.path.isdir(car_dir):
                continue
            for track in sorted(os.listdir(car_dir)):
                track_dir = os.path.join(car_dir, track)
                if not os.path.isdir(track_dir):
                    continue
                for file_name in sorted(os.listdir(track_dir)):
                    if not file_name.endswith(".json"):
                        continue
                    file_path = os.path.join(track_dir, file_name)
                    setups.append({
                        "car": car,
                        "track": track,
                        "name": file_name.replace(".json", ""),
                        "file_path": file_path,
                    })
        return setups

    def get_setup_details(self, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return None

    def get_filtered_setups(self, car_filter=None, track_filter=None):
        setups = self.list_all_setups()
        if car_filter and car_filter not in ("Todos os carros", "Todos"):
            setups = [s for s in setups if s["car"] == car_filter]
        if track_filter and track_filter not in ("Todas as pistas", "Todas"):
            setups = [s for s in setups if s["track"] == track_filter]
        return setups

    def get_available_cars_and_tracks(self):
        cars = []
        tracks = set()
        if os.path.exists(self.setups_folder):
            for car in os.listdir(self.setups_folder):
                car_path = os.path.join(self.setups_folder, car)
                if os.path.isdir(car_path):
                    cars.append(car)
                    for track in os.listdir(car_path):
                        if os.path.isdir(os.path.join(car_path, track)):
                            tracks.add(track)
        return sorted(cars), sorted(list(tracks))

    def save_setup(self, file_path: str, data: dict):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def delete_setup(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_unique_filename(self, target_dir: str, base_name: str):
        new_path = os.path.join(target_dir, f"{base_name}.json")
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(target_dir, f"{base_name}_v{counter}.json")
            counter += 1
        return new_path

    def clone_setup(self, source_path: str, new_name: str):
        dir_name = os.path.dirname(source_path)
        new_path = self.get_unique_filename(dir_name, new_name)
        data = self.get_setup_details(source_path)
        self.save_setup(new_path, data)
        return new_path

    def replicate_setup(self, source_path: str, target_car: str, target_track: str, new_name: str, adjust_19: bool = False):
        data = self.get_setup_details(source_path)
        if not data:
            raise ValueError("Nao foi possivel ler o setup de origem.")

        if adjust_19:
            try:
                tyres = data.get("basicSetup", {}).get("tyres", {}).get("tyrePressure", [])
                new_tyres = []
                for t in tyres:
                    adjusted = round(t - 1.0, 1)
                    if adjusted < 20.0: adjusted = 20.0
                    new_tyres.append(adjusted)
                if len(new_tyres) == 4:
                    data["basicSetup"]["tyres"]["tyrePressure"] = new_tyres
            except Exception:
                pass

        target_dir = os.path.join(self.setups_folder, target_car, target_track)
        os.makedirs(target_dir, exist_ok=True)
        
        new_path = self.get_unique_filename(target_dir, new_name)
        self.save_setup(new_path, data)
        return new_path
    
    def generate_qualy_preset(self, setup_data: dict):
        new_data = copy.deepcopy(setup_data)
        try:
            new_data["basicSetup"]["strategy"]["fuel"] = 15
            new_data["basicSetup"]["strategy"]["frontBrakePadCompound"] = 0
            new_data["basicSetup"]["strategy"]["rearBrakePadCompound"] = 0
            tc1 = new_data["basicSetup"]["electronics"].get("tC1", 3)
            new_data["basicSetup"]["electronics"]["tC1"] = max(0, tc1 - 1)
        except KeyError: pass
        return new_data

    def generate_race_preset(self, setup_data: dict):
        new_data = copy.deepcopy(setup_data)
        try:
            new_data["basicSetup"]["strategy"]["fuel"] = 105
            new_data["basicSetup"]["strategy"]["frontBrakePadCompound"] = 1
            new_data["basicSetup"]["strategy"]["rearBrakePadCompound"] = 1
            bbias = new_data["basicSetup"]["alignment"].get("brakeBias", 55.0)
            new_data["basicSetup"]["alignment"]["brakeBias"] = round(bbias + 1.2, 1)
        except KeyError: pass
        return new_data

    def generate_wet_preset(self, setup_data: dict):
        new_data = copy.deepcopy(setup_data)
        try:
            new_data["basicSetup"]["tyres"]["tyreCompound"] = 1
            new_data["basicSetup"]["strategy"]["fuel"] = 105
            new_data["basicSetup"]["strategy"]["frontBrakePadCompound"] = 2
            new_data["basicSetup"]["strategy"]["rearBrakePadCompound"] = 2
            new_data["basicSetup"]["electronics"]["tC1"] = 7
            new_data["basicSetup"]["electronics"]["abs"] = 7
            arb_f = new_data["basicSetup"]["mechanicalBalance"].get("aRBFront", 2)
            arb_r = new_data["basicSetup"]["mechanicalBalance"].get("aRBRear", 2)
            new_data["basicSetup"]["mechanicalBalance"]["aRBFront"] = max(0, arb_f - 2)
            new_data["basicSetup"]["mechanicalBalance"]["aRBRear"] = max(0, arb_r - 2)
            ride_height = new_data["advancedSetup"]["aero"].get("rideHeight", [55, 55, 70, 70])
            if len(ride_height) == 4:
                new_data["advancedSetup"]["aero"]["rideHeight"] = [
                    ride_height[0] + 5, ride_height[1] + 5, 
                    ride_height[2] + 5, ride_height[3] + 5
                ]
        except KeyError: pass
        return new_data