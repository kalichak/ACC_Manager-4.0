import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.leaderboard_client import SetupUsageClient


def test_record_setup_usage_posts_payload_to_supabase(monkeypatch):
    captured = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("core.leaderboard_client.requests.post", fake_post)

    client = SetupUsageClient("https://proj.supabase.co", "anon-key")
    result = client.record_usage(
        driver_name="Joao",
        car_id="porsche_911_gt3_r",
        track_id="silverstone",
        setup_name="base_q",
        setup_file_path="C:/Setups/Porsche/base_q.json",
        preset_type="qualy",
        notes="Configurado para qualy",
        setup_json={"basicSetup": {"tyres": {"tyrePressure": [20.0, 20.0, 19.5, 19.5]}}},
        created_by="user-123",
        created_by_name="Joao Silva",
    )

    assert result is True
    assert captured["url"] == "https://proj.supabase.co/rest/v1/setup_usage"
    assert captured["json"]["setup_name"] == "base_q"
    assert captured["json"]["preset_type"] == "qualy"
    assert captured["json"]["driver_name"] == "Joao"
    assert captured["json"]["created_by"] == "user-123"
    assert captured["json"]["created_by_name"] == "Joao Silva"
    assert captured["json"]["setup_json"]["basicSetup"]["tyres"]["tyrePressure"] == [20.0, 20.0, 19.5, 19.5]


def test_download_shared_setup_returns_json_from_latest_record(monkeypatch):
    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, headers, params, timeout):
        assert params["select"] == "*"
        assert params["order"] == "used_at.desc"
        return DummyResponse([
            {
                "driver_name": "Pedro",
                "car_id": "porsche_911_gt3_r",
                "track_id": "cota",
                "setup_name": "qualy_1",
                "setup_json": {"basicSetup": {"alignment": {"camber": 3.5}}},
            }
        ])

    monkeypatch.setattr("core.leaderboard_client.requests.get", fake_get)

    client = SetupUsageClient("https://proj.supabase.co", "anon-key")
    shared = client.download_shared_setup("Pedro", "porsche_911_gt3_r", "cota")

    assert shared["setup_name"] == "qualy_1"
    assert shared["setup_json"]["basicSetup"]["alignment"]["camber"] == 3.5
