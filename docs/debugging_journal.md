# Debugging Journal

## Phase 3 — Refactoring and query-plan evidence

### EXPLAIN QUERY PLAN

Before refactor (naive transaction-only lookup):

```sql
EXPLAIN QUERY PLAN
SELECT * FROM transactions;
```

```text
[(2, 0, 216, 'SCAN transactions')]
```

After refactor (eager-loaded join with related category data):

```sql
EXPLAIN QUERY PLAN
SELECT transactions.id,
       transactions.description,
       transactions.amount,
       transactions.category,
       transactions.category_id,
       transactions.transaction_date,
       transactions.created_at,
       categories.id,
       categories.name
FROM transactions
LEFT OUTER JOIN categories
  ON categories.id = transactions.category_id
ORDER BY transactions.created_at DESC, transactions.id DESC
LIMIT 10;
```

```text
[(5, 0, 216, 'SCAN transactions'),
 (7, 0, 45, 'SEARCH categories USING INTEGER PRIMARY KEY (rowid=?) LEFT-JOIN'),
 (33, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')]
```

Interpretation:
- The refactor moves the access pattern from a simple transactions scan toward a joined eager-load path.
- This allows the service layer to load related category data in the same query instead of relying on repeated follow-up lookups.
- The result is a more efficient read pattern for transaction listings that include related metadata.

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
