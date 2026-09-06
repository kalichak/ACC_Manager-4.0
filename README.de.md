# ACC Manager

[Português (BR)](README.md) | [English](README.en.md) | [Deutsch](README.de.md)

> Die deutsche Übersetzung ist vollständig.

Kostenlose Open-Source-Desktopanwendung zur Verwaltung von LAN-Servern für
**Assetto Corsa Competizione (ACC)**.

ACC Manager verbindet die Verwaltung des Dedicated Servers, Telemetrieanalyse,
Setup-Verwaltung, Freundes-Rangliste und Discord-Benachrichtigungen in einer
Oberfläche.

## Funktionen

- **LAN- / Radmin-Server:** Strecke, Fahrzeug, Sessions, Wetter und
  Rennbedingungen konfigurieren, den Dedicated Server starten und stoppen sowie
  seinen Status überwachen.
<img width="1279" height="789" alt="SERVER - DE" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />

- **Telemetrie:** MoTeC-Sessions und `.ld`-/`.ldx`-Dateien lesen, Rundenzeiten,
  Geschwindigkeit, Bremsungen, G-Kräfte und Konstanz analysieren sowie
  Streckenprofile aktualisieren.
<img width="1278" height="945" alt="TELEMETRY DE" src="https://github.com/user-attachments/assets/18393002-10c1-47ad-83cd-0c7dad6f8000" />

- **Setup-Verwaltung:** Setups anzeigen, filtern und bearbeiten, auf andere
  Fahrzeuge oder Strecken kopieren, Reifendrücke für ACC 1.9 anpassen und
  Setup-Vorschläge erstellen.
<img width="1280" height="1389" alt="SETUPS DE" src="https://github.com/user-attachments/assets/ab42d7e2-d502-44b0-90a2-23ec0b5f5975" />

- **Rangliste:** Beste Rundenzeiten an Supabase senden, nach Fahrzeug und
  Strecke filtern sowie die beste Zeit und Historie jedes Fahrers behalten.
<img width="1279" height="789" alt="SERVER - DE" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />

- **Optionale Module und Sprachen:** Module in den Einstellungen ohne Neustart
  ein- oder ausblenden und die Oberfläche zwischen Portugiesisch, Englisch und
  Deutsch wechseln.
<img width="927" height="607" alt="LANGUAGES DE" src="https://github.com/user-attachments/assets/f4c2a026-6c4a-403f-8602-8d0914e7dd21" />

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
