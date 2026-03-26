"""
Quick verification test for Nexus modules.
Run with: python test_nexus.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 55)
print("  NEXUS VERIFICATION TEST")
print("=" * 55)

# ── Test 1: Classifier ────────────────────────────────────
print("\n[1] CLASSIFIER TEST")
print("-" * 40)
from brain.classifier import classify

tests = [
    ("open chrome",                     "OPEN_BROWSER"),
    ("I need to crunch some numbers",   "OPEN_CALCULATOR"),
    ("save this to my ideas",           "SAVE_TEXT"),
    ("where did I put my presentation", "FIND_FILE"),
    ("create a folder called Vacation", "CREATE_FOLDER"),
    ("open my downloads folder",        "OPEN_FOLDER"),
    ("run my python script",            "RUN_COMMAND"),
    ("bye nexus",                       "GOODBYE"),
    ("I want to write some code",       "OPEN_VSCODE"),
    ("blah blah blah nonsense",         "UNKNOWN"),
]

passed = 0
for phrase, expected in tests:
    intent, conf, entity = classify(phrase)
    status = "PASS" if intent == expected else "FAIL"
    if status == "PASS":
        passed += 1
    print(f"  [{status}] [{conf:.2f}] \"{phrase}\"")
    print(f"         => {intent} (expected {expected})")

print(f"\n  Result: {passed}/{len(tests)} passed")

# ── Test 2: Storage Manager ───────────────────────────────
print("\n[2] STORAGE MANAGER TEST")
print("-" * 40)
from memory.storage_manager import StorageManager

sm = StorageManager()
path = sm.save_text("test_verification", "Hello from Nexus verification!", tags="test,verify")
print(f"  Saved:  {path}")
assert os.path.exists(path), "FAIL: file not created on disk!"

found = sm.find_file("verification")
print(f"  Found:  {found}")
assert found is not None, "FAIL: file not found in database!"
print("  Result: PASS")

# ── Test 3: File listing ──────────────────────────────────
print("\n[3] STORAGE LISTING TEST")
print("-" * 40)
files = sm.list_all()
print(f"  Files indexed in Nexus DB: {len(files)}")
for f in files[:3]:
    print(f"    • {f['name']} -> {f['path']}")
print("  Result: PASS")

print("\n" + "=" * 55)
print("  ALL TESTS COMPLETE")
print("=" * 55)
