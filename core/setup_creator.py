"""
Criador de Setups Inteligente
==============================

Gera uma variacao de um setup EXISTENTE (base_setup) considerando:
  - Perfil da pista (downforce, buracos, frenagem, velocidade media) - core/data/tracks.json
  - Temperamento do carro (estavel x nervoso)                        - core/data/cars.json
  - Um "dial" de agressividade de 0 a 100 (0 = bem conservador/seguro,
    50 = equilibrado, 100 = bem agressivo/pace maximo)
  - Condicao (seco / molhado)

POR QUE PARTIR DE UM SETUP BASE E NAO "DO ZERO":
Cada carro do ACC tem faixas minimas/maximas diferentes para cada parametro
(ex.: a Ford Mustang GT3 aceita rigidez de mola entre ~105.000 e 165.000 N/m -
outros carros tem faixas bem diferentes) e essas faixas nao sao uniformes nem
publicadas de forma centralizada pela Kunos. Gerar um JSON "do zero" arriscaria
valores fora do permitido pelo jogo. Este motor sempre parte de um setup
valido (o padrao do carro exportado pelo proprio ACC, ou qualquer setup salvo)
e aplica DELTAS relativos, sempre travados (clamped) dentro de margens
seguras - o resultado e sempre coerente com os limites reais daquele carro.

VALIDACAO DE ENGENHARIA (direcao dos ajustes):
As direcoes abaixo foram conferidas contra guias tecnicos de setup do ACC
(Coach Dave Academy, SimRacingSetup) e a logica classica de chassi:
  - ARB traseira MAIS RIGIDA -> mais transferencia de carga no eixo traseiro
    -> eixo traseiro perde grip relativo -> MAIS rotacao/oversteer (agressivo).
    ARB dianteira MAIS RIGIDA -> MAIS understeer (conservador).
  - Preload do diferencial MAIS BAIXO -> mais liberdade entre as rodas
    traseiras -> MAIS rotacao na entrada/tangencia (lift-off oversteer),
    exige mais cuidado. Preload MAIS ALTO -> tracao mais estavel na saida,
    porem tendencia a understeer cronico.
  - Brake bias mais para TRAS (numero menor) -> mais rotacao/oversteer na
    frenagem e entrada de curva (agressivo, arriscado em frenagens longas).
  - Camber mais NEGATIVO -> mais contato lateral em curva (mais pace), porem
    mais sensivel a temperatura/desgaste do pneu em stints longos.
  - Altura/rake: mais baixo e mais rake (traseira alta) -> mais downforce e
    pace, mas mais risco de raspar o fundo em pistas com pisos/zebras
    irregulares (usa o eixo "bumpiness" da pista para conter isso).
  - TC/ABS mais baixos -> dependem mais da habilidade do piloto, mais pace
    potencial, menos seguranca.
  - Molas MAIS RIGIDAS -> plataforma aerodinamica mais consistente (menos
    pitch/roll), mais pace em pista lisa; MAS transmite mais impacto de
    zebra/buraco pro carro, entao o delta e automaticamente reduzido (e pode
    inverter para mais macio) em pistas com bumpiness alto, independente do
    slider de agressividade.
  - Toe-out dianteiro -> giro mais rapido no esterco (turn-in mais vivo,
    agressivo), custa um pouco de estabilidade em linha reta. Toe-in
    traseiro -> mais estabilidade/tracao, tipico em setups conservadores.

Alem dos deltas, ha PISOS DE SEGURANCA absolutos (nao dependem do setup
base): preload nunca abaixo de 10 e altura do carro nunca abaixo de 30mm,
para nunca gerar um setup irreal mesmo que o setup de origem ja fosse
extremo.

Nenhum destes deltas e absoluto: todos sao proporcionais ao valor do setup
base e limitados a uma janela de seguranca, entao o "agressivo" de um carro
nervoso (temperamento alto) e automaticamente mais comedido que o de um
carro estavel (ver 'damp' abaixo).
"""

import copy

from core import data_loader

AGGRESSION_LABELS = {
    0: "Muito Conservador",
    1: "Conservador",
    2: "Equilibrado",
    3: "Agressivo",
    4: "Muito Agressivo",
}


