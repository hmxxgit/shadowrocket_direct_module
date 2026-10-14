"""Domestic product rules use the same typed policy source as all other rules."""
from policy import reviewed_imports, suffixes


def domestic_direct_rules():
    rules, events = reviewed_imports('domestic')
    return [r.line() for r in rules if r.policy == 'DIRECT'], events
