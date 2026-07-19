# ADR 001: Use a service layer for transaction business logic

- Status: Accepted
- Date: 2026-07-19

## Context

The expense tracker started as a small FastAPI application with transaction endpoints and direct database access. As the API grew, the business rules for validation, duplicate detection, and pagination became more important. Keeping those rules inside route handlers would have made the code harder to test, maintain, and evolve.

A clear separation was needed between HTTP concerns and domain behavior so the application could remain simple while supporting future enhancements such as additional validation rules, richer reporting, and safer reuse across multiple entry points.

## Decision

We will place transaction-related business logic in a dedicated service layer and inject that service into the FastAPI route handlers. The service layer will own the core operations for creating, listing, fetching, deleting, and detecting duplicates for transactions.

This approach keeps the route handlers focused on request parsing, validation, and response handling, while the service layer handles application behavior and persistence coordination.

## Consequences

### Positive

- Business logic becomes easier to test in isolation.
- Route handlers remain thin and easier to read.
- The service layer can be reused by future APIs or background workers.
- Dependencies are clearer because the route layer depends on a well-defined service interface.

### Negative

- The project gains one additional abstraction layer.
- Developers must understand the separation between API routes and service methods when making changes.

## Alternatives considered

### Keep business logic directly in the route handlers

This would have been simpler at first, but it would have mixed HTTP concerns with application rules and made the code harder to test and reuse.

### Put business logic in the database layer or models only

This would have reduced the number of layers, but it would have made the logic less explicit and less suitable for coordinating multiple operations or responding to API-level errors consistently.

## Links

- Implementation entry point: main.py
- Service implementation: services/transaction_service.py
