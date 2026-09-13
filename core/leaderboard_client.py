"""
Cliente do Ranking Compartilhado (Leaderboard de amigos)
==========================================================

Este modulo NAO sobe nenhum servidor - ele conversa via REST com um projeto
Supabase (banco Postgres com API REST pronta, free tier generoso, sem precisar
manter maquina ligada). Voce cria o projeto uma unica vez e distribui a
URL + chave "anon" para os seus amigos (via .env), assim todos leem e
escrevem na MESMA tabela.

COMO CRIAR (uma vez, leva ~5 minutos):
  1. Crie uma conta gratis em https://supabase.com e um novo projeto.
  2. No SQL Editor do projeto, rode:

        create table leaderboard (
            id bigint generated always as identity primary key,
            driver_name text not null,
            car_id text not null,
            track_id text not null,
            lap_time_seconds numeric not null,
            lap_time_formatted text not null,
            session_type text,
            track_temp text,
            ambient_temp text,
            recorded_at timestamptz default now()
        );

        create table setup_usage (
            id bigint generated always as identity primary key,
            driver_name text not null,
            car_id text not null,
            track_id text not null,
            setup_name text not null,
            setup_file_path text,
            preset_type text,
            notes text,
            setup_json jsonb,
            used_at timestamptz default now()
        );

        -- se a tabela ja existe, rode:
        alter table setup_usage add column if not exists setup_json jsonb;

        alter table leaderboard enable row level security;
        alter table setup_usage enable row level security;

        create policy "allow_insert" on leaderboard for insert to anon with check (true);
        create policy "allow_select" on leaderboard for select to anon using (true);
        create policy "allow_insert_setup_usage" on setup_usage for insert to anon with check (true);
        create policy "allow_select_setup_usage" on setup_usage for select to anon using (true);

  3. Em Project Settings > API, copie a "Project URL" e a chave "anon public".
  4. Cole essas duas informacoes no arquivo .env do ACC Manager:

        SUPABASE_URL=https://SEUPROJETO.supabase.co
        SUPABASE_KEY=sua_chave_anon_aqui

  5. Envie o MESMO .env (ou só essas 2 linhas) para os seus amigos usarem no
     .env deles. Pronto: todo mundo alimenta e le a mesma base de dados.

Por a tabela ser "insert-only" (sem update/delete liberado pra chave anon),
ninguem consegue apagar ou forjar o tempo de outra pessoa por acidente -
o pior que um amigo mal-intencionado poderia fazer e inserir um tempo falso
em nome dele mesmo, o que e um problema de confianca entre amigos, nao de
seguranca do banco.
"""

import requests


class LeaderboardClient:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.base_url = supabase_url.rstrip("/") if supabase_url else None
        self.api_key = supabase_key
        self.enabled = bool(self.base_url and self.api_key)

    def _headers(self, extra=None):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def submit_lap(self, driver_name: str, car_id: str, track_id: str,
                    lap_time_seconds: float, lap_time_formatted: str,
                    session_type: str = None, track_temp: str = None,
                    ambient_temp: str = None):
        if not self.enabled:
            raise RuntimeError(
                "Ranking compartilhado nao configurado. Defina SUPABASE_URL e "
                "SUPABASE_KEY no arquivo .env (veja instrucoes no topo deste arquivo)."
            )
        payload = {
            "driver_name": driver_name,
            "car_id": car_id,
            "track_id": track_id,
            "lap_time_seconds": lap_time_seconds,
            "lap_time_formatted": lap_time_formatted,
            "session_type": session_type,
            "track_temp": track_temp,
            "ambient_temp": ambient_temp,
        }
        resp = requests.post(
            f"{self.base_url}/rest/v1/leaderboard",
            json=payload,
            headers=self._headers({"Prefer": "return=minimal"}),
            timeout=10,
        )
        resp.raise_for_status()
        return True

    def fetch_raw(self, track_id: str = None, car_id: str = None, limit: int = 1000):
        if not self.enabled:
            return []
        params = {"select": "*", "order": "lap_time_seconds.asc", "limit": str(limit)}
        if track_id:
            params["track_id"] = f"eq.{track_id}"
        if car_id:
            params["car_id"] = f"eq.{car_id}"
        resp = requests.get(
            f"{self.base_url}/rest/v1/leaderboard",
            headers=self._headers(),
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def best_per_driver(rows: list) -> list:
        """Reduz o historico bruto ao melhor tempo de cada piloto por carro+pista."""
        best = {}
        for r in rows:
            key = (r.get("driver_name"), r.get("car_id"), r.get("track_id"))
            if key not in best or r["lap_time_seconds"] < best[key]["lap_time_seconds"]:
                best[key] = r
        result = list(best.values())
        result.sort(key=lambda r: r["lap_time_seconds"])
        return result


class SetupUsageClient:
    """Registra quais setups foram usados em cada sessão compartilhada."""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.base_url = supabase_url.rstrip("/") if supabase_url else None
        self.api_key = supabase_key
        self.enabled = bool(self.base_url and self.api_key)

    def _headers(self, extra=None):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def record_usage(self, driver_name: str, car_id: str, track_id: str,
                     setup_name: str, setup_file_path: str = None,
                     preset_type: str = None, notes: str = None,
                     setup_json: dict = None, created_by: str = None,
                     created_by_name: str = None):
        if not self.enabled:
            raise RuntimeError(
                "Registro de uso de setups nao configurado. Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env."
            )

        payload = {
            "driver_name": driver_name,
            "car_id": car_id,
            "track_id": track_id,
            "setup_name": setup_name,
            "setup_file_path": setup_file_path,
            "preset_type": preset_type,
            "notes": notes,
        }
        if setup_json is not None:
            payload["setup_json"] = setup_json
        if created_by is not None:
            payload["created_by"] = created_by
        if created_by_name is not None:
            payload["created_by_name"] = created_by_name
        resp = requests.post(
            f"{self.base_url}/rest/v1/setup_usage",
            json=payload,
            headers=self._headers({"Prefer": "return=minimal"}),
            timeout=10,
        )
        resp.raise_for_status()
        return True

    def fetch_recent(self, limit: int = 100):
        if not self.enabled:
            return []

        resp = requests.get(
            f"{self.base_url}/rest/v1/setup_usage",
            headers=self._headers(),
            params={"select": "*", "order": "used_at.desc", "limit": str(limit)},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def download_shared_setup(self, driver_name: str, car_id: str, track_id: str):
        if not self.enabled:
            return None

        resp = requests.get(
            f"{self.base_url}/rest/v1/setup_usage",
            headers=self._headers(),
            params={
                "select": "*",
                "driver_name": f"eq.{driver_name}",
                "car_id": f"eq.{car_id}",
                "track_id": f"eq.{track_id}",
                "order": "used_at.desc",
                "limit": "1",
            },
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            return None
        return rows[0]
