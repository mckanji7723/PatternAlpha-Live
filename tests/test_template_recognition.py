
import numpy as np
from core.template_recognition import base_templates, classify_shape

def test_templates_exist():
    t = base_templates()
    assert "Head & Shoulders" in t
    assert len(t["Head & Shoulders"]) == 60

def test_knn_recognizes_reference_shape():
    t = base_templates()
    out = classify_shape(t["Double Top"])
    assert out["predicted_pattern"] == "Double Top"
    assert out["knn_vote"] >= 0.6
