import os
import json
import shutil
import copy
import math
import re

TELEMETRY_SUFFIX = ".telemetry.json"


def calculate_race_fuel(lap_time_seconds: float, fuel_per_lap: float, race_minutes: float,
                         formation_laps: int = 1, safety_laps: float = 1.0) -> dict:
    """Calcula quanto combustivel carregar pra corrida a partir do tempo de
    volta, do consumo por volta e da duracao da corrida (em minutos) - em
    vez do valor fixo usado antes nos presets. formation_laps cobre a
    volta de formacao/largada e safety_laps e uma margem extra (em voltas
    equivalentes) pra nao faltar combustivel por 1-2 voltas de diferenca
    entre a simulacao e a corrida real."""
    if lap_time_seconds is None or fuel_per_lap is None or race_minutes is None:
        raise ValueError("Tempo de volta, consumo por volta e duracao da corrida sao obrigatorios.")
    if lap_time_seconds <= 0 or fuel_per_lap <= 0 or race_minutes <= 0:
        raise ValueError("Tempo de volta, consumo por volta e duracao da corrida devem ser maiores que zero.")

    laps_in_race = (race_minutes * 60.0) / lap_time_seconds
    total_laps = math.ceil(laps_in_race) + formation_laps
    total_fuel = round((total_laps + safety_laps) * fuel_per_lap, 1)
    return {
        "laps_in_race": round(laps_in_race, 2),
        "total_laps": total_laps,
        "total_fuel": total_fuel,
    }


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

    @staticmethod
    def _is_setup_file(filename: str) -> bool:
        """Um setup de verdade e qualquer .json que NAO seja o arquivo
        auxiliar de telemetria (*.telemetry.json) criado por
        save_setup_with_telemetry. Sem esse filtro, os arquivos de
        telemetria aparecem misturados na lista de setups (podendo ser
        selecionados/editados por engano) e, se "Adicionar TLM" for usado
        neles, o sufixo .telemetry vai se acumulando (.telemetry.telemetry...)."""
        lower = filename.lower()
        return lower.endswith(".json") and not lower.endswith(TELEMETRY_SUFFIX)

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
                    if not self._is_setup_file(file_name):
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

    @staticmethod
    def normalize_setup_token(value):
        text = str(value or "").strip().lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text).strip("_")
        return text or "setup"

    def build_standardized_setup_name(self, car: str, track: str, preset_label: str = "setup", variant: str = None):
        parts = [self.normalize_setup_token(car), self.normalize_setup_token(track)]
        if preset_label:
            parts.append(self.normalize_setup_token(preset_label))
        if variant:
            parts.append(self.normalize_setup_token(variant))
        return "_".join(part for part in parts if part)

    def find_identical_setup(self, target_dir: str, data: dict, exclude_path: str = None):
        """Procura, dentro de target_dir, um setup .json (nunca um arquivo
        .telemetry.json auxiliar) com o MESMO conteudo de 'data'. Usada
        antes de clonar/replicar/renomear/gerar setups pra nunca criar uma
        copia identica com nome novo (_v1, _v2, _v3...) - se achar, devolve
        o caminho do arquivo ja existente; senao devolve None."""
        if not os.path.exists(target_dir):
            return None
        exclude_abs = os.path.abspath(exclude_path) if exclude_path else None
        for filename in os.listdir(target_dir):
            if not self._is_setup_file(filename):
                continue
            candidate_path = os.path.join(target_dir, filename)
            if exclude_abs and os.path.abspath(candidate_path) == exclude_abs:
                continue
            existing_data = self.get_setup_details(candidate_path)
            if existing_data == data:
                return candidate_path
        return None

    def resolve_setup_save_path(self, target_dir: str, base_name: str, data: dict, exclude_path: str = None):
        """Decide o caminho final pra salvar um setup evitando duplicar
        conteudo identico com nome novo: se ja existir um setup com o
        MESMO conteudo em target_dir, devolve (caminho_existente, False)
        pra quem chamou avisar o usuario em vez de duplicar; senao devolve
        (caminho_novo_unico, True), com o incremento _v1, _v2... de
        sempre."""
        duplicate = self.find_identical_setup(target_dir, data, exclude_path=exclude_path)
        if duplicate:
            return duplicate, False
        return self.get_unique_filename(target_dir, base_name), True

    def standardize_setup_names(self, folder_path=None):
        target_folder = folder_path or self.setups_folder
        if not os.path.exists(target_folder):
            return {"renamed": [], "duplicates": []}

        renamed = []
        duplicates = []
        for car_name in sorted(os.listdir(target_folder)):
            car_dir = os.path.join(target_folder, car_name)
            if not os.path.isdir(car_dir):
                continue
            for track_name in sorted(os.listdir(car_dir)):
                track_dir = os.path.join(car_dir, track_name)
                if not os.path.isdir(track_dir):
                    continue
                for filename in sorted(os.listdir(track_dir)):
                    if not self._is_setup_file(filename):
                        continue
                    file_path = os.path.join(track_dir, filename)
                    base_name = os.path.splitext(filename)[0]
                    base_label = base_name.lower()
                    if "qualy" in base_label:
                        preset = "qualy"
                    elif "race" in base_label:
                        preset = "race"
                    elif "wet" in base_label:
                        preset = "wet"
                    elif "smart" in base_label:
                        preset = "smart"
                    else:
                        preset = "setup"

                    normalized = self.build_standardized_setup_name(car_name, track_name, preset, variant=None)
                    if base_name.lower() == normalized:
                        continue

                    file_data = self.get_setup_details(file_path)
                    candidate = os.path.join(track_dir, f"{normalized}.json")

                    # Antes de gerar um _v1/_v2/_v3 novo, verifica se algum
                    # arquivo que ja ocupa um nome candidato tem conteudo
                    # IDENTICO ao que estamos renomeando - se tiver, esse
                    # arquivo e uma duplicata real e nao precisa (nem deve)
                    # virar mais uma copia com nome novo.
                    unique_candidate = candidate
                    counter = 1
                    is_duplicate = False
                    while os.path.exists(unique_candidate) and os.path.abspath(unique_candidate) != os.path.abspath(file_path):
                        existing_data = self.get_setup_details(unique_candidate)
                        if file_data is not None and existing_data == file_data:
                            duplicates.append({"kept": unique_candidate, "duplicate_of": file_path})
                            is_duplicate = True
                            break
                        unique_candidate = os.path.join(track_dir, f"{normalized}_v{counter}.json")
                        counter += 1

                    if is_duplicate:
                        continue

                    os.rename(file_path, unique_candidate)
                    renamed.append({"from": file_path, "to": unique_candidate})

        return {"renamed": renamed, "duplicates": duplicates}

    def save_setup_with_telemetry(self, setup_path: str, setup_data: dict, car_id: str, track_id: str, telemetry_laps: list = None, notes: str = None):
        # So regrava o setup em si se setup_path realmente APONTA pra um
        # setup (nunca pro sidecar .telemetry.json) - protege contra a UI
        # acidentalmente sobrescrever o payload de telemetria com o dict
        # do setup se algum caminho errado chegar aqui.
        if setup_path and self._is_setup_file(os.path.basename(setup_path)) and os.path.exists(setup_path):
            self.save_setup(setup_path, setup_data)

        # Sempre parte do nome "cru" do setup: tira a extensao .json e, se
        # setup_path ja for (ou tiver virado, por chamadas repetidas) um
        # arquivo .telemetry.json - inclusive encadeado tipo
        # "...telemetry.telemetry.telemetry.json" - tira TODOS os sufixos
        # ".telemetry" tambem. Assim o caminho final e sempre
        # "nome_do_setup.telemetry.json", nunca importa quantas vezes essa
        # funcao seja chamada nem qual variante do caminho for passada.
        base_path = setup_path
        if base_path.lower().endswith(".json"):
            base_path = base_path[: -len(".json")]
        while base_path.lower().endswith(".telemetry"):
            base_path = base_path[: -len(".telemetry")]
        telemetry_path = base_path + TELEMETRY_SUFFIX

        existing_laps = []
        existing_payload = {}
        if os.path.exists(telemetry_path):
            try:
                with open(telemetry_path, "r", encoding="utf-8-sig") as f:
                    existing_payload = json.load(f) or {}
                existing_laps = existing_payload.get("laps", []) or []
            except Exception:
                existing_laps = []
                existing_payload = {}

        # Soma de voltas de verdade: mescla as voltas novas com as que ja
        # estavam salvas, sem duplicar a mesma volta (identificada por
        # tempo + data do arquivo de origem). Antes disso, cada clique
        # simplesmente sobrescrevia "laps" com o que veio na chamada
        # (as vezes uma lista vazia), funcionando so como uma flag de
        # "tem telemetria sim/nao" em vez de acumular as voltas reais.
        merged_laps = list(existing_laps)
        seen_signatures = {
            (lap.get("raw_time"), lap.get("file_name")) for lap in existing_laps if isinstance(lap, dict)
        }
        for lap in (telemetry_laps or []):
            if not isinstance(lap, dict):
                continue
            signature = (lap.get("raw_time"), lap.get("file_name"))
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            merged_laps.append(lap)

        best_lap = None
        for lap in merged_laps:
            raw_time = lap.get("raw_time") if isinstance(lap, dict) else None
            if raw_time is None:
                continue
            if best_lap is None or raw_time < best_lap:
                best_lap = raw_time

        payload = {
            "car_id": car_id,
            "track_id": track_id,
            "setup_name": os.path.splitext(os.path.basename(base_path))[0],
            "saved_at": __import__("datetime").datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "notes": notes,
            "lap_count": len(merged_laps),
            "best_lap_seconds": best_lap,
            "laps": merged_laps,
        }
        with open(telemetry_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return telemetry_path

    def get_unique_filename(self, target_dir: str, base_name: str):
        new_path = os.path.join(target_dir, f"{base_name}.json")
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(target_dir, f"{base_name}_v{counter}.json")
            counter += 1
        return new_path

    def clone_setup(self, source_path: str, new_name: str):
        dir_name = os.path.dirname(source_path)
        data = self.get_setup_details(source_path)
        new_path, is_new = self.resolve_setup_save_path(dir_name, new_name, data, exclude_path=source_path)
        if is_new:
            self.save_setup(new_path, data)
        return new_path, is_new

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

        new_path, is_new = self.resolve_setup_save_path(target_dir, new_name, data)
        if is_new:
            self.save_setup(new_path, data)
        return new_path, is_new

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

    def generate_race_preset(self, setup_data: dict, race_minutes: float = None,
                              fuel_per_lap: float = None, lap_time_seconds: float = None):
        """race_minutes / fuel_per_lap / lap_time_seconds sao opcionais: se
        os tres forem informados, o combustivel e calculado com
        calculate_race_fuel (duracao da corrida + consumo real por volta).
        Se faltar algum, cai no valor fixo de 105L usado antes, entao quem
        ja usava esse preset sem esses dados continua funcionando igual."""
        new_data = copy.deepcopy(setup_data)
        try:
            if race_minutes and fuel_per_lap and lap_time_seconds:
                fuel_calc = calculate_race_fuel(lap_time_seconds, fuel_per_lap, race_minutes)
                new_data["basicSetup"]["strategy"]["fuel"] = fuel_calc["total_fuel"]
            else:
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