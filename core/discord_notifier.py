"""
Notificador Discord
======================

Usa um Webhook do Discord (nao precisa criar bot nem pedir permissao de
servidor): em qualquer canal do seu servidor Discord, va em
Configuracoes do Canal > Integracoes > Webhooks > Novo Webhook, copie a URL
e cole no .env como DISCORD_WEBHOOK_URL.

Como funciona: um webhook e so uma URL secreta que aceita POST com uma
mensagem JSON e a posta naquele canal. Qualquer processo (inclusive este
app) pode enviar mensagem sem autenticacao alem da propria URL.
"""

import re

import requests


class DiscordNotifier:
    DISCORD_WEBHOOK_RE = re.compile(r"^https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+/?$")

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url.strip() if isinstance(webhook_url, str) else None
        self.enabled = self.is_valid_webhook_url(self.webhook_url)

    @classmethod
    def is_valid_webhook_url(cls, value: str) -> bool:
        if not value or not isinstance(value, str):
            return False
        value = value.strip()
        if not value:
            return False
        return bool(cls.DISCORD_WEBHOOK_RE.match(value))

    def set_webhook_url(self, webhook_url: str) -> bool:
        self.webhook_url = webhook_url.strip() if isinstance(webhook_url, str) else None
        self.enabled = self.is_valid_webhook_url(self.webhook_url)
        return self.enabled

    def _post(self, payload: dict) -> bool:
        if not self.enabled or not self.webhook_url:
            return False
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=8)
            if resp.status_code in (200, 204):
                return True
            if resp.status_code in (400, 401, 404, 429):
                return False
            return False
        except Exception:
            return False

    def send_text(self, message: str) -> bool:
        if not message or not isinstance(message, str):
            return False
        return self._post({"content": message})

    def send_embed(self, title: str, description: str = "", color: int = 0xFF3B30, fields: list = None) -> bool:
        if not title or not isinstance(title, str):
            return False
        embed = {"title": title, "description": description or "", "color": color}
        if fields:
            embed["fields"] = [{"name": n, "value": str(v), "inline": bool(inline)} for n, v, inline in fields]
        return self._post({"embeds": [embed]})

    def build_setup_usage_embed(self, driver_name: str, car_display: str, track_display: str,
                               setup_name: str, preset_type: str = "manual", notes: str = None):
        preset_label = (preset_type or "manual").strip().lower() or "manual"
        title = "🛠️ Setup registrado"
        description = f"**{driver_name}** usou o setup **{setup_name}** em **{track_display}**."
        fields = [
            ("Carro", car_display or "Não informado", True),
            ("Pista", track_display or "Não informado", True),
            ("Tipo", preset_label, True),
        ]
        if notes:
            fields.append(("Notas", notes[:200], False))
        return {"embeds": [{"title": title, "description": description, "color": 0x007AFF, "fields": [
            {"name": name, "value": value, "inline": inline} for name, value, inline in fields
        ]}]}

    def notify_setup_usage(self, driver_name: str, car_display: str, track_display: str,
                           setup_name: str, preset_type: str = "manual", notes: str = None):
        if not driver_name or not setup_name:
            return False
        payload = self.build_setup_usage_embed(
            driver_name=driver_name,
            car_display=car_display,
            track_display=track_display,
            setup_name=setup_name,
            preset_type=preset_type,
            notes=notes,
        )
        return self._post(payload)

    # --- Eventos prontos do ACC Manager ---

    def notify_server_started(self, server_name: str, track_display: str, slots: int):
        self.send_embed(
            title="🟢 Servidor LAN no ar",
            description=f"**{server_name}** acabou de subir.",
            color=0x04D361,
            fields=[
                ("Pista", track_display, True),
                ("Vagas", str(slots), True),
            ],
        )

    def notify_server_stopped(self, server_name: str):
        self.send_embed(
            title="🔴 Servidor LAN encerrado",
            description=f"**{server_name}** foi fechado.",
            color=0xFF4B3E,
        )

    def notify_new_record(self, driver_name: str, car_display: str, track_display: str, lap_time_formatted: str):
        self.send_embed(
            title="🏆 Novo recorde no grupo!",
            description=f"**{driver_name}** fez **{lap_time_formatted}** em {track_display}.",
            color=0xFFD60A,
            fields=[("Carro", car_display, True)],
        )

    def build_rank_snapshot_embed(self, rows: list, driver_name: str = None):
        if not rows:
            return {"embeds": [{"title": "📊 Ranking atual do grupo", "description": "Nenhum tempo registrado ainda.", "color": 0x7A5AF8}]}

        try:
            from config import TRACKS_DATABASE, CAR_NAMES_MAPPING
        except Exception:
            TRACKS_DATABASE = {}
            CAR_NAMES_MAPPING = {}

        best_by_driver = {}
        track_counts = {}
        car_counts = {}
        for row in rows:
            key = row.get("driver_name") or "Desconhecido"
            current = best_by_driver.get(key)
            candidate = float(row.get("lap_time_seconds", 999999))
            if current is None or candidate < current:
                best_by_driver[key] = candidate

            track_id = row.get("track_id")
            car_id = row.get("car_id")
            if track_id:
                track_label = TRACKS_DATABASE.get(track_id, str(track_id))
                track_counts[track_label] = track_counts.get(track_label, 0) + 1
            if car_id:
                car_label = CAR_NAMES_MAPPING.get(car_id, str(car_id))
                car_counts[car_label] = car_counts.get(car_label, 0) + 1

        ordered = sorted(best_by_driver.items(), key=lambda item: item[1])
        ranking_text = "\n".join(
            f"{idx}° **{name}** — {self._format_lap_seconds(value)}"
            for idx, (name, value) in enumerate(ordered[:5], start=1)
        )

        description = ranking_text or "Sem dados"
        if driver_name:
            my_rank = next((idx for idx, (name, _) in enumerate(ordered, start=1) if name == driver_name), None)
            if my_rank:
                description += f"\n\n📍 Sua posição atual: **{my_rank}°**"

        primary_track = max(track_counts.items(), key=lambda item: item[1])[0] if track_counts else "Não informado"
        primary_car = max(car_counts.items(), key=lambda item: item[1])[0] if car_counts else "Não informado"

        return {
            "embeds": [{
                "title": "📊 Ranking atual do grupo",
                "description": description,
                "color": 0x7A5AF8,
                "fields": [
                    {"name": "Pista", "value": primary_track, "inline": True},
                    {"name": "Carro", "value": primary_car, "inline": True},
                    {"name": "Participantes", "value": str(len(ordered)), "inline": True},
                ],
            }]
        }

    def build_daily_summary_embed(self, rows: list, label: str = "Hoje"):
        title = "📅 Resumo diário"
        if not rows:
            return {"embeds": [{"title": title, "description": f"{label}: nenhum dado registrado.", "color": 0x04D361}]}

        best_by_driver = {}
        for row in rows:
            key = row.get("driver_name") or "Desconhecido"
            current = best_by_driver.get(key)
            candidate = float(row.get("lap_time_seconds", 999999))
            if current is None or candidate < current:
                best_by_driver[key] = candidate

        ordered = sorted(best_by_driver.items(), key=lambda item: item[1])
        leader_name, leader_time = ordered[0]
        content = f"{label}: o melhor tempo foi de **{leader_name}** em **{self._format_lap_seconds(leader_time)}**."
        return {"embeds": [{"title": title, "description": content, "color": 0x04D361}]}

    def build_monthly_summary_embed(self, rows: list, label: str = "Este mês"):
        title = "📆 Resumo mensal"
        if not rows:
            return {"embeds": [{"title": title, "description": f"{label}: nenhum dado registrado.", "color": 0xFFD60A}]}

        best_by_driver = {}
        for row in rows:
            key = row.get("driver_name") or "Desconhecido"
            current = best_by_driver.get(key)
            candidate = float(row.get("lap_time_seconds", 999999))
            if current is None or candidate < current:
                best_by_driver[key] = candidate

        ordered = sorted(best_by_driver.items(), key=lambda item: item[1])
        summary_lines = "\n".join(
            f"{idx}° **{name}** — {self._format_lap_seconds(value)}"
            for idx, (name, value) in enumerate(ordered[:5], start=1)
        )
        return {"embeds": [{
            "title": title,
            "description": f"{label}: os melhores tempos do período foram:\n{summary_lines}",
            "color": 0xFFD60A,
        }]}

    @staticmethod
    def _parse_race_log_summary(raw_log: str):
        text = (raw_log or "").replace("\r", "")
        if not text:
            return {
                "lap_count": 0,
                "best_lap": None,
                "cut_count": 0,
                "network_errors": 0,
                "session_summary": "Nenhum log recebido.",
            }

        lap_count = 0
        cut_count = 0
        network_errors = 0
        best_lap_seconds = None
        best_lap_label = None

        for line in text.splitlines():
            if "Lap carId" in line or "Lap  carId" in line:
                match = re.search(r"lapTime\s+([0-9]+:[0-9]{2}:[0-9]{3}|[0-9]+:[0-9]{2}\.[0-9]{3}|[0-9]+:[0-9]{3})", line)
                if match:
                    lap_count += 1
                    lap_value = match.group(1)
                    try:
                        raw = lap_value.replace(".", ":")
                        parts = raw.split(":")
                        if len(parts) == 3:
                            minutes, seconds, millis = parts
                            seconds_total = int(minutes) * 60 + int(seconds) + int(millis) / 1000.0
                        elif len(parts) == 2:
                            minutes, seconds = parts
                            seconds_total = int(minutes) * 60 + float(seconds)
                        else:
                            seconds_total = float(lap_value)
                    except ValueError:
                        continue
                    if best_lap_seconds is None or seconds_total < best_lap_seconds:
                        best_lap_seconds = seconds_total
                        best_lap_label = self._format_lap_seconds(seconds_total) if hasattr(self, '_format_lap_seconds') else lap_value

                if "hasCut" in line.lower():
                    cut_count += 1

            if "Didn't read TCP" in line or "timestamp is" in line and "future" in line:
                network_errors += 1

        session_summary = "Sem eventos relevantes detectados."
        if lap_count:
            session_summary = f"{lap_count} volta(s) detectada(s) no servidor."
        elif network_errors:
            session_summary = "Corrida iniciada, mas houve erros de rede e sincronização."

        return {
            "lap_count": lap_count,
            "best_lap": best_lap_label,
            "cut_count": cut_count,
            "network_errors": network_errors,
            "session_summary": session_summary,
        }

    def build_race_log_summary_embed(self, server_name: str, track_display: str, raw_log: str):
        stats = self._parse_race_log_summary(raw_log)
        description = stats["session_summary"]
        title = "🏁 Resumo da corrida"
        fields = [
            ("Voltas", str(stats["lap_count"]), True),
            ("Melhor volta", stats["best_lap"] or "—", True),
            ("Cortes", str(stats["cut_count"]), True),
            ("Erros de rede", str(stats["network_errors"]), True),
        ]
        return {
            "embeds": [{
                "title": title,
                "description": f"**{server_name}** em **{track_display}**\n{description}",
                "color": 0x00D26A,
                "fields": [
                    {"name": name, "value": value, "inline": inline}
                    for name, value, inline in fields
                ],
            }]
        }

    @staticmethod
    def _format_lap_seconds(value):
        try:
            seconds = float(value)
            minutes, remainder = divmod(seconds, 60)
            return f"{int(minutes):02d}:{remainder:05.3f}"
        except (TypeError, ValueError):
            return "00:00.000"

    def send_rank_snapshot(self, rows: list, driver_name: str = None):
        return self._post(self.build_rank_snapshot_embed(rows, driver_name=driver_name))

    def send_daily_summary(self, rows: list, label: str = "Hoje"):
        return self._post(self.build_daily_summary_embed(rows, label=label))

    def send_monthly_summary(self, rows: list, label: str = "Este mês"):
        return self._post(self.build_monthly_summary_embed(rows, label=label))

    def validate_webhook(self) -> tuple[bool, str]:
        if not self.webhook_url:
            return False, "Webhook nao configurado."
        if not self.is_valid_webhook_url(self.webhook_url):
            return False, "URL do webhook invalida. Use uma URL do Discord do tipo https://discord.com/api/webhooks/..."
        try:
            resp = requests.post(self.webhook_url, json={"content": "✅ Teste de validacao do webhook do ACC Manager"}, timeout=8)
            if resp.status_code in (200, 204):
                return True, "Webhook validado com sucesso."
            if resp.status_code == 401:
                return False, "Webhook rejeitado pelo Discord (token ou URL invalida)."
            if resp.status_code == 404:
                return False, "Webhook nao encontrado no Discord. O canal ou webhook foi removido."
            if resp.status_code == 429:
                return False, "Discord limitou as requisicoes. Tente novamente em alguns segundos."
            return False, f"Discord respondeu com status {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            return False, f"Erro de rede ao validar o webhook: {exc}"
