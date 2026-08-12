# Architecture

Status: initial map; this document will be refined after dependency and route inspection.

The repository currently uses four broad layers:

- `src/domain`: linguistic entities, value objects, rule data, services, and repository contracts.
- `src/application`: text/URL/batch/export services and ingestion use cases.
- `src/infrastructure`: configuration, SQLAlchemy models/connections, and repository implementations.
- `src/web`: the synchronous FastAPI transport layer.

The linguistic core is lexeme-first: `Lexeme` owns `WordForm`, `Meaning`, and `Context`; `SwahiliTerm` remains a legacy compatibility object. The morphology implementation is heuristic and must expose that uncertainty rather than being described as a complete analyzer.

