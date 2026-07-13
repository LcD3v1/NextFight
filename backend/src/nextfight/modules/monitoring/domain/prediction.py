"""Deterministic MVP fight-start prediction policy."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """Transparent prediction output ready for persistence."""

    predicted_start_at: datetime
    earliest_start_at: datetime
    latest_start_at: datetime
    confidence_score: Decimal
    factors: dict[str, int | bool]
    model_version: str = "rules-v1"


def predict_start(
    *,
    reference_at: datetime,
    fights_before: int,
    event_paused: bool,
    provider_delayed: bool,
) -> PredictionResult:
    """Estimate a start window from remaining bouts and operational uncertainty."""
    bout_minutes = 18
    interval_minutes = 8
    expected_minutes = fights_before * (bout_minutes + interval_minutes)
    uncertainty_minutes = 5 + fights_before * 4
    confidence = Decimal("0.92") - Decimal(fights_before) * Decimal("0.08")
    if event_paused:
        confidence -= Decimal("0.20")
        uncertainty_minutes += 15
    if provider_delayed:
        confidence -= Decimal("0.15")
        uncertainty_minutes += 10
    confidence = max(Decimal("0.20"), min(Decimal("0.95"), confidence))
    predicted = reference_at + timedelta(minutes=expected_minutes)
    return PredictionResult(
        predicted_start_at=predicted,
        earliest_start_at=predicted - timedelta(minutes=uncertainty_minutes),
        latest_start_at=predicted + timedelta(minutes=uncertainty_minutes),
        confidence_score=confidence,
        factors={
            "fights_before": fights_before,
            "bout_minutes": bout_minutes,
            "interval_minutes": interval_minutes,
            "event_paused": event_paused,
            "provider_delayed": provider_delayed,
        },
    )
