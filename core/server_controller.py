import os
import shutil
import json
import subprocess
import psutil

class ServerController:
    def __init__(self, server_root_path: str):
        self.server_root = server_root_path
        self.cfg_path = os.path.join(self.server_root, "cfg")
        self.exe_path = os.path.join(self.server_root, "accServer.exe")

    def _write_json_to_targets(self, file_name: str, data: dict, targets=None):
        if targets is None:
            targets = [self.cfg_path]

        for folder in targets:
            if not folder:
                continue
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, file_name)
            
            with open(file_path, "w", encoding="utf-16le") as f:
                json.dump(data, f, indent=2)

    def is_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == "accserver.exe":
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def stop_server(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == "accserver.exe":
                    proc.kill()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def _delete_path_if_exists(self, path):
        if not path or not os.path.exists(path):
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=False)
            else:
                os.remove(path)
        except Exception:
            pass

    def clean_current_folder(self):
        candidates = [
            os.path.join(self.server_root, "cfg", "current"),
            os.path.join(self.server_root, "current"),
        ]
        for folder in candidates:
            self._delete_path_if_exists(folder)

    def write_settings_json(
        self,
        server_name: str,
        password: str,
        max_car_slots: int = 30,
        track_medals_requirement: int = 0,
        safety_rating_requirement: int = 0,
    ):
        spectator_pass = password + "_spectator" if password else "senha_espectador_oculta"

        data = {
            "serverName": server_name,
            "password": password,
            "spectatorPassword": spectator_pass,
            "adminPassword": "admin123",
            "carGroup": "FreeForAll", 
            "maxCarSlots": int(max_car_slots),
            "trackMedalsRequirement": int(track_medals_requirement),
            "safetyRatingRequirement": int(safety_rating_requirement),
            "racecraftRatingRequirement": -1,
            "dumpLeaderboards": 1,
            "isRaceLocked": 0,
            "randomizeTrackWhenEmpty": 0,
            "allowAutoDQ": 1,
            "shortFormationLap": 1,
            "dumpEntryList": 0,
            "formationLapType": 3,
            "configVersion": 1
        }
        self._write_json_to_targets("settings.json", data)

    def write_configuration_json(
        self,
        tcp_port: int = 9231,
        udp_port: int = 9232,
        register_to_lobby: int = 0,
        max_connections: int = 30,
        lan_discovery: int = 1,
    ):
        data = {
            "tcpPort": tcp_port,
            "udpPort": udp_port,
            "maxConnections": max_connections,
            "lanDiscovery": lan_discovery,
            "registerToLobby": register_to_lobby,
            "configVersion": 1
        }
        self._write_json_to_targets("configuration.json", data)

    def write_event_json(
        self, 
        track: str, 
        q_minutes: int, 
        r_minutes: int,
        hour: int,
        temp: int,
        cloud: float,
        rain: float,
        randomness: int
    ):
        q_hour = (hour - 2) % 24 

        data = {
            "track": track,
            "preRaceWaitingTimeSeconds": 60,
            "sessionOverTimeSeconds": 120,
            "ambientTemp": temp,
            "cloudLevel": round(cloud, 2),
            "rain": round(rain, 2),
            "weatherRandomness": randomness,
            "configVersion": 1,
            "sessions": [
                {"sessionType": "Q", "sessionDurationMinutes": q_minutes, "dayOfWeekend": 2, "hourOfDay": q_hour, "timeMultiplier": 1},
                {"sessionType": "R", "sessionDurationMinutes": r_minutes, "dayOfWeekend": 2, "hourOfDay": hour, "timeMultiplier": 1},
            ]
        }
        self._write_json_to_targets("event.json", data)

    def start(
        self,
        server_name: str,
        password: str,
        track: str,
        q_min: int,
        r_min: int,
        max_car_slots: int = 30,
        track_medals_requirement: int = 0,
        safety_rating_requirement: int = 0,
        register_to_lobby: int = 0,
        force_current_reset: bool = True,
        hour: int = 14,
        temp: int = 22,
        cloud: float = 0.1,
        rain: float = 0.0,
        randomness: int = 1
    ):
        if not os.path.exists(self.exe_path):
            raise FileNotFoundError(f"accServer.exe não encontrado em:\n{self.exe_path}")

        self.stop_server()

        if force_current_reset:
            self.clean_current_folder()

        os.makedirs(self.cfg_path, exist_ok=True)

        self.write_settings_json(
            server_name,
            password,
            max_car_slots=max_car_slots,
            track_medals_requirement=track_medals_requirement,
            safety_rating_requirement=safety_rating_requirement,
        )
        self.write_configuration_json(
            register_to_lobby=register_to_lobby,
            max_connections=max_car_slots + 5,
        )
        self.write_event_json(
            track=track, 
            q_minutes=q_min, 
            r_minutes=r_min, 
            hour=hour, 
            temp=temp, 
            cloud=cloud, 
            rain=rain, 
            randomness=randomness
        )

        subprocess.Popen(
            [self.exe_path],
            cwd=self.server_root,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )