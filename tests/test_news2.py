"""Unit tests for the NEWS2 scoring engine.

Each parameter is tested at its clinical band boundaries (the values
either side of a threshold) because off-by-one errors at a boundary are
the most clinically dangerous failure mode for an early-warning score.
"""

import pytest

from app.news2 import (
    Consciousness,
    Observation,
    RiskBand,
    calculate_news2,
    score_consciousness,
    score_pulse,
    score_respiratory_rate,
    score_spo2,
    score_supplemental_oxygen,
    score_systolic_bp,
    score_temperature,
)


@pytest.mark.parametrize(
    "value,expected",
    [(8, 3), (9, 1), (11, 1), (12, 0), (20, 0), (21, 2), (24, 2), (25, 3)],
)
def test_respiratory_rate_boundaries(value: int, expected: int) -> None:
    assert score_respiratory_rate(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [(91, 3), (92, 2), (93, 2), (94, 1), (95, 1), (96, 0), (100, 0)],
)
def test_spo2_boundaries(value: int, expected: int) -> None:
    assert score_spo2(value) == expected


@pytest.mark.parametrize("on_oxygen,expected", [(True, 2), (False, 0)])
def test_supplemental_oxygen(on_oxygen: bool, expected: int) -> None:
    assert score_supplemental_oxygen(on_oxygen) == expected


@pytest.mark.parametrize(
    "value,expected",
    [(90, 3), (91, 2), (100, 2), (101, 1), (110, 1), (111, 0), (219, 0), (220, 3)],
)
def test_systolic_bp_boundaries(value: int, expected: int) -> None:
    assert score_systolic_bp(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [(40, 3), (41, 1), (50, 1), (51, 0), (90, 0), (91, 1), (110, 1),
     (111, 2), (130, 2), (131, 3)],
)
def test_pulse_boundaries(value: int, expected: int) -> None:
    assert score_pulse(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (Consciousness.ALERT, 0),
        (Consciousness.CONFUSION, 3),
        (Consciousness.VOICE, 3),
        (Consciousness.PAIN, 3),
        (Consciousness.UNRESPONSIVE, 3),
    ],
)
def test_consciousness(value: Consciousness, expected: int) -> None:
    assert score_consciousness(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [(35.0, 3), (35.1, 1), (36.0, 1), (36.1, 0), (38.0, 0),
     (38.1, 1), (39.0, 1), (39.1, 2)],
)
def test_temperature_boundaries(value: float, expected: int) -> None:
    assert score_temperature(value) == expected


def _healthy() -> Observation:
    return Observation(
        respiratory_rate=16,
        spo2=98,
        on_supplemental_oxygen=False,
        systolic_bp=120,
        pulse=70,
        consciousness=Consciousness.ALERT,
        temperature=36.8,
    )


def test_healthy_patient_scores_zero_low_risk() -> None:
    result = calculate_news2(_healthy())
    assert result.total_score == 0
    assert result.has_red_score is False
    assert result.risk_band == RiskBand.LOW


def test_single_red_score_triggers_low_medium_band() -> None:
    obs = Observation(
        respiratory_rate=16,
        spo2=98,
        on_supplemental_oxygen=False,
        systolic_bp=120,
        pulse=70,
        consciousness=Consciousness.ALERT,
        temperature=34.5,  # <=35.0 -> single parameter scores 3
    )
    result = calculate_news2(obs)
    assert result.total_score == 3
    assert result.has_red_score is True
    assert result.risk_band == RiskBand.LOW_MEDIUM


def test_medium_risk_band() -> None:
    obs = Observation(
        respiratory_rate=22,  # 2
        spo2=93,  # 2
        on_supplemental_oxygen=False,
        systolic_bp=105,  # 1
        pulse=70,
        consciousness=Consciousness.ALERT,
        temperature=36.8,
    )
    result = calculate_news2(obs)
    assert result.total_score == 5
    assert result.risk_band == RiskBand.MEDIUM


def test_high_risk_band_deteriorating_patient() -> None:
    obs = Observation(
        respiratory_rate=28,  # 3
        spo2=90,  # 3
        on_supplemental_oxygen=True,  # 2
        systolic_bp=85,  # 3
        pulse=135,  # 3
        consciousness=Consciousness.VOICE,  # 3
        temperature=39.5,  # 2
    )
    result = calculate_news2(obs)
    assert result.total_score == 19
    assert result.risk_band == RiskBand.HIGH
    assert "critical-care" in result.clinical_response
