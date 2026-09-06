"""
Sistema de idiomas (i18n)
============================
Dicionario simples de traducoes + idioma atual guardado em memoria (uma
variavel de modulo). Nao usa nenhuma lib externa de i18n de proposito:
o projeto e pequeno, e um dict + funcao 'get' resolve sem dependencia nova.

Uso nos arquivos de ui/*:
    from ui.i18n import t
    self.setWindowTitle(t("settings_dialog_title"))

Se uma chave nao existir no idioma atual, cai para o portugues (pt); se
nem la existir, mostra a propria chave (fica facil de achar o que falta
traduzir, ao inves de quebrar ou mostrar string vazia).

Para adicionar um idioma novo: copie o bloco de "pt", traduza os valores
e adicione a chave em LANGUAGES.
Para adicionar uma tela nova ao sistema de traducao: adicione a MESMA
chave nos 3 idiomas (senao ela cai no fallback pt sempre).
"""

LANGUAGES = {
    "pt": "Portugues (BR)",
    "en": "English",
    "de": "Deutsch",
}

_current_language = "pt"


def set_language(lang: str):
    global _current_language
    if lang in TRANSLATIONS:
        _current_language = lang


def get_language() -> str:
    return _current_language


def t(key: str, **kwargs) -> str:
    """Retorna a string traduzida para o idioma atual. kwargs faz
    .format() no resultado, ex: t('paths_missing_item', name='MoTeC', path='C:/x')"""
    text = TRANSLATIONS.get(_current_language, {}).get(key)
    if text is None:
        text = TRANSLATIONS["pt"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


TRANSLATIONS = {
    "pt": {
        # Janela principal
        "app_title": "ACC Server LAN & Telemetry Manager",
        "tab_server": "Servidor LAN / Radmin",
        "tab_telemetry": "Telemetria e Rating (MoTeC)",
        "tab_setups": "Gerenciador de Setups",
        "tab_leaderboard": "Ranking dos Amigos",
        "btn_settings": "\u2699 Configuracoes",
        "no_modules_tab_title": "Aviso",
        "no_modules_message": "Nenhum modulo esta habilitado.\nAbra Configuracoes e habilite pelo menos um modulo.",
        "settings_saved_title": "Configuracoes salvas",
        "settings_saved_message": "As novas configuracoes ja foram aplicadas - nao precisa reiniciar o programa.",
        "paths_warning_title": "Atencao - Configuracao Necessaria",
        "paths_warning_intro": "Alguns diretorios configurados nao foram encontrados no seu sistema:",
        "paths_warning_footer": "Clique no botao '\u2699 Configuracoes' (canto superior direito) para ajustar os caminhos.",
        "path_label_server": "Servidor",
        "path_label_motec": "MoTeC",
        "path_label_setups": "Setups",
        "leaderboard_status_connected": "Ranking: Conectado",
        "leaderboard_status_disconnected": "Ranking: Nao configurado",
        "discord_status_connected": "Discord conectado",
        "discord_status_disconnected": "Discord nao configurado",
        "ui_settings_save_success_title": "Salvo",
        "ui_settings_save_success_message": "Configuracoes salvas com sucesso!",
        "ui_settings_save_error_title": "Erro",
        "ui_settings_save_error_message": "Nao foi possivel salvar: {error}",

        # Aba Servidor
        "box_general_title": "Servidor & Pista",
        "label_server_name": "Nome do Servidor:",
        "label_password": "Senha de Acesso:",
        "label_select_track": "Selecione a Pista:",
        "box_sessions_title": "Sessoes & Horario",
        "label_qualy": "Qualy (min):",
        "label_race": "Race (min):",
        "label_race_hour": "Hora da Corrida:",
        "box_weather_title": "Clima da Pista",
        "label_temperature": "Temperatura (C):",
        "label_clouds": "Nuvens (0.0 a 1.0):",
        "label_rain": "Chuva (0.0 a 1.0):",
        "label_randomness": "Aleatoriedade (0 a 7):",
        "box_rules_title": "Regras & Slots",
        "label_slots": "Slots:",
        "label_tm": " TM:",
        "label_sa": " SA:",
        "chk_lobby": "Registrar no lobby (Servidor Publico)",
        "chk_reset": "Limpar pasta 'current' antes de iniciar (Evita bugs)",
        "btn_save_settings": "Salvar Settings",
        "btn_start_server": "Iniciar Servidor",
        "btn_stop_server": "Fechar Servidor",
        "box_circuit_title": "Circuito",
        "no_track_image": "[Sem imagem disponivel para {track}]",
        "public_server_warning_title": "Aviso de Limitacao",
        "public_server_warning_message": "Servidores publicos exigem 3 TM e 70 SA para mais de 10 carros. Deseja iniciar?",
        "server_start_success_title": "Sucesso",
        "server_start_success_message": "Servidor iniciado com a pista {track}!",
        "server_start_error_title": "Erro ao Iniciar",
        "server_closed_title": "Servidor Finalizado",
        "server_closed_message": "accServer.exe foi fechado.",
        "server_stop_error_title": "Erro",

        # Dialogo de configuracoes
        "settings_dialog_title": "Configuracoes",
        "group_paths_title": "Pastas do ACC",
        "label_server_path": "Servidor Dedicado (accServer.exe)",
        "label_motec_path": "Pasta do MoTeC",
        "label_setups_path": "Pasta de Setups",
        "btn_browse": "Procurar...",
        "browse_dialog_title": "Selecione a pasta",
        "group_integrations_title": "Integracoes (opcionais)",
        "label_supabase_url": "Supabase URL:",
        "label_supabase_key": "Supabase Key:",
        "label_discord_webhook": "Discord Webhook:",
        "btn_test_discord": "Testar",
        "discord_test_empty_url": "Preencha a URL do webhook antes de testar.",
        "discord_test_message_body": "\U0001F527 Teste de configuracao do ACC Manager - webhook funcionando!",
        "discord_test_success": "Mensagem enviada! Confira o canal do Discord.",
        "discord_test_bad_status": "Discord respondeu {status}: {body}",
        "discord_test_exception": "Falha ao conectar: {error}",
        "group_modules_title": "Modulos ativos",
        "modules_hint": "Desmarque um modulo para esconder a aba dele. Nao precisa reiniciar o programa.",
        "module_server": "Servidor LAN",
        "module_telemetry": "Telemetria (MoTeC)",
        "module_setups": "Gerenciador de Setups",
        "module_leaderboard": "Ranking dos Amigos",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
    },
    "en": {
        "app_title": "ACC Server LAN & Telemetry Manager",
        "tab_server": "LAN / Radmin Server",
        "tab_telemetry": "Telemetry & Rating (MoTeC)",
        "tab_setups": "Setup Manager",
        "tab_leaderboard": "Friends Leaderboard",
        "btn_settings": "\u2699 Settings",
        "no_modules_tab_title": "Notice",
        "no_modules_message": "No module is enabled.\nOpen Settings and enable at least one module.",
        "settings_saved_title": "Settings saved",
        "settings_saved_message": "The new settings have been applied - no need to restart the app.",
        "paths_warning_title": "Warning - Configuration Needed",
        "paths_warning_intro": "Some configured folders were not found on your system:",
        "paths_warning_footer": "Click the '\u2699 Settings' button (top-right corner) to fix the paths.",
        "path_label_server": "Server",
        "path_label_motec": "MoTeC",
        "path_label_setups": "Setups",
        "leaderboard_status_connected": "Leaderboard: Connected",
        "leaderboard_status_disconnected": "Leaderboard: Not configured",
        "discord_status_connected": "Discord connected",
        "discord_status_disconnected": "Discord not configured",
        "ui_settings_save_success_title": "Saved",
        "ui_settings_save_success_message": "Settings saved successfully!",
        "ui_settings_save_error_title": "Error",
        "ui_settings_save_error_message": "Could not save: {error}",

        "box_general_title": "Server & Track",
        "label_server_name": "Server Name:",
        "label_password": "Access Password:",
        "label_select_track": "Select the Track:",
        "box_sessions_title": "Sessions & Time",
        "label_qualy": "Qualy (min):",
        "label_race": "Race (min):",
        "label_race_hour": "Race Hour:",
        "box_weather_title": "Track Weather",
        "label_temperature": "Temperature (C):",
        "label_clouds": "Clouds (0.0 to 1.0):",
        "label_rain": "Rain (0.0 to 1.0):",
        "label_randomness": "Randomness (0 to 7):",
        "box_rules_title": "Rules & Slots",
        "label_slots": "Slots:",
        "label_tm": " TM:",
        "label_sa": " SA:",
        "chk_lobby": "Register in lobby (Public Server)",
        "chk_reset": "Clear the 'current' folder before starting (avoids bugs)",
        "btn_save_settings": "Save Settings",
        "btn_start_server": "Start Server",
        "btn_stop_server": "Stop Server",
        "box_circuit_title": "Circuit",
        "no_track_image": "[No image available for {track}]",
        "public_server_warning_title": "Limit Warning",
        "public_server_warning_message": "Public servers require 3 TM and 70 SA for more than 10 cars. Start anyway?",
        "server_start_success_title": "Success",
        "server_start_success_message": "Server started at {track}!",
        "server_start_error_title": "Error Starting Server",
        "server_closed_title": "Server Stopped",
        "server_closed_message": "accServer.exe was closed.",
        "server_stop_error_title": "Error",

        "settings_dialog_title": "Settings",
        "group_paths_title": "ACC Folders",
        "label_server_path": "Dedicated Server (accServer.exe)",
        "label_motec_path": "MoTeC Folder",
        "label_setups_path": "Setups Folder",
        "btn_browse": "Browse...",
        "browse_dialog_title": "Select the folder",
        "group_integrations_title": "Integrations (optional)",
        "label_supabase_url": "Supabase URL:",
        "label_supabase_key": "Supabase Key:",
        "label_discord_webhook": "Discord Webhook:",
        "btn_test_discord": "Test",
        "discord_test_empty_url": "Fill in the webhook URL before testing.",
        "discord_test_message_body": "\U0001F527 ACC Manager configuration test - webhook working!",
        "discord_test_success": "Message sent! Check the Discord channel.",
        "discord_test_bad_status": "Discord responded {status}: {body}",
        "discord_test_exception": "Connection failed: {error}",
        "group_modules_title": "Active modules",
        "modules_hint": "Uncheck a module to hide its tab. No need to restart the app.",
        "module_server": "LAN Server",
        "module_telemetry": "Telemetry (MoTeC)",
        "module_setups": "Setup Manager",
        "module_leaderboard": "Friends Leaderboard",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
    },
    "de": {
        "app_title": "ACC Server LAN & Telemetry Manager",
        "tab_server": "LAN-/Radmin-Server",
        "tab_telemetry": "Telemetrie & Bewertung (MoTeC)",
        "tab_setups": "Setup-Verwaltung",
        "tab_leaderboard": "Freundes-Rangliste",
        "btn_settings": "\u2699 Einstellungen",
        "no_modules_tab_title": "Hinweis",
        "no_modules_message": "Kein Modul ist aktiviert.\nOeffne die Einstellungen und aktiviere mindestens ein Modul.",
        "settings_saved_title": "Einstellungen gespeichert",
        "settings_saved_message": "Die neuen Einstellungen wurden angewendet - ein Neustart ist nicht noetig.",
        "paths_warning_title": "Achtung - Konfiguration erforderlich",
        "paths_warning_intro": "Einige konfigurierte Ordner wurden auf Ihrem System nicht gefunden:",
        "paths_warning_footer": "Klicken Sie oben rechts auf '\u2699 Einstellungen', um die Pfade anzupassen.",
        "path_label_server": "Server",
        "path_label_motec": "MoTeC",
        "path_label_setups": "Setups",
        "leaderboard_status_connected": "Rangliste: Verbunden",
        "leaderboard_status_disconnected": "Rangliste: Nicht konfiguriert",
        "discord_status_connected": "Discord verbunden",
        "discord_status_disconnected": "Discord nicht konfiguriert",
        "ui_settings_save_success_title": "Gespeichert",
        "ui_settings_save_success_message": "Einstellungen erfolgreich gespeichert!",
        "ui_settings_save_error_title": "Fehler",
        "ui_settings_save_error_message": "Konnte nicht gespeichert werden: {error}",

        "box_general_title": "Server & Strecke",
        "label_server_name": "Servername:",
        "label_password": "Zugangspasswort:",
        "label_select_track": "Strecke auswaehlen:",
        "box_sessions_title": "Sessions & Uhrzeit",
        "label_qualy": "Qualifying (Min):",
        "label_race": "Rennen (Min):",
        "label_race_hour": "Rennzeit:",
        "box_weather_title": "Streckenwetter",
        "label_temperature": "Temperatur (C):",
        "label_clouds": "Wolken (0.0 bis 1.0):",
        "label_rain": "Regen (0.0 bis 1.0):",
        "label_randomness": "Zufall (0 bis 7):",
        "box_rules_title": "Regeln & Plaetze",
        "label_slots": "Plaetze:",
        "label_tm": " TM:",
        "label_sa": " SA:",
        "chk_lobby": "In Lobby registrieren (oeffentlicher Server)",
        "chk_reset": "'current'-Ordner vor dem Start leeren (vermeidet Fehler)",
        "btn_save_settings": "Einstellungen speichern",
        "btn_start_server": "Server starten",
        "btn_stop_server": "Server stoppen",
        "box_circuit_title": "Strecke",
        "no_track_image": "[Kein Bild verfuegbar fuer {track}]",
        "public_server_warning_title": "Hinweis zur Begrenzung",
        "public_server_warning_message": "Oeffentliche Server benoetigen 3 TM und 70 SA fuer mehr als 10 Autos. Trotzdem starten?",
        "server_start_success_title": "Erfolg",
        "server_start_success_message": "Server mit der Strecke {track} gestartet!",
        "server_start_error_title": "Fehler beim Start",
        "server_closed_title": "Server beendet",
        "server_closed_message": "accServer.exe wurde geschlossen.",
        "server_stop_error_title": "Fehler",

        "settings_dialog_title": "Einstellungen",
        "group_paths_title": "ACC-Ordner",
        "label_server_path": "Dedizierter Server (accServer.exe)",
        "label_motec_path": "MoTeC-Ordner",
        "label_setups_path": "Setup-Ordner",
        "btn_browse": "Durchsuchen...",
        "browse_dialog_title": "Ordner auswaehlen",
        "group_integrations_title": "Integrationen (optional)",
        "label_supabase_url": "Supabase-URL:",
        "label_supabase_key": "Supabase-Schluessel:",
        "label_discord_webhook": "Discord-Webhook:",
        "btn_test_discord": "Testen",
        "discord_test_empty_url": "Bitte die Webhook-URL vor dem Test ausfuellen.",
        "discord_test_message_body": "\U0001F527 ACC Manager Konfigurationstest - Webhook funktioniert!",
        "discord_test_success": "Nachricht gesendet! Pruefen Sie den Discord-Kanal.",
        "discord_test_bad_status": "Discord antwortete {status}: {body}",
        "discord_test_exception": "Verbindung fehlgeschlagen: {error}",
        "group_modules_title": "Aktive Module",
        "modules_hint": "Deaktivieren Sie ein Modul, um dessen Tab auszublenden. Kein Neustart noetig.",
        "module_server": "LAN-Server",
        "module_telemetry": "Telemetrie (MoTeC)",
        "module_setups": "Setup-Verwaltung",
        "module_leaderboard": "Freundes-Rangliste",
        "btn_save": "Speichern",
        "btn_cancel": "Abbrechen",
    },
}
