import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
sys.path.insert(0, os.path.join(REPO_ROOT, "skills", "spec-orchestrator", "scripts"))

from compile_yang import build_attributes
from reconcile_backlog import sanitize_mermaid_diagrams


class MockNode:
    def __init__(self, keyword, arg, children=None, substmts=None):
        self.keyword = keyword
        self.arg = arg
        self.i_children = children or []
        self.substmts = substmts or []
        self.i_is_validated = True

    def search_one(self, keyword):
        for c in (self.i_children or self.substmts):
            if c.keyword == keyword:
                return c
        return None


def test_build_attributes_filters_choice_and_case():
    type_stmt = MockNode("type", "string")
    lat_leaf = MockNode("leaf", "latitude", children=[type_stmt])
    long_leaf = MockNode("leaf", "longitude", children=[type_stmt])

    gps_case = MockNode("case", "gps-case", children=[lat_leaf, long_leaf])
    loc_choice = MockNode("choice", "location-choice", children=[gps_case])
    loc_container = MockNode("container", "location", children=[loc_choice])

    attrs = build_attributes([loc_container])

    # Assert choice and case node names are NOT created as scalar attributes
    # and NOT included in child leaf XPath paths.
    attr_keys = [a["key"] for a in attrs]
    assert "location/latitude" in attr_keys
    assert "location/longitude" in attr_keys

    for a in attrs:
        assert "location-choice" not in a["key"]
        assert "gps-case" not in a["key"]

    assert len(attrs) == 2


def test_sanitize_mermaid_diagrams_fixes_line_wrapped_arrows():
    input_md = (
        "# Spec\n\n"
        "```mermaid\n"
        "sequenceDiagram\n"
        "    participant A\n"
        "    participant B\n"
        "    A ->>\n"
        "    B: message\n"
        "    A ->\n"
        "    > B: reply\n"
        "    A --\n"
        "    > B: done\n"
        "```\n"
    )

    sanitized = sanitize_mermaid_diagrams(input_md)

    assert "A ->> B: message" in sanitized
    assert "A ->> B: reply" in sanitized
    assert "A --> B: done" in sanitized
    assert "A ->>\n    B: message" not in sanitized
