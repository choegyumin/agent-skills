# Greenfield Ask Step

Use this file only to collect the next unresolved user decision.

Ask exactly one decision group per response, then stop.

## Decision Queue

Ask the first unresolved item only.

### 1. OpenAPI Code Generation

Ask whether API client and schema code will be generated from OpenAPI.

Options:

- A. Use OpenAPI code generation.
- B. Do not use OpenAPI code generation.

### 2. Data Access Entry Points (Repository pattern)

Ask which repository entry points the project should use for REST API access and query client integration, such as TanStack Query.

Here, Repository means a Data-layer access boundary, not the Repository Class pattern.

Options:

- A. Query/Mutation Options entry point, such as TanStack Query options.
- B. API adapter function entry point for API calls and optional DTO transformation.
- C. Both entry points.
- D. No repository entry point.

### 3. Follow-up Conventions

Ask this only after the top-level structure and dependency direction are approved.

Ask these together as one decision group, then stop:

- Layer-internal grouping strategy.
- Barrel file policy.
- Related file co-location policy.

## Boundaries

- Do not interpret what the answers imply for directories.
- Do not propose directory structure.
- Do not explain dependency direction.
- Do not ask for documentation location.
- Do not read later step files such as `greenfield-propose.md` or `writing-docs.md` from this step.
- Do not write files.