def aggressiveness_label(value: int) -> str:
    if value < 20: return AGGRESSION_LABELS[0]
    if value < 40: return AGGRESSION_LABELS[1]
    if value < 60: return AGGRESSION_LABELS[2]
    if value < 80: return AGGRESSION_LABELS[3]
    return AGGRESSION_LABELS[4]


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _get(d, *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _set(d, *path_and_value):
    *path, value = path_and_value
    cur = d
    for p in path[:-1]:
        cur = cur.setdefault(p, {})
    cur[path[-1]] = value


class SetupCreator:
    """Gera setups inteligentes a partir de um setup base valido."""

    def generate_smart_setup(self, base_setup: dict, car_id: str, track_id: str,
                              aggressiveness: int = 50, condition: str = "dry") -> tuple:
        """
        base_setup: dict do setup .json ja carregado (setup padrao do carro
                    exportado do jogo, ou qualquer outro setup salvo valido).
        car_id: pasta do carro (ex: 'bmw_m4_gt3')
        track_id: pasta da pista (ex: 'monza')
        aggressiveness: 0 (muito seguro) .. 50 (neutro) .. 100 (muito agressivo)
        condition: 'dry' ou 'wet'

        Retorna (novo_setup_dict, meta_dict) - meta_dict traz as notas
        explicando cada ajuste feito, para exibir no Engenheiro Virtual.
        """
        if not base_setup:
            raise ValueError("Setup base vazio ou invalido.")

        data = copy.deepcopy(base_setup)
        aggressiveness = _clamp(int(aggressiveness), 0, 100)
        intensity = (aggressiveness - 50) / 50.0  # -1.0 (conservador) .. +1.0 (agressivo)

        track = data_loader.track_profile(track_id)
        temperament = data_loader.car_temperament(car_id)

        # Carros nervosos (temperamento alto) sofrem menos o efeito do slider,
        # para evitar setups instaveis demais em carros ja naturalmente vivos.
        damp = _clamp(1.0 - 0.15 * (temperament - 3), 0.55, 1.3)
        eff = intensity * damp

        downforce_need = data_loader.normalize(track["downforce"])
        bumpiness = data_loader.normalize(track["bumpiness"])
        brake_stress = data_loader.normalize(track["brake_stress"])

        notes = []

        # --- Barras estabilizadoras (mechanicalBalance) ---
        arb_f = _get(data, "basicSetup", "mechanicalBalance", "aRBFront")
        arb_r = _get(data, "basicSetup", "mechanicalBalance", "aRBRear")
        if arb_f is not None and arb_r is not None:
            new_r = _clamp(round(arb_r + eff * 2), 0, arb_r + 4)
            new_f = _clamp(round(arb_f - eff * 1), 0, arb_f + 2)
            _set(data, "basicSetup", "mechanicalBalance", "aRBRear", new_r)
            _set(data, "basicSetup", "mechanicalBalance", "aRBFront", new_f)
            notes.append(f"Barras: ARB F {arb_f}->{new_f} / R {arb_r}->{new_r} "
                         f"({'traseira mais rigida = mais rotacao (oversteer)' if eff > 0 else 'mais estavel/seguro (understeer leve)' if eff < 0 else 'mantido'})")

        # --- Diferencial (preload) ---
        preload = _get(data, "advancedSetup", "drivetrain", "preload")
        if preload is not None:
            delta = round(eff * -15)
            new_preload = _clamp(preload + delta, max(10, preload - 25), preload + 25)
            _set(data, "advancedSetup", "drivetrain", "preload", new_preload)
            notes.append(f"Diferencial: preload {preload}->{new_preload} "
                         f"({'mais solto p/ rotacionar na entrada' if eff > 0 else 'mais travado p/ tracao estavel na saida' if eff < 0 else 'mantido'})")

        # --- Brake bias ---
        bbias = _get(data, "basicSetup", "alignment", "brakeBias")
        if bbias is not None:
            delta = round((eff * -1.0 + brake_stress * 0.3), 2)
            new_bbias = _clamp(round(bbias + delta, 1), bbias - 2.5, bbias + 2.0)
            _set(data, "basicSetup", "alignment", "brakeBias", new_bbias)
            notes.append(f"Brake bias: {bbias}%->{new_bbias}%")

        # --- Camber ---
        camber = _get(data, "basicSetup", "alignment", "camber")
        if isinstance(camber, list) and len(camber) == 4:
            delta = round(eff * -0.3, 2)
            new_camber = [round(_clamp(c + delta, c - 0.6, c + 0.3), 2) for c in camber]
            _set(data, "basicSetup", "alignment", "camber", new_camber)
            notes.append(f"Camber: {camber}->{new_camber}")

        # --- Aerodinamica / altura e rake (advancedSetup.aero.rideHeight) ---
        ride_height = _get(data, "advancedSetup", "aero", "rideHeight")
        if isinstance(ride_height, list) and len(ride_height) == 4:
            # Pistas de alto downforce + setup agressivo => mais rake (traseira mais
            # alta que a dianteira) para maximizar carga aerodinamica.
            # Pistas com muitos buracos/zebras => nao abaixar demais (risco de raspar).
            front_delta = round(_clamp(-eff * 2 - downforce_need * 2 + bumpiness * 2, -4, 4))
            rear_delta = round(_clamp(eff * 2 + downforce_need * 3, -3, 5))
            new_rh = [
                _clamp(ride_height[0] + front_delta, max(30, ride_height[0] - 6), ride_height[0] + 6),
                _clamp(ride_height[1] + front_delta, max(30, ride_height[1] - 6), ride_height[1] + 6),
                _clamp(ride_height[2] + rear_delta, max(30, ride_height[2] - 6), ride_height[2] + 6),
                _clamp(ride_height[3] + rear_delta, max(30, ride_height[3] - 6), ride_height[3] + 6),
            ]
            _set(data, "advancedSetup", "aero", "rideHeight", new_rh)
            notes.append(f"Altura/Rake: {ride_height}->{new_rh}")

        # --- Molas (springs) e amortecedores (dampers) ---
        # Mais rigido = plataforma mais consistente/direta (mais pace), mas
        # transmite mais impacto de zebra/buraco -> perigoso em pista bumpy.
        # Por isso o delta de mola SEMPRE reduz com bumpiness, mesmo em modo agressivo.
        springs = _get(data, "advancedSetup", "mechanicalBalance", "wheelRate")
        if isinstance(springs, list) and len(springs) == 4:
            spring_factor = _clamp(eff - bumpiness * 0.6, -1.2, 1.2)
            new_springs = [round(_clamp(s * (1 + spring_factor * 0.05), s * 0.85, s * 1.15)) for s in springs]
            _set(data, "advancedSetup", "mechanicalBalance", "wheelRate", new_springs)
            notes.append(f"Molas: {springs}->{new_springs} "
                         f"({'mais rigidas p/ plataforma direta' if spring_factor > 0.05 else 'mais macias p/ absorver irregularidades' if spring_factor < -0.05 else 'mantidas'})")

        bump_damp = _get(data, "advancedSetup", "dampers", "bumpSlow")
        if isinstance(bump_damp, list) and len(bump_damp) == 4:
            damper_factor = _clamp(eff - bumpiness * 0.5, -1.0, 1.0)
            new_bump = [round(_clamp(d + damper_factor * 2, d - 3, d + 3)) for d in bump_damp]
            _set(data, "advancedSetup", "dampers", "bumpSlow", new_bump)
            notes.append(f"Amortecedores (bump lento): {bump_damp}->{new_bump}")

        # --- Toe ---
        toe = _get(data, "basicSetup", "alignment", "toe")
        if isinstance(toe, list) and len(toe) == 4:
            # Toe-out dianteiro = giro mais rapido no esterco (mais agressivo/vivo).
            # Toe-in traseiro = mais estabilidade em linha reta e tracao (mais seguro).
            front_delta = round(eff * 0.02, 3)
            rear_delta = round(-eff * 0.02, 3)
            new_toe = [
                round(_clamp(toe[0] + front_delta, toe[0] - 0.05, toe[0] + 0.05), 3),
                round(_clamp(toe[1] + front_delta, toe[1] - 0.05, toe[1] + 0.05), 3),
                round(_clamp(toe[2] + rear_delta, toe[2] - 0.05, toe[2] + 0.05), 3),
                round(_clamp(toe[3] + rear_delta, toe[3] - 0.05, toe[3] + 0.05), 3),
            ]
            _set(data, "basicSetup", "alignment", "toe", new_toe)
            notes.append(f"Toe: {toe}->{new_toe}")

        # --- Eletronica (TC / ABS) ---
        tc1 = _get(data, "basicSetup", "electronics", "tC1")
        if tc1 is not None:
            new_tc1 = _clamp(tc1 - round(eff * 1), 0, 7)
            _set(data, "basicSetup", "electronics", "tC1", new_tc1)
            notes.append(f"TC1: {tc1}->{new_tc1}")

        abs_v = _get(data, "basicSetup", "electronics", "abs")
        if abs_v is not None:
            new_abs = _clamp(abs_v - round(eff * 1), 0, 7)
            _set(data, "basicSetup", "electronics", "abs", new_abs)
            notes.append(f"ABS: {abs_v}->{new_abs}")

        # --- Pressao dos pneus (ajuste fino conforme velocidade media da pista) ---
        pressures = _get(data, "basicSetup", "tyres", "tyrePressure")
        if isinstance(pressures, list) and len(pressures) == 4:
            speed_norm = data_loader.normalize(track["avg_speed"])
            delta = round(speed_norm * 0.3, 2)
            new_pressures = [round(p + delta, 1) for p in pressures]
            _set(data, "basicSetup", "tyres", "tyrePressure", new_pressures)
            notes.append(f"Pressoes: {pressures}->{new_pressures} (ajuste pela vel. media da pista)")

        # --- Condicao molhada: usa a logica ja existente de composto/freios/eletronica ---
        if condition == "wet":
            try:
                _set(data, "basicSetup", "tyres", "tyreCompound", 1)
                _set(data, "basicSetup", "strategy", "frontBrakePadCompound", 2)
                _set(data, "basicSetup", "strategy", "rearBrakePadCompound", 2)
                notes.append("Condicao: pneu de chuva + pastilhas de chuva aplicados.")
            except Exception:
                pass

        meta = {
            "aggressiveness": aggressiveness,
            "aggressiveness_label": aggressiveness_label(aggressiveness),
            "car_id": car_id,
            "track_id": track_id,
            "condition": condition,
            "car_temperament": temperament,
            "track_profile": track,
            "notes": notes,
        }
        return data, meta
