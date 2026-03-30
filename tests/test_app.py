import pytest,sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.ui.app import TYPE_EXPLANATIONS


def test_type_explanations():
    assert TYPE_EXPLANATIONS["Complaint"] == "Initial violation report"
    assert TYPE_EXPLANATIONS["Systematic Code Enforcement Program"] == "Routine periodic inspection (SCEP)"
    assert TYPE_EXPLANATIONS["Case Management"] == "Active inspector monitoring"
    assert TYPE_EXPLANATIONS["Rent Escrow Account Program"] == "REAP: Rent diverted to escrow"
    assert TYPE_EXPLANATIONS["Hearing"] == "Formal administrative review"
    assert TYPE_EXPLANATIONS["Property Management Training Program"] == "PMTP: Owner training program"
    assert TYPE_EXPLANATIONS["Legal"] == "Referred to City Attorney"
    assert TYPE_EXPLANATIONS["Emergency"] == "Critical health/safety hazard"
    assert TYPE_EXPLANATIONS["Out Reach Case"] == "Tenant advocacy engagement"


def test_type_explanations_missing():
    assert TYPE_EXPLANATIONS.get("Unknown", "Not found") == "Not found"