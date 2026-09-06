import xml.etree.ElementTree as ET
from pathlib import Path

from core.motec_parser import MotecParser


def _write_ldx(path: Path, xml_text: str) -> None:
    path.write_text(xml_text, encoding="utf-8")


def test_read_session_file_parses_summary_and_metadata(tmp_path):
    xml_text = """
    <Session>
      <String Id="Session" Value="Race" />
      <String Id="Fastest Time" Value="01:45.678" />
      <Number Id="Total Laps" Value="14" />
      <String Id="Track Temperature" Value="27" />
      <String Id="Ambient Temperature" Value="22" />
      <String Id="Vehicle Weight" Value="1300" />
    </Session>
    """
    file_path = tmp_path / "Monza-gt3-Driver-2024.05.18-12.30.00.ldx"
    _write_ldx(file_path, xml_text)

    summary = MotecParser(str(tmp_path)).read_session_file(str(file_path))

    assert summary["total_laps"] == 14
    assert summary["fastest_time"] == "01:45.678"
    assert summary["session_type"] == "Race"
    assert summary["track_temp"] == "27"
    assert summary["ambient_temp"] == "22"
    assert summary["vehicle_weight"] == "1300"


def test_get_best_laps_uses_marker_fallback_and_filename_metadata(tmp_path):
    xml_text = """
    <Root>
      <Marker ClassName="BCN" Time="1000000" />
      <Marker ClassName="BCN" Time="2000000" />
      <Marker ClassName="BCN" Time="3000000" />
      <Marker ClassName="BCN" Time="4300000" />
    </Root>
    """
    file_path = tmp_path / "silverstone-porsche_911_gt3_r-Driver-2024.06.02-18.30.00.ldx"
    _write_ldx(file_path, xml_text)

    laps = MotecParser(str(tmp_path)).get_best_laps()

    assert len(laps) == 1
    lap = laps[0]
    assert lap["track"] == "Silverstone"
    assert lap["car"] == "Porsche 911 Gt3 R" or lap["car"].startswith("Porsche")
    assert lap["driver"] == "Driver"
    assert lap["date"] == "02/06/2024 18:30"
    assert lap["raw_time"] == 1.0
    assert lap["lap_time"].startswith("0:01")


def test_read_session_file_handles_missing_file_and_invalid_xml(tmp_path):
    missing_summary = MotecParser(str(tmp_path)).read_session_file(str(tmp_path / "missing.ldx"))
    assert missing_summary["total_laps"] == 0
    assert missing_summary["fastest_time"] == ""

    invalid_file = tmp_path / "broken.ldx"
    invalid_file.write_text("<Root><Broken>", encoding="utf-8")

    invalid_summary = MotecParser(str(tmp_path)).read_session_file(str(invalid_file))
    assert invalid_summary["total_laps"] == 0
    assert invalid_summary["fastest_time"] == ""
    assert invalid_summary["session_type"] == "Desconhecida"
