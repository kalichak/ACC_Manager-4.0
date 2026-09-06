# ACC Manager

[Português (BR)](README.md) | [English](README.en.md) | [Deutsch](README.de.md)

> Note: the full English translation is still in progress and will be completed soon. This file may not yet match the latest Portuguese version exactly.

Free and open-source desktop application for managing **Assetto Corsa
Competizione (ACC)** LAN servers.

ACC Manager combines dedicated-server control, telemetry analysis, setup
management, friends leaderboard and Discord notifications in one interface.

## Features

- **LAN / Radmin server:** configure track, car, sessions, weather and race
  conditions; start and stop the dedicated server; monitor its status.
<img width="1279" height="789" alt="SERVER - EN" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />

- **Telemetry:** read MoTeC sessions and `.ld`/`.ldx` files, inspect lap times,
  speed, braking, G-forces and consistency, and update track profiles.
<img width="1278" height="945" alt="TELEMETRY EN" src="https://github.com/user-attachments/assets/18393002-10c1-47ad-83cd-0c7dad6f8000" />

- **Setup manager:** list, filter, view and edit setups; replicate setups to
  other cars or tracks; adjust ACC 1.9 pressures; create setup suggestions.
<img width="1280" height="1389" alt="SETUPS EN" src="https://github.com/user-attachments/assets/ab42d7e2-d502-44b0-90a2-23ec0b5f5975" />

- **Leaderboard:** publish best laps to Supabase, filter by car and track, and
  keep each driver's best time and history.
<img width="1279" height="789" alt="SERVER - EN" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />

- **Optional modules and languages:** enable or hide each module in Settings
  without restarting, and switch the interface between Portuguese, English and
  German at runtime.
<img width="927" height="607" alt="LANGUAGES EN" src="https://github.com/user-attachments/assets/f4c2a026-6c4a-403f-8602-8d0914e7dd21" />

## Requirements

- Windows 10 or later.
- Python 3.10 or later.
- Assetto Corsa Competizione.
- ACC Dedicated Server for server management.
- MoTeC i2 Pro and telemetry files for telemetry analysis.
- A Supabase account for the shared leaderboard.

## Installation and usage

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The application creates `.env` on first run. Use Settings to configure paths,
Supabase, Discord and enabled modules. `.env` and `ui_settings.json` are local
files and must not be committed.

## Building the executable

Run `.\build_exe.bat` on Windows. The executable is generated at
`dist\ACCManager\ACCManager.exe`; distribute the entire `dist\ACCManager`
folder. See [EMPACOTAMENTO.md](EMPACOTAMENTO.md) for details.

## Contributing

Fork the project, create a branch, test your changes and open a pull request.
Keep credentials and generated local files out of commits. The original
project code is available under the MIT License. The vendored
`core\vendor\ldparser.py` library remains under its original GPLv3 license;
see [core/vendor/LICENSE-ldparser.txt](core/vendor/LICENSE-ldparser.txt).

## License

ACC Manager is free software distributed under the [MIT License](LICENSE).
It may be used, modified and redistributed, including in commercial projects,
provided that the copyright notice and license text are retained.
