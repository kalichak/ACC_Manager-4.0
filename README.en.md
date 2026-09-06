# ACC Manager

[Português (BR)](README.md) | [English](README.en.md) | [Deutsch](README.de.md)

Free and open-source desktop application for managing **Assetto Corsa
Competizione (ACC)** LAN servers.

ACC Manager combines dedicated-server control, telemetry analysis, setup
management, friends leaderboard and Discord notifications in one interface.

## Features

- **LAN / Radmin server:** configure track, car, sessions, weather and race
  conditions; start and stop the dedicated server; monitor its status.
- **Telemetry:** read MoTeC sessions and `.ld`/`.ldx` files, inspect lap times,
  speed, braking, G-forces and consistency, and update track profiles.
- **Setup manager:** list, filter, view and edit setups; replicate setups to
  other cars or tracks; adjust ACC 1.9 pressures; create setup suggestions.
- **Leaderboard:** publish best laps to Supabase, filter by car and track, and
  keep each driver's best time and history.
- **Optional modules and languages:** enable or hide each module in Settings
  without restarting, and switch the interface between Portuguese, English and
  German at runtime.

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
