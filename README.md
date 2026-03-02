# ragapp-max-findings (Fixture)

This repository is a **static analysis fixture** designed to trigger findings in:
- Agentic orchestration
- RAG / vector stores
- Dataset connectors
- System prompts / metaprompts risks
- Prompt injection + unsafe output handling patterns
- AI supply chain exposure (deps + CI secrets)

## Safety
- Not intended for deployment
- Network calls are stubbed
- "Bad" patterns are included to maximize detection signals

## Vibe coding marker
This fixture includes "vibe coding" artifacts (TODOs, minimal review notes, rapid config merges).