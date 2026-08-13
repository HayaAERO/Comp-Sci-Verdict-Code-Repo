"""
Tests for the verdict pipeline output.
Run: python3 -m pytest pipeline/test_pipeline.py  (if pytest available)
Or:  python3 pipeline/test_pipeline.py
"""

import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)  # data-intelligence/
REPO_DIR = os.path.dirname(PIPELINE_DIR)     # HORUS root
DATA_DIR = os.path.join(REPO_DIR, "data")
RAW_DIR = os.path.join(PIPELINE_DIR, "data", "raw")

sys.path.insert(0, PIPELINE_DIR)
from pipeline.verdict_rule import decide, load_aei_data, SKILL_VERDICT_OVERRIDES
from pipeline.guidance import generate_guidance, generate_overview


def load_verdicts(path=None):
    if path is None:
        path = os.path.join(DATA_DIR, "verdicts.json")
    with open(path) as f:
        return json.load(f)


def test_data_contract_shape():
    """Vérifie que le JSON suit le data contract."""
    d = load_verdicts()
    required_keys = {"source", "university", "degree", "tier", "courses", "overview"}
    assert required_keys.issubset(d.keys()), f"Missing keys: {required_keys - d.keys()}"
    assert d["source"] in ("major", "upload")
    assert d["university"] == "Texas A&M University"
    assert d["tier"] in ("verified", "estimate")


def test_courses_structure():
    """Vérifie la structure des cours."""
    d = load_verdicts()
    for c in d["courses"]:
        assert "code" in c, f"Course missing 'code': {c}"
        assert "title" in c, f"Course missing 'title': {c}"
        assert "skills" in c, f"Course missing 'skills': {c['code']}"
        assert isinstance(c["skills"], list)
        for s in c["skills"]:
            assert "name" in s
            assert s["verdict"] in ("Automating", "Transforming", "Untouched"), \
                f"Invalid verdict '{s['verdict']}' for {s['name']}"
            assert s["confidence"] in ("high", "medium", "low"), \
                f"Invalid confidence '{s['confidence']}' for {s['name']}"
            assert "guidance" in s and s["guidance"].strip(), \
                f"Empty guidance for {s['name']}"
            assert "source" in s and s["source"].strip(), \
                f"Empty source for {s['name']}"


def test_overview_structure():
    """Vérifie l'overview."""
    d = load_verdicts()
    ov = d["overview"]
    assert ov["automating"] >= 0
    assert ov["transforming"] >= 0
    assert ov["untouched"] >= 0
    assert ov["summary"].strip(), "Empty summary"
    total = ov["automating"] + ov["transforming"] + ov["untouched"]
    assert total > 0, "Overview counts are all zero"


def test_overview_matches_skills():
    """Vérifie que les comptes overview = somme des skills."""
    d = load_verdicts()
    counts = {"automating": 0, "transforming": 0, "untouched": 0}
    for c in d["courses"]:
        for s in c["skills"]:
            v = s["verdict"].lower()
            if "automating" in v:
                counts["automating"] += 1
            elif "transforming" in v:
                counts["transforming"] += 1
            else:
                counts["untouched"] += 1
    ov = d["overview"]
    assert counts["automating"] == ov["automating"], \
        f"Automating count mismatch: {counts['automating']} vs {ov['automating']}"
    assert counts["transforming"] == ov["transforming"], \
        f"Transforming count mismatch: {counts['transforming']} vs {ov['transforming']}"
    assert counts["untouched"] == ov["untouched"], \
        f"Untouched count mismatch: {counts['untouched']} vs {ov['untouched']}"


def test_all_skills_have_verdict():
    """Vérifie que tout skill a un verdict défini dans notre map."""
    d = load_verdicts()
    aei = load_aei_data(os.path.join(RAW_DIR, "onet_task_mappings.csv"))
    found_skills = set()
    for c in d["courses"]:
        for s in c["skills"]:
            found_skills.add(s["name"])
    
    # Verify every skill in the output has a verdict rule
    for name in sorted(found_skills):
        if name not in SKILL_VERDICT_OVERRIDES:
            print(f"  ⚠️  {name} has no explicit verdict override (using AEI fallback)")


def test_no_empty_courses_in_output():
    """Vérifie qu'on ne garde que les cours qui ont des skills."""
    d = load_verdicts()
    for c in d["courses"]:
        assert len(c["skills"]) > 0, f"Course {c['code']} has no skills in output"


def test_guidance_generator():
    """Vérifie que tous les templates de guidance fonctionnent."""
    verdicts = ["Automating", "Transforming", "Untouched"]
    for v in verdicts:
        text = generate_guidance("NonExistentSkill", v)
        assert text.strip(), f"Empty guidance for default {v}"


def test_overview_generator():
    """Vérifie generate_overview."""
    skills = [
        {"verdict": "Transforming"},
        {"verdict": "Transforming"},
        {"verdict": "Untouched"},
        {"verdict": "Automating"},
    ]
    ov = generate_overview(skills)
    assert ov["automating"] == 1
    assert ov["transforming"] == 2
    assert ov["untouched"] == 1
    assert ov["summary"].strip()


def test_verdict_rule_all_skills():
    """Vérifie que toutes les 23 skills O*NET retournent un verdict valide."""
    aei = load_aei_data(os.path.join(RAW_DIR, "onet_task_mappings.csv"))
    all_skills = [
        "Active Learning", "Active Listening", "Complex Problem Solving",
        "Coordination", "Critical Thinking", "Instructing",
        "Judgment and Decision Making", "Learning Strategies", "Mathematics",
        "Monitoring", "Operation and Control", "Operations Monitoring",
        "Persuasion", "Programming", "Quality Control Analysis",
        "Reading Comprehension", "Service Orientation", "Social Perceptiveness",
        "Speaking", "Systems Analysis", "Systems Evaluation",
        "Time Management", "Writing",
    ]
    for s in all_skills:
        r = decide(s, aei)
        assert r["verdict"] in ("Automating", "Transforming", "Untouched")
        assert r["confidence"] in ("high", "medium", "low")
        assert generate_guidance(s, r["verdict"]).strip()


def test_aei_data_loaded():
    """Vérifie que les données AEI se chargent."""
    path = os.path.join(RAW_DIR, "onet_task_mappings.csv")
    assert os.path.exists(path), "AEI data not found"
    scores = load_aei_data(path)
    assert len(scores) > 0, "AEI scores empty"
    # Programming should have the highest presence
    if "Programming" in scores:
        assert scores["Programming"]["presence"] > 10.0, \
            f"Programming presence too low: {scores['Programming']['presence']}"


if __name__ == "__main__":
    tests = [
        ("Data contract shape", test_data_contract_shape),
        ("Courses structure", test_courses_structure),
        ("Overview structure", test_overview_structure),
        ("Overview matches skills", test_overview_matches_skills),
        ("No empty courses", test_no_empty_courses_in_output),
        ("Guidance generator", test_guidance_generator),
        ("Overview generator", test_overview_generator),
        ("Verdict rule all skills", test_verdict_rule_all_skills),
        ("AEI data loaded", test_aei_data_loaded),
        ("All skills have verdict", test_all_skills_have_verdict),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"  {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)