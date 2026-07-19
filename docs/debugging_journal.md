# Debugging Journal

## Issue 1: Silent duplicate inserts

- Prompt asked: "Why does posting the same transaction twice succeed instead of returning a conflict?"
- Copilot response: The duplicate check should compare description, amount, category, and transaction date, and explicitly reject duplicates with HTTP 409.
- What was correct: The intended behavior was a duplicate rejection, and the API should return 409 for repeated transaction payloads.
- What was wrong: The initial logic only considered duplicates when an explicit transaction date was present. Requests that omitted a date were treated as new records, so duplicates slipped through silently.

## Issue 2: Broken pagination

- Prompt asked: "Why does GET /transactions ignore page and page_size?"
- Copilot response: The endpoint should apply ordering, offset, and limit so that page-based results are returned deterministically.
- What was correct: Pagination requires offset/limit handling and a stable sort order.
- What was wrong: The initial implementation returned the full query result without applying pagination, so every page request returned all transactions.

## Resolution

- Added regression tests for duplicate rejection and pagination.
- Updated the duplicate-check logic to work even when transaction_date is missing.
- Updated the list endpoint to accept page and page_size and return the correct slice of results.
