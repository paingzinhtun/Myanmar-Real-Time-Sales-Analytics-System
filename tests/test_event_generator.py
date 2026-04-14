from __future__ import annotations

from src.producer.event_generator import MyanmarSalesEventGenerator
from src.validation.event_schema import REQUIRED_FIELDS


def test_generator_produces_payload_with_expected_schema() -> None:
    generator = MyanmarSalesEventGenerator(seed=42)
    event = generator.generate_event()

    if "event_id" in event:
        assert REQUIRED_FIELDS.issubset(set(event.keys()))
    else:
        assert "event_timestamp" in event


def test_generator_duplicate_preserves_event_identity() -> None:
    generator = MyanmarSalesEventGenerator(seed=7)
    generator.settings = generator.settings.__class__(
        **{
            **generator.settings.__dict__,
            "producer_duplicate_event_rate": 1.0,
            "producer_invalid_event_rate": 0.0,
        }
    )

    first_event = generator.generate_event()
    second_event = generator.generate_event()

    assert "event_id" in first_event
    assert second_event["event_id"] == first_event["event_id"]
    assert second_event["duplicate_injected"] is True
