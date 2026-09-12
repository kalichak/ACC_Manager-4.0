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
