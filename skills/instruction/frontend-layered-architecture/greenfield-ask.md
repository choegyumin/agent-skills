# New Project (Greenfield) Ask Step

Use this file only to collect the next unresolved user decision for a new frontend project structure.

Ask exactly one decision group per response, then stop.

## Decision Queue

Ask the first unresolved item only.

### 1. OpenAPI Code Generation

Ask whether API client and schema code will be generated from OpenAPI.

Options:

- A. Use OpenAPI code generation.
- B. Do not use OpenAPI code generation.

### 2. Data Access Entry Points

Ask whether the project should use the API adapter pattern for REST API access and optional DTO transformation.

Options:

- A. Use the API adapter pattern.
- B. Do not use the API adapter pattern.

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
- Do not read later step files such as `greenfield-propose.md`, `writing-docs.md`, or `enforcing-rules.md` from this step.
- Do not write files.
