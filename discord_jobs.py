"""Jobs automáticos para o Discord do ACC Manager.

Uso:
    python discord_jobs.py --run-now
    python discord_jobs.py --daily
    python discord_jobs.py --monthly
    python discord_jobs.py --loop

O modo --loop roda em background e verifica a cada 60 segundos se chegou
horário para enviar o snapshot do ranking, o resumo diário e o mensal.

Para rodar no Windows como serviço simples, pode usar:
    discord_jobs.bat
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import DISCORD_WEBHOOK_URL, SUPABASE_KEY, SUPABASE_URL
from core.discord_notifier import DiscordNotifier
from core.leaderboard_client import LeaderboardClient


def parse_iso_datetime(value):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            dt = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def fetch_rows(limit: int = 1000):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    client = LeaderboardClient(SUPABASE_URL, SUPABASE_KEY)
    try:
        rows = client.fetch_raw(limit=limit)
    except Exception as exc:
        print(f"[discord_jobs] erro ao consultar Supabase: {exc}")
        return []

    valid = []
    for row in rows or []:
        lap = row.get("lap_time_seconds")
        if lap is None:
            continue
        try:
            row["lap_time_seconds"] = float(lap)
        except (TypeError, ValueError):
            continue
        valid.append(row)
    return valid


def filter_by_period(rows: Iterable[dict], days: int | None = None, months: int | None = None):
    if not rows:
        return []

    now = datetime.utcnow()
    filtered = []
    for row in rows:
        recorded_at = parse_iso_datetime(row.get("recorded_at"))
        if not recorded_at:
            continue

        if days is not None:
            cutoff = now - timedelta(days=days)
            if recorded_at >= cutoff:
                filtered.append(row)
                continue

        if months is not None:
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if recorded_at >= month_start:
                filtered.append(row)
                continue

        if days is None and months is None:
            filtered.append(row)

    return filtered


def build_and_send_rank_snapshot(notifier: DiscordNotifier, rows: List[dict], driver_name: str | None = None):
    if not rows:
        print("[discord_jobs] nenhum tempo para snapshot do ranking.")
        return False

    ok = notifier.send_rank_snapshot(rows, driver_name=driver_name)
    print(f"[discord_jobs] ranking enviado: {ok}")
    return ok


def build_and_send_daily_summary(notifier: DiscordNotifier, rows: List[dict]):
    day_rows = filter_by_period(rows, days=1)
    if not day_rows:
        print("[discord_jobs] nenhum dado para resumo diário.")
        return False

    ok = notifier.send_daily_summary(day_rows, label="Hoje")
    print(f"[discord_jobs] resumo diário enviado: {ok}")
    return ok


def build_and_send_monthly_summary(notifier: DiscordNotifier, rows: List[dict]):
    month_rows = filter_by_period(rows, months=1)
    if not month_rows:
        print("[discord_jobs] nenhum dado para resumo mensal.")
        return False

    ok = notifier.send_monthly_summary(month_rows, label="Este mês")
    print(f"[discord_jobs] resumo mensal enviado: {ok}")
    return ok


def run_now():
    if not DISCORD_WEBHOOK_URL:
        print("[discord_jobs] DISCORD_WEBHOOK_URL não configurado.")
        return 1

    notifier = DiscordNotifier(DISCORD_WEBHOOK_URL)
    rows = fetch_rows(limit=500)

    if not rows:
        print("[discord_jobs] nenhuma linha lida do Supabase.")
        return 0

    build_and_send_rank_snapshot(notifier, rows)
    build_and_send_daily_summary(notifier, rows)
    build_and_send_monthly_summary(notifier, rows)
    return 0


def run_daily_only():
    if not DISCORD_WEBHOOK_URL:
        print("[discord_jobs] DISCORD_WEBHOOK_URL não configurado.")
        return 1

    notifier = DiscordNotifier(DISCORD_WEBHOOK_URL)
    rows = fetch_rows(limit=500)
    return 0 if build_and_send_daily_summary(notifier, rows) or not rows else 0


def run_monthly_only():
    if not DISCORD_WEBHOOK_URL:
        print("[discord_jobs] DISCORD_WEBHOOK_URL não configurado.")
        return 1

    notifier = DiscordNotifier(DISCORD_WEBHOOK_URL)
    rows = fetch_rows(limit=500)
    return 0 if build_and_send_monthly_summary(notifier, rows) or not rows else 0


def run_loop(interval_seconds: int = 60):
    print(f"[discord_jobs] loop iniciado. Verificando a cada {interval_seconds} segundos.")
    last_daily = None
    last_monthly = None

    while True:
        now = datetime.now()
        rows = fetch_rows(limit=500)

        if rows:
            if now.hour == 20 and now.minute == 0 and now.second < 5:
                today = now.date()
                if last_daily != today:
                    print(f"[discord_jobs] disparando resumo diário em {now.isoformat(timespec='seconds')}")
                    build_and_send_daily_summary(DiscordNotifier(DISCORD_WEBHOOK_URL), rows)
                    last_daily = today

            if now.day == 1 and now.hour == 20 and now.minute == 30 and now.second < 5:
                month_key = (now.year, now.month)
                if last_monthly != month_key:
                    print(f"[discord_jobs] disparando resumo mensal em {now.isoformat(timespec='seconds')}")
                    build_and_send_monthly_summary(DiscordNotifier(DISCORD_WEBHOOK_URL), rows)
                    last_monthly = month_key

            if now.hour in (20, 21) and now.minute % 15 == 0 and now.second < 5:
                print(f"[discord_jobs] disparando snapshot em {now.isoformat(timespec='seconds')}")
                build_and_send_rank_snapshot(DiscordNotifier(DISCORD_WEBHOOK_URL), rows)

        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="Jobs automáticos do Discord para o ACC Manager")
    parser.add_argument("--run-now", action="store_true", help="envia snapshot + diário + mensal agora")
    parser.add_argument("--daily", action="store_true", help="envia somente o resumo diário")
    parser.add_argument("--monthly", action="store_true", help="envia somente o resumo mensal")
    parser.add_argument("--loop", action="store_true", help="ativa o loop automático em background")
    parser.add_argument("--interval", type=int, default=60, help="intervalo em segundos do loop (padrão: 60)")
    args = parser.parse_args()

    if args.run_now:
        return run_now()
    if args.daily:
        return run_daily_only()
    if args.monthly:
        return run_monthly_only()
    if args.loop:
        return run_loop(interval_seconds=args.interval)

    print("[discord_jobs] sem ação definida. Use --run-now, --daily, --monthly ou --loop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
