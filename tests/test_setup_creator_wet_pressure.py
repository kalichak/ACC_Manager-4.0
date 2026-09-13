import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.setup_creator import SetupCreator


def test_wet_setup_uses_higher_tyre_pressure_than_dry() -> None:
    base_setup = {
        "basicSetup": {
            "mechanicalBalance": {"aRBFront": 4, "aRBRear": 5},
            "alignment": {"brakeBias": 55.0, "camber": [0.0, 0.0, 0.0, 0.0], "toe": [0.0, 0.0, 0.0, 0.0]},
            "tyres": {"tyrePressure": [25.5, 25.5, 24.7, 24.7]},
            "electronics": {"tC1": 3, "abs": 3},
        },
        "advancedSetup": {
            "drivetrain": {"preload": 18},
            "aero": {"rideHeight": [55, 55, 70, 70]},
            "mechanicalBalance": {"wheelRate": [6000, 6000, 7000, 7000]},
            "dampers": {"bumpSlow": [3, 3, 4, 4]},
        },
    }

    dry_setup, _ = SetupCreator().generate_smart_setup(base_setup, "bmw_m4_gt3", "monza", aggressiveness=50, condition="dry")
    wet_setup, _ = SetupCreator().generate_smart_setup(base_setup, "bmw_m4_gt3", "monza", aggressiveness=50, condition="wet")

    assert dry_setup["basicSetup"]["tyres"]["tyrePressure"] == [25.5, 25.5, 24.7, 24.7]
    assert wet_setup["basicSetup"]["tyres"]["tyrePressure"] > dry_setup["basicSetup"]["tyres"]["tyrePressure"]
    assert wet_setup["basicSetup"]["tyres"]["tyrePressure"] == [25.9, 25.9, 25.1, 25.1]
