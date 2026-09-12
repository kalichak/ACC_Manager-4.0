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
