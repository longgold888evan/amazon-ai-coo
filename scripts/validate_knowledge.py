#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "knowledge/_meta/source_registry.yaml",
    ROOT / "knowledge/_meta/status_taxonomy.yaml",
    ROOT / "policies/knowledge_precedence.yaml",
    ROOT / "policies/blocked_legacy_tactics.yaml",
    ROOT / "schemas/knowledge_item.schema.json",
    ROOT / "schemas/decision_rule.schema.json",
]

missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing required knowledge files: " + ", ".join(missing))

for schema in [ROOT / "schemas/knowledge_item.schema.json", ROOT / "schemas/decision_rule.schema.json"]:
    json.loads(schema.read_text(encoding="utf-8"))

print("Knowledge pack structural validation: OK")
