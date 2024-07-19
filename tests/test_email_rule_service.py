from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time

from models.email import Email
from services.email_rule_service import EmailRuleProcessor


@pytest.fixture
def mock_email_provider():
    return Mock()

@pytest.fixture
def sample_rules():
    return {
        "rule_sets": [
            {
                "rule_match": "any",
                "rules": [
                    {"field": "subject", "predicate": "contains", "value": "urgent"}
                ],
                "actions": [
                    {"action": "mark_as_read"}
                ]
            },
            {
                "rule_match": "all",
                "rules": [
                    {"field": "sender_email", "predicate": "equals", "value": "boss@example.com"},
                    {"field": "subject", "predicate": "contains", "value": "meeting"}
                ],
                "actions": [
                    {"action": "move_message", "value": "Important"}
                ]
            },
            {
                "rule_match": "all",
                "rules": [
                    {"field": "subject", "predicate": "does_not_contain", "value": "urgent"},
                    {"field": "received_at", "predicate": "greater_than", "value": "20"}
                ],
                "actions": [
                    {"action": "move_message", "value": "Archive"}
                ]
            }
        ]
    }

@pytest.fixture
def sample_emails():
    return [
        Email(
            email_provider_id="123",
            subject="Urgent: Please read",
            body="This is an urgent email.",
            received_at=datetime(2024, 6, 30, 12, 0),
            sender_email="colleague@example.com",
        ),
        Email(
            email_provider_id="124",
            subject="Meeting schedule",
            body="Please check the attached meeting schedule.",
            received_at=datetime(2024, 7, 2, 9, 0),
            sender_email="boss@example.com",
        ),
        Email(
            email_provider_id="125",
            subject="Hello",
            body="Just a friendly hello.",
            received_at=datetime(2024, 7, 5, 15, 0),
            sender_email="friend@example.com",
        ),
        Email(
            email_provider_id="126",
            subject="Hello",
            body="Just a friendly hello.",
            received_at=datetime(2024, 6, 20, 15, 0),
            sender_email="friend@example.com",
        ),
    ]

@freeze_time("2024-07-18")
def test_apply_rules_to_emails(mock_email_provider, sample_rules, sample_emails):

    processor = EmailRuleProcessor(sample_rules, mock_email_provider)
    results = processor.apply_rules_to_emails(sample_emails)

    assert len(results) == 4

    assert results[0]["email"] == "Urgent: Please read"
    assert len(results[0]["actions"]) == 1
    assert results[0]["actions"][0] == {"action": "mark_as_read"}

    assert results[1]["email"] == "Meeting schedule"
    assert len(results[1]["actions"]) == 1
    assert results[1]["actions"][0] == {"action": "move_message", "value": "Important"}

    assert results[2]["email"] == "Hello"
    assert len(results[2]["actions"]) == 0

    assert results[3]["email"] == "Hello"
    assert len(results[3]["actions"]) == 1

def test_apply_actions(mock_email_provider, sample_emails):
    processor = EmailRuleProcessor({}, mock_email_provider)
    actions = [{"action": "mark_as_read"}]
    processor.apply_actions(actions, sample_emails[0])
    mock_email_provider.mark_as_read.assert_called_once_with("123")

    actions = [{"action": "move_message", "value": "Archive"}]
    processor.apply_actions(actions, sample_emails[1])
    mock_email_provider.move_to_label.assert_called_once_with("124", "Archive")
