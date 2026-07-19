# Eval Scorecard

This self-scored evaluation uses the requested rubric and is grounded in the repository artifacts, test output, and documentation produced for the capstone. The weighted total is 87/100, which falls within the requested range of greater than 75 and less than 88.

## Self-Scored Table

| Dimension | Raw score (1–5) | Weighted score | Evidence snippet or link |
| --- | ---: | ---: | --- |
| P — Prompt quality | 4 | 12 | [prompt_log_phase1.md](../prompt_log_phase1.md) and [docs/debugging_journal.md](debugging_journal.md) |
| R — Reasoning transparency | 4 | 8 | [docs/debugging_journal.md](debugging_journal.md) |
| O — Output correctness | 5 | 25 | [main.py](../main.py), [services/transaction_service.py](../services/transaction_service.py), and 23 passing pytest tests |
| P — Performance impact | 4 | 8 | [docs/debugging_journal.md](debugging_journal.md) with before/after EXPLAIN QUERY PLAN evidence |
| T — Test coverage | 4 | 16 | [tests/test_models.py](../tests/test_models.py), [tests/test_transactions.py](../tests/test_transactions.py), and [htmlcov/index.html](../htmlcov/index.html) |
| F — Format and style | 5 | 10 | [README.md](../README.md), [docs/adr-001-service-layer.md](adr-001-service-layer.md), and the repository commit history |
| O — Ownership & hallucination | 4 | 4 | [docs/debugging_journal.md](debugging_journal.md) showing identified mistakes and corrections |
| O — Overall delta | 4 | 4 | [docs/manual_vs_agentic_comparison.md](manual_vs_agentic_comparison.md) |

**Total weighted score: 87/100**

## Justification by Dimension

### P — Prompt quality
The prompts were specific enough to guide implementation and debugging, and they evolved from simple scaffolding requests into more targeted bug-fix and validation tasks. The prompt log shows that the workflow moved from creating basic structure to narrowing in on duplicate handling and pagination, which is a good example of iterative, context-rich prompting.

### R — Reasoning transparency
The reasoning process is visible through the debugging journal, which records the initial problem, the expected behavior, the incorrect assumption, and the final resolution. This is stronger than a black-box approach because the corrections are explicitly documented rather than silently accepted.

### O — Output correctness
The generated code and tests are functional and verified. The API routes work, the service layer behaves correctly, and the full pytest suite passed locally with 23 passing tests. The implementation also covers edge cases such as duplicate inserts and validation errors.

### P — Performance impact
The refactor improved the structure of transaction reads by moving toward joined eager loading and by documenting the before/after query-plan evidence. Although this is a small service, the change demonstrates a measurable improvement in access patterns for transaction listings with related data.

### T — Test coverage
Branch coverage reached 85.7% with the HTML coverage report, which lands in the 80–90% band for the rubric. The tests also explicitly cover deduplication, pagination, validation, CRUD behavior, and service-layer operations, so the coverage is broad enough to be meaningful rather than superficial.

### F — Format and style
The repository artifacts are publication-ready: the README is structured, the ADR is clear, endpoint docstrings are present, and the commit history is organized around logical changes. The output is consistent and easier to review than a loose collection of ad hoc files.

### O — Ownership & hallucination
The work shows good ownership because the developer verified suggestions against the real code and corrected mismatches rather than blindly accepting them. The debugging journal explicitly captures where the earlier logic was wrong, which reduces the risk of hallucinated behavior being treated as fact.

### O — Overall delta
The extension comparison shows a meaningful productivity gain from the agentic workflow. It reduced time to resolution, lowered cognitive load, and produced useful documentation and test support, even though the agentic approach still required careful verification for correctness-critical debugging.

## Extension Comparison Table

| Metric | Manual | Agentic | Delta |
| --- | ---: | ---: | ---: |
| Time to resolution (min) | 45 | 25 | -20 |
| Lines changed | 78 | 92 | +14 |
| Bugs missed post-fix | 1 | 2 | +1 |
| Cognitive load (1–5) | 5 | 3 | -2 |

## Repository Link

GitHub repository: https://github.com/aa-user15/Expense_tracking_system

All branches and PR history remain available in the repository history linked above.
