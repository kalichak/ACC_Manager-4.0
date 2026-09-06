import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from core import data_loader


class MotecParser:
    def __init__(self, motec_folder=None):
        if motec_folder:
            self.motec_folder = motec_folder
        else:
            candidates = [
                os.path.join(os.path.expanduser("~"), "OneDrive", "Documentos", "Assetto Corsa Competizione", "MoTeC"),
                os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa Competizione", "MoTeC"),
            ]
            self.motec_folder = next((p for p in candidates if os.path.exists(p)), candidates[0])

    def _parse_time_to_seconds(self, value):
        if not value:
            return 0.0
        cleaned = str(value).strip().replace(" ", "")
        if not cleaned:
            return 0.0
        parts = cleaned.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return float(cleaned)

    @staticmethod
    def _detail_value(details, name, default=""):
        """Busca campos MoTeC sem depender de caixa ou espacos extras."""
        wanted = " ".join(str(name).split()).casefold()
        for key, value in details.items():
            if " ".join(str(key).split()).casefold() == wanted:
                return value if value is not None else default
        return default

    def _fastest_marker_time(self, file_path):
        """Calcula a melhor volta quando o resumo final ainda nao existe."""
        try:
            root = ET.parse(file_path).getroot()
            times = sorted(
                float(marker.get("Time"))
                for marker in root.iter("Marker")
                if marker.get("ClassName") == "BCN" and marker.get("Time")
            )
        except (ET.ParseError, TypeError, ValueError):
            return 0.0

        if len(times) < 2:
            return 0.0
        return min((end - start) / 1_000_000.0 for start, end in zip(times, times[1:]))

    def _normalize_track_name(self, track_id):
        if not track_id:
            return "Desconhecida"
        track_id = track_id.strip()
        if "_" in track_id:
            track_id = track_id.replace("_", " ")
        return track_id.replace("-", " ").title()

    def _normalize_car_name(self, car_id):
        if not car_id:
            return "Carro Desconhecido"
        return data_loader.car_display_name(car_id)

    def _extract_from_filename(self, filename):
        stem = os.path.splitext(filename)[0]
        parts = stem.split("-")
        if len(parts) >= 2:
            track = parts[0].lower().strip()
            car = self._normalize_car_name(parts[1])
            driver_token = parts[2] if len(parts) >= 3 else "Piloto"
            return track, car, driver_token
        return "desconhecida", "Carro", "Piloto"

    def _parse_file_date(self, filename):
        stem = os.path.splitext(filename)[0]
        match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2})", stem)
        if match:
            try:
                return datetime.strptime(match.group(0), "%Y.%m.%d-%H.%M.%S").strftime("%d/%m/%Y %H:%M")
            except ValueError:
                pass
        return datetime.fromtimestamp(os.path.getmtime(os.path.join(self.motec_folder, filename))).strftime("%d/%m/%Y %H:%M")

    def read_session_file(self, file_path):
        summary = {
            "file": os.path.basename(file_path),
            "file_path": file_path,
            "details": {},
            "total_laps": 0,
            "fastest_time": "",
            "fastest_lap": "",
            "session_type": "Desconhecida",
            "track_temp": "N/A",
            "ambient_temp": "N/A",
            "vehicle_weight": "N/A"
        }

        if not os.path.exists(file_path):
            return summary

        try:
            root = ET.parse(file_path).getroot()
            details = {}
            for node in root.iter():
                if node.tag in {"String", "Number", "Boolean"}:
                    node_id = node.get("Id") or node.get("id") or node.get("Name") or node.get("name")
                    value = node.get("Value") or node.get("value")
                    if node_id:
                        details[node_id] = value

            summary["details"] = details
            summary["total_laps"] = int(self._detail_value(details, "Total Laps", 0) or 0)
            summary["fastest_time"] = self._detail_value(details, "Fastest Time")
            summary["fastest_lap"] = self._detail_value(details, "Fastest Lap")
            summary["session_type"] = self._detail_value(details, "Session", "N/A")
            summary["track_temp"] = self._detail_value(details, "Track Temperature", "N/A")
            summary["ambient_temp"] = self._detail_value(details, "Ambient Temperature", "N/A")
            summary["vehicle_weight"] = self._detail_value(details, "Vehicle Weight", "N/A")

        except Exception:
            pass

        return summary

    def get_best_laps(self):
        results = []
        if not os.path.exists(self.motec_folder):
            return results

        for filename in sorted(os.listdir(self.motec_folder)):
            if not filename.lower().endswith(".ldx"):
                continue

            file_path = os.path.join(self.motec_folder, filename)
            try:
                summary = self.read_session_file(file_path)
                fastest_time_value = summary.get("fastest_time")
                if not fastest_time_value:
                    marker_time = self._fastest_marker_time(file_path)
                    if marker_time > 0:
                        fastest_time_value = marker_time
                        summary["fastest_time"] = marker_time
                if not fastest_time_value:
                    continue

                track_id, car, driver = self._extract_from_filename(filename)
                track_name = self._normalize_track_name(track_id)
                time_sec = self._parse_time_to_seconds(fastest_time_value)
                if time_sec <= 0:
                    continue

                mins = int(time_sec // 60)
                secs = time_sec % 60
                formatted_time = f"{mins}:{secs:06.3f}"

                result = {
                    "track_id": track_id,
                    "track": track_name,
                    "driver": driver.replace("_", " ").title(),
                    "car": car,
                    "raw_time": time_sec,
                    "lap_time": formatted_time,
                    "date": self._parse_file_date(filename),
                    "total_laps": summary.get("total_laps", 0),
                    "fastest_lap": summary.get("fastest_lap", ""),
                    "session_type": summary.get("session_type"),
                    "track_temp": summary.get("track_temp"),
                    "ambient_temp": summary.get("ambient_temp"),
                    "vehicle_weight": summary.get("vehicle_weight"),
                    "file_name": filename,
                    "file_path": file_path,
                    "details": summary.get("details", {})
                }
                results.append(result)
            except Exception:
                continue

        results.sort(key=lambda x: x["raw_time"])
        return results

    def delete_telemetry(self, file_path):
        base, _extension = os.path.splitext(file_path)
        paths = (file_path, base + ".ld")
        for path in paths:
            if os.path.exists(path):
                os.remove(path)