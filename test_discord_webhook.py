"""
Teste Forcado do Webhook do Discord
======================================

Roda isso direto, sem precisar abrir o ACC Manager nem ligar/desligar o
servidor de verdade:

    python test_discord_webhook.py

O script le o DISCORD_WEBHOOK_URL do seu .env e manda 3 mensagens de teste
pro canal: uma simples, uma igual a "servidor ligou" e uma igual a "novo
recorde", pra voce ver exatamente como cada uma vai aparecer no Discord.

Se der erro, o script mostra o motivo mais provavel (URL vazia, webhook
apagado, formato errado etc.) em vez de so falhar silenciosamente.
"""

import os
import sys

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")


def read_webhook_url_from_env() -> str:
    if not os.path.exists(ENV_FILE):
        return ""
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DISCORD_WEBHOOK_URL="):
                return line.split("=", 1)[1].strip()
    return ""


def send(webhook_url: str, payload: dict, label: str) -> bool:
    print(f"\n-> Enviando: {label} ...")
    try:
        resp = requests.post(webhook_url, json=payload, timeout=8)
    except requests.exceptions.RequestException as e:
        print(f"   FALHOU - erro de rede/conexao: {e}")
        return False

    if resp.status_code in (200, 204):
        print(f"   OK - Discord respondeu {resp.status_code}. Confira o canal.")
        return True

    print(f"   FALHOU - Discord respondeu {resp.status_code}")
    print(f"   Corpo da resposta: {resp.text[:300]}")
    if resp.status_code == 401:
        print("   -> Isso normalmente significa token/URL invalida (webhook editado ou nunca foi valido).")
    elif resp.status_code == 404:
        print("   -> Isso normalmente significa que o webhook foi APAGADO no Discord. Crie um novo.")
    elif resp.status_code == 429:
        print("   -> Rate limit do Discord - espere alguns segundos e tente de novo.")
    return False


def main():
    print("=" * 60)
    print("TESTE FORCADO DO WEBHOOK DO DISCORD - ACC Manager")
    print("=" * 60)

    webhook_url = read_webhook_url_from_env()

    if not webhook_url:
        print("\nDISCORD_WEBHOOK_URL nao encontrado ou vazio no .env.")
        print(f"Confira o arquivo: {ENV_FILE}")
        print("Ele deve ter uma linha assim:")
        print("DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcDEF...")
        sys.exit(1)

    if "discord.com/api/webhooks/" not in webhook_url:
        print(f"\nAVISO: a URL nao parece um webhook valido do Discord:\n  {webhook_url}")
        print("Confira se voce copiou a URL certa (deve conter 'discord.com/api/webhooks/').")

    print(f"\nURL encontrada no .env (parcial, por seguranca): {webhook_url[:45]}...")

    ok1 = send(webhook_url, {"content": "🔧 Teste simples do ACC Manager - se voce esta vendo isso, o webhook funciona!"}, "mensagem de texto simples")

    ok2 = send(webhook_url, {
        "embeds": [{
            "title": "🟢 Servidor LAN no ar",
            "description": "**[TESTE] LAN Radmin Session** acabou de subir.",
            "color": 0x04D361,
            "fields": [
                {"name": "Pista", "value": "Monza (Italia)", "inline": True},
                {"name": "Vagas", "value": "30", "inline": True},
            ],
        }]
    }, "embed de 'servidor iniciado' (exemplo)")

    ok3 = send(webhook_url, {
        "embeds": [{
            "title": "🏆 Novo recorde no grupo!",
            "description": "**[TESTE] Fulano** fez **1:29.392** em Brands Hatch (Reino Unido).",
            "color": 0xFFD60A,
            "fields": [{"name": "Carro", "value": "BMW M4 GT3", "inline": True}],
        }]
    }, "embed de 'novo recorde' (exemplo)")

    print("\n" + "=" * 60)
    if ok1 and ok2 and ok3:
        print("TUDO OK - as 3 mensagens foram entregues. O webhook esta funcionando.")
    else:
        print("Pelo menos uma mensagem falhou - veja os detalhes acima.")
    print("=" * 60)


if __name__ == "__main__":
    main()
