# Brownfield Project Structure Judgment

Use this file for existing frontend projects when deciding layer, role, file placement, extraction, import direction, or dependency boundaries.

Do not use this file to design a new project structure, write architecture documentation, or configure lint/CI enforcement. Use `greenfield.md`, `writing-docs.md`, or `enforcing-rules.md` for those purposes.

## When to Stop

Immediately before any of the following frontend changes, stop and check roles and boundaries. Do not skip this just because the user did not ask about structure or because the change looks small.

- Planning implementation, reviewing code, or evaluating the user’s suggestion/instruction
- Writing new code
- Creating, moving, or renaming files
- Extracting part of an existing file
- Adding a new import or changing an import path

This checkpoint does not mean you must explain structure at length. If there is no boundary problem, apply it silently and continue. Only when a boundary may be broken should you briefly state the reason and the safe alternative.

## What to Check

1. Are there explicit rules in `AGENTS.md`, `CLAUDE.md`, `README.md`, `ARCHITECTURE.md`, `docs/architecture.md`, or other docs, the current directory structure, or lint rules?
2. Which layer is this code closest to? End-User, Domain, Shared, or Data?
3. What role does this code have? API, UI, business rule, utility, mapper, adapter, route orchestration, etc.
4. Even within the same abstract layer, are there role-based dependency directions that should be disallowed?
5. If this code is placed in a lower-level role folder, will that folder learn higher-level context?
6. Are external data contracts and frontend-owned business rules mixed in the same file or code?
7. Is this code being placed in `components`, `hooks`, `models`, `utils`, `shared`, or a similar location only because it is reusable?
8. If rules already exist, what placement respects those rules while avoiding worse dependency direction within the current scope?

## Role Classification Criteria

Folder names are conventions or rules, not actual roles. Do not judge layers by folder names alone. Inspect project rules and actual usage, then infer the layer and role from observed responsibility.

| Observed responsibility example | Role | Layer |
| --- | --- | --- |
| Page UI, route configuration, URL state subscription, navigation control | Screen-level UI orchestration | End-User |
| Independently functioning feature UI, such as `<NewArrivalsSection shopId={shopId} />` or `<AuthorizationDialog onComplete={onComplete} />` | Standalone feature UI orchestration | End-User |
| Business rules, validation, calculations, and feature flags, such as `canBuyProduct(product)` or `isBetaEnabled(user)` | Reusable business rules, similar to Clean Architecture Entities and Use Cases | Domain |
| Components that render UI only from props but directly express business requirements in code | Domain-aware UI presentation | Domain |
| Components that render UI only from props and do not directly read external data | General-purpose UI presentation | Shared |
| Utility functions/modules, browser API wrappers | General-purpose utility logic | Shared |
| API endpoint calls, API schemas, Query/Mutation Options | External data contracts and execution | Data |

## Default Choices When Ambiguous

- Keep code next to its caller. If there are multiple callers, place it in the layer of the nearest caller. Hidden dependencies are more dangerous than longer caller code, so placing code in a lower layer requires stronger justification.
- Unless the user explicitly instructs that a component should take on a higher-layer role, or unless there is a requirement for it to work independently, treat it as general-purpose UI. In that case, pass data through props.
- If the existing structure is polluted, do not choose a large structural change. Pick the smallest placement that avoids adding new pollution in the current change. Still mention the pollution briefly.

## Existing Codebase Attitude

Follow the existing structure and import conventions first, even when there are no explicit rules.

- If you cannot introduce a new layer folder, choose a narrow namespace folder or consistent filename pattern already present in the existing structure.
- If the structure is ambiguous, preserve existing placement as much as possible, but do not make new code in lower-level roles learn higher-level context.
- This is a minimal compromise for existing structures, not the default for new projects.
- If the user specifies a frontend directory/layer structure, follow that structure first, but verify whether it satisfies domain abstraction, isolated external data contracts, and valid dependency direction.
- In existing codebases, ignore `greenfield.md` and do not introduce a new structure unless the user asks.

## Pressure Rules

Stop and reconsider placement and dependency direction when you see bad signals:

- Type-based folders such as `components`, `hooks`, `models`, or `utils` contain “everything except pages.”
- Business rules, API contracts, URL state, or query logic are placed where the code looks shared.
- Code with different roles is mixed in the same folder or file only because it is convenient.
- External data contracts and frontend-owned code are mixed in the same folder or file.
- Lower-level roles such as general-purpose UI components, utilities, or shared modules directly perform or encode higher-level context such as page flow, routing, form control, API calls, store access, query/data fetching, external data contracts, or business rules.
- A small or quick change is used to justify worsening dependency direction or skipping ownership checks.

Minimum line to hold under pressure:

- Even under time pressure or when the user asks you not to discuss structure, do not agree to place data fetching, API execution, external data contracts, URL state, form control, or business rules inside a lower-level UI, utility, or shared role.
- If the user demands a placement that breaks dependency direction, keep the response short: acknowledge the constraint, reject the invalid dependency, and offer the smallest safe alternative.

## Quick Decision Table

| Situation | Action |
| --- | --- |
| Project rules exist | Follow them. |
| Existing project with unclear rules | Preserve existing structure, but do not worsen dependency direction. |
| Adding a feature to an existing type-based structure | Do not scatter it flatly at the root; group it narrowly by feature namespace or prefix at minimum. |
| A lower-level UI, utility, or shared role starts reading external data or business rules | Stop and check ownership. Prefer props-based UI plus business-rule or data-access logic in an appropriate higher-level role. |
| File placement or import direction is ambiguous | Judge by the context the code directly depends on, not by reusability. |
| A large structural change seems necessary | Do not demand it; mention it briefly and lightly. |

If boundary judgment remains uncertain after this process, read `best-practices.md` for examples. Do not use best-practice examples as a template that overrides the current project structure.
