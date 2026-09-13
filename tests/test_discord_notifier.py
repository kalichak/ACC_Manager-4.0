import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.discord_notifier import DiscordNotifier


def test_validates_discord_webhook_url_format():
    assert DiscordNotifier.is_valid_webhook_url("https://discord.com/api/webhooks/123/abc") is True
    assert DiscordNotifier.is_valid_webhook_url("https://example.com/abc") is False
    assert DiscordNotifier.is_valid_webhook_url("") is False


def test_builds_setup_registration_embed_payload():
    notifier = DiscordNotifier("https://discord.com/api/webhooks/123/abc")
    payload = notifier.build_setup_usage_embed(
        driver_name="Joao",
        car_display="Porsche 911 GT3 R",
        track_display="Monza",
        setup_name="porsche_911_gt3_r_monza_qualy",
        preset_type="qualy",
    )

    assert payload["embeds"][0]["title"] == "🛠️ Setup registrado"
    assert payload["embeds"][0]["fields"][0]["name"] == "Carro"
    assert payload["embeds"][0]["fields"][1]["name"] == "Pista"
    assert payload["embeds"][0]["fields"][2]["name"] == "Tipo"


def test_builds_rank_snapshot_and_daily_monthly_reports():
    notifier = DiscordNotifier("https://discord.com/api/webhooks/123/abc")
    rows = [
        {"driver_name": "Ana", "car_id": "Porsche 911 GT3 R", "track_id": "monza", "lap_time_seconds": 90.0},
        {"driver_name": "Beto", "car_id": "Porsche 911 GT3 R", "track_id": "monza", "lap_time_seconds": 95.0},
        {"driver_name": "Ana", "car_id": "Ferrari 296 GT3", "track_id": "silverstone", "lap_time_seconds": 100.0},
    ]

    rank = notifier.build_rank_snapshot_embed(rows, driver_name="Ana")
    daily = notifier.build_daily_summary_embed(rows, "Hoje")
    monthly = notifier.build_monthly_summary_embed(rows, "Este mês")

    assert rank["embeds"][0]["title"] == "📊 Ranking atual do grupo"
    assert rank["embeds"][0]["fields"][0]["name"] == "Pista"
    assert rank["embeds"][0]["fields"][1]["name"] == "Carro"
    assert rank["embeds"][0]["fields"][2]["name"] == "Participantes"
    assert daily["embeds"][0]["title"] == "📅 Resumo diário"
    assert monthly["embeds"][0]["title"] == "📆 Resumo mensal"


def test_builds_race_summary_from_server_log():
    notifier = DiscordNotifier("https://discord.com/api/webhooks/123/abc")
    raw_log = """
    ==ERR: Didn't read TCP paket 70 to the end (1/6)
    New Split: 1079499 for carId 1001 with lapstates: HasCut,  (raw 1)
    Lap  carId 1001, driverId 0, lapTime 35791:23:647, timestampMS 1079499.000000, flags: 01, S1 0:30:100, S2 0:34:522, S3 1:16:507, fuel 0.000000, hasCut
    Lap carId 1001, driverId 0, lapTime 2:21:130, timestampMS 1079499.000000, flags: 01, S1 0:30:100, S2 0:34:522, S3 1:16:507, fuel 56.000000, hasCut
    Updated leaderboard for 2 clients (Race-<session> 2 min)
    """

    payload = notifier.build_race_log_summary_embed("LAN Radmin", "Monza", raw_log)

    assert payload["embeds"][0]["title"] == "🏁 Resumo da corrida"
    assert payload["embeds"][0]["fields"][0]["name"] == "Voltas"
    assert payload["embeds"][0]["fields"][1]["name"] == "Melhor volta"
    assert payload["embeds"][0]["fields"][2]["name"] == "Cortes"
    assert payload["embeds"][0]["fields"][3]["name"] == "Erros de rede"
