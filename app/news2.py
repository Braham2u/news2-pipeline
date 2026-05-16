"""NEWS2 scoring engine.

Implements the National Early Warning Score 2 (NEWS2) as defined by the
Royal College of Physicians (2017). Each physiological parameter is mapped
to a sub-score of 0-3; the aggregate score determines the clinical risk
band and the recommended monitoring/escalation response.

Reference: Royal College of Physicians. National Early Warning Score
(NEWS) 2: Standardising the assessment of acute-illness severity in the
NHS. London: RCP, 2017.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Consciousness(str, Enum):
    """ACVPU scale. 'A' (Alert) scores 0; any of C/V/P/U scores 3."""

    ALERT = "A"
    CONFUSION = "C"
    VOICE = "V"
    PAIN = "P"
    UNRESPONSIVE = "U"


class RiskBand(str, Enum):
    LOW = "low"
    LOW_MEDIUM = "low-medium"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Observation:
    """A single set of patient vital-sign observations."""

    respiratory_rate: int
    spo2: int
    on_supplemental_oxygen: bool
    systolic_bp: int
    pulse: int
    consciousness: Consciousness
    temperature: float


@dataclass(frozen=True)
class News2Result:
    total_score: int
    parameter_scores: dict[str, int]
    has_red_score: bool
    risk_band: RiskBand
    clinical_response: str


def score_respiratory_rate(value: int) -> int:
    if value <= 8:
        return 3
    if value <= 11:
        return 1
    if value <= 20:
        return 0
    if value <= 24:
        return 2
    return 3


def score_spo2(value: int) -> int:
    if value <= 91:
        return 3
    if value <= 93:
        return 2
    if value <= 95:
        return 1
    return 0


def score_supplemental_oxygen(on_oxygen: bool) -> int:
    return 2 if on_oxygen else 0


def score_systolic_bp(value: int) -> int:
    if value <= 90:
        return 3
    if value <= 100:
        return 2
    if value <= 110:
        return 1
    if value <= 219:
        return 0
    return 3


def score_pulse(value: int) -> int:
    if value <= 40:
        return 3
    if value <= 50:
        return 1
    if value <= 90:
        return 0
    if value <= 110:
        return 1
    if value <= 130:
        return 2
    return 3


def score_consciousness(value: Consciousness) -> int:
    return 0 if value == Consciousness.ALERT else 3


def score_temperature(value: float) -> int:
    if value <= 35.0:
        return 3
    if value <= 36.0:
        return 1
    if value <= 38.0:
        return 0
    if value <= 39.0:
        return 1
    return 2


def _risk_band(total: int, has_red_score: bool) -> RiskBand:
    if total >= 7:
        return RiskBand.HIGH
    if total >= 5:
        return RiskBand.MEDIUM
    if has_red_score:
        return RiskBand.LOW_MEDIUM
    return RiskBand.LOW


_RESPONSE = {
    RiskBand.LOW: "Routine monitoring; minimum 12-hourly observations.",
    RiskBand.LOW_MEDIUM: (
        "Urgent review by a ward-based clinician; minimum 1-hourly "
        "observations."
    ),
    RiskBand.MEDIUM: (
        "Urgent review by a clinician with competencies in acute illness; "
        "minimum 1-hourly observations."
    ),
    RiskBand.HIGH: (
        "Emergency assessment by a critical-care-competent team; "
        "continuous monitoring of vital signs."
    ),
}


def calculate_news2(obs: Observation) -> News2Result:
    """Compute the aggregate NEWS2 score and clinical risk band."""

    parameter_scores = {
        "respiratory_rate": score_respiratory_rate(obs.respiratory_rate),
        "spo2": score_spo2(obs.spo2),
        "supplemental_oxygen": score_supplemental_oxygen(
            obs.on_supplemental_oxygen
        ),
        "systolic_bp": score_systolic_bp(obs.systolic_bp),
        "pulse": score_pulse(obs.pulse),
        "consciousness": score_consciousness(obs.consciousness),
        "temperature": score_temperature(obs.temperature),
    }

    total = sum(parameter_scores.values())
    has_red_score = any(score == 3 for score in parameter_scores.values())
    band = _risk_band(total, has_red_score)

    return News2Result(
        total_score=total,
        parameter_scores=parameter_scores,
        has_red_score=has_red_score,
        risk_band=band,
        clinical_response=_RESPONSE[band],
    )
