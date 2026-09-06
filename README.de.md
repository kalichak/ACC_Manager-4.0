# ACC Manager

[Português (BR)](README.md) | [English](README.en.md) | [Deutsch](README.de.md)

Kostenlose Open-Source-Desktopanwendung zur Verwaltung von LAN-Servern für
**Assetto Corsa Competizione (ACC)**.

ACC Manager verbindet die Verwaltung des Dedicated Servers, Telemetrieanalyse,
Setup-Verwaltung, Freundes-Rangliste und Discord-Benachrichtigungen in einer
Oberfläche.

## Funktionen

- **LAN- / Radmin-Server:** Strecke, Fahrzeug, Sessions, Wetter und
  Rennbedingungen konfigurieren sowie den Dedicated Server starten und stoppen.
- **Telemetrie:** MoTeC-Sessions und `.ld`-/`.ldx`-Dateien lesen, Rundenzeiten,
  Geschwindigkeit, Bremsungen, G-Kräfte und Konstanz analysieren.
- **Setup-Verwaltung:** Setups anzeigen, filtern, bearbeiten und auf andere
  Fahrzeuge oder Strecken kopieren.
- **Rangliste:** Beste Rundenzeiten an Supabase senden, nach Fahrzeug und
  Strecke filtern und die Historie behalten.
- **Optionale Module und Sprachen:** Module in den Einstellungen ohne Neustart
  ein- oder ausblenden und die Oberfläche zwischen Portugiesisch, Englisch und
  Deutsch wechseln.

## Voraussetzungen

- Windows 10 oder neuer.
- Python 3.10 oder neuer.
- Assetto Corsa Competizione.
- ACC Dedicated Server für die Serververwaltung.
- MoTeC i2 Pro und Telemetriedateien für die Telemetrieanalyse.
- Ein Supabase-Konto für die gemeinsame Rangliste.

## Installation und Verwendung

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Beim ersten Start wird `.env` erstellt. Über Einstellungen können Pfade,
Supabase, Discord und aktive Module konfiguriert werden. `.env` und
`ui_settings.json` sind lokale Dateien und dürfen nicht committet werden.

## Ausführbare Datei erstellen

Führen Sie `.\build_exe.bat` unter Windows aus. Die Anwendung wird unter
`dist\ACCManager\ACCManager.exe` erstellt. Verteilen Sie den gesamten Ordner
`dist\ACCManager`. Weitere Informationen stehen in
[EMPACOTAMENTO.md](EMPACOTAMENTO.md).

## Mitwirken

Erstellen Sie einen Fork, legen Sie einen Branch an, testen Sie Ihre
Änderungen und öffnen Sie einen Pull Request. Zugangsdaten und lokale,
generierte Dateien dürfen nicht in Commits gelangen. Der originale
Projektcode steht unter der MIT-Lizenz. Die vendorisierte Bibliothek
`core\vendor\ldparser.py` bleibt unter ihrer ursprünglichen GPLv3-Lizenz;
siehe [core/vendor/LICENSE-ldparser.txt](core/vendor/LICENSE-ldparser.txt).

## Lizenz

ACC Manager ist kostenlose Software unter der [MIT-Lizenz](LICENSE). Sie darf
verwendet, geändert und weiterverteilt werden, auch in kommerziellen
Projekten, sofern Copyright-Hinweis und Lizenztext erhalten bleiben.
