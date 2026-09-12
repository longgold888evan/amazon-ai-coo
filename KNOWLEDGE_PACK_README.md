# Amazon AI COO — Knowledge Pack v0.1

Generated: 2026-09-12

This pack is designed to be copied into the root of `amazon-ai-coo` without overwriting application code. It contains the first curated knowledge layer assembled from:

1. Current Amazon official developer / seller / ads sources.
2. Amazon Brand Analytics and Customer Feedback concepts available from official sources.
3. Keepa official API/MCP documentation metadata.
4. Structured, policy-filtered learnings from the SCYS `Amazon 入门 | 实战手册 | 2022年11月航海` and selected operator case studies.

The repository should store **normalized knowledge and source metadata**, not a dump of third-party copyrighted material. Long-form source documents remain external and are referenced through stable source records.

## Copy into repo

From the repo root:

```bash
cp -R /path/to/amazon-ai-coo-knowledge-pack/knowledge ./
cp -R /path/to/amazon-ai-coo-knowledge-pack/policies ./
cp -R /path/to/amazon-ai-coo-knowledge-pack/schemas ./
cp -R /path/to/amazon-ai-coo-knowledge-pack/docs ./
cp -R /path/to/amazon-ai-coo-knowledge-pack/scripts ./
```

Then run:

```bash
python scripts/validate_knowledge.py
```

## Core design

Every knowledge item must answer five questions:

- **Where did it come from?**
- **How authoritative is the source?**
- **How fresh is it?**
- **Is it policy-safe?**
- **Can an agent execute it, or is it only a hypothesis?**

Current Amazon policy and official documentation always outrank operator playbooks.
