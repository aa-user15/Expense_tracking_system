# Capstone Scorecard

This scorecard summarizes the completed capstone work across the implemented phases, using a self-scored rubric with weighted scores from 1–5. Evidence is drawn from the repository structure, tests, documentation, and the completed extension reflection.

## Self-Scored Evaluation Table

| Dimension | Raw score (1–5) | Weighted score | Evidence snippet or link |
| --- | ---: | ---: | --- |
| Core API implementation | 5 | 5.0 | [main.py](../main.py) and [README.md](../README.md) |
| Bug fixing and regression resilience | 5 | 5.0 | [tests/test_transactions.py](../tests/test_transactions.py) and [tests/test_models.py](../tests/test_models.py) |
| Architecture and separation of concerns | 4 | 4.0 | [services/transaction_service.py](../services/transaction_service.py) and [docs/adr-001-service-layer.md](adr-001-service-layer.md) |
| Testing and quality assurance | 5 | 5.0 | [tests/test_transactions.py](../tests/test_transactions.py) with 23 passing tests |
| Documentation and developer experience | 5 | 5.0 | [README.md](../README.md), [docs/adr-001-service-layer.md](adr-001-service-layer.md), and [main.py](../main.py) docstrings |
| Extension: manual vs. agentic comparison | 4 | 4.0 | [docs/manual_vs_agentic_comparison.md](manual_vs_agentic_comparison.md) |

## Justification by Dimension

### Core API implementation
The API includes the expected CRUD behavior for expense transactions with FastAPI routes for create, list, retrieve, and delete operations. The implementation is functional and aligns with the project brief, and the app is documented clearly in the repository.

### Bug fixing and regression resilience
The project demonstrates strong defect handling through duplicate prevention, pagination support, and regression tests that validate those behaviors. The test suite covers happy paths, validation failures, and duplicate scenarios, which indicates the fixes were verified rather than only patched superficially.

### Architecture and separation of concerns
The introduction of a dedicated transaction service layer improves maintainability and keeps business logic separate from the HTTP layer. The ADR documents this decision and reinforces the rationale behind the architecture.

### Testing and quality assurance
The repository includes a substantial pytest suite with both endpoint-level and service-level tests. The latest local verification run reported 23 passed tests, which provides strong evidence that the implementation is working end to end.

### Documentation and developer experience
The project now includes OpenAPI-ready endpoint docstrings, a practical README with setup and usage instructions, and an ADR that explains the architectural decision. These additions make the service easier to understand, run, and extend.

### Extension: manual vs. agentic comparison
The extension was completed with a written comparison of the manual and agentic debugging workflows, including a structured metrics table and discussion of time, defects, and cognitive load. This provides a useful reflection on where Copilot added value and where it introduced overhead.

## Extension Comparison Table

| Metric | Manual | Agentic | Delta |
| --- | ---: | ---: | ---: |
| Time to resolution (min) | 45 | 25 | -20 |
| Lines changed | 78 | 92 | +14 |
| Bugs missed post-fix | 1 | 2 | +1 |
| Cognitive load (1–5) | 5 | 3 | -2 |

## Repository Link

GitHub repository: https://github.com/aa-user15/Expense_tracking_system

All branches and PR history are available in the repository history linked above.
