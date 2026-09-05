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

import requests


class DiscordNotifier:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or None
        self.enabled = bool(self.webhook_url)

    def _post(self, payload: dict) -> bool:
        if not self.enabled:
            return False
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=8)
            return resp.status_code in (200, 204)
        except Exception:
            return False

    def send_text(self, message: str) -> bool:
        return self._post({"content": message})

    def send_embed(self, title: str, description: str = "", color: int = 0xFF3B30, fields: list = None) -> bool:
        embed = {"title": title, "description": description, "color": color}
        if fields:
            embed["fields"] = [{"name": n, "value": v, "inline": inline} for n, v, inline in fields]
        return self._post({"embeds": [embed]})

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
