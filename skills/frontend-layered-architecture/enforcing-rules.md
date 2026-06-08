# Enforcing Architecture Rules

Use this file when the user wants architecture rules enforced by tools such as ESLint, CI, import boundary checks, or similar automation.

Do not use this file for general structure judgment, new project structure selection, or architecture documentation by itself. Use `brownfield.md`, `greenfield.md`, or `writing-docs.md` for those purposes.

## Scope

This file covers how to translate approved architecture rules into enforceable checks. It is not a plugin syntax reference.

If the user asks for a specific ESLint/plugin/API configuration, check current tool documentation before proposing syntax. Follow the project’s package manager and ESLint config style.

## Rule Source

Before writing or proposing rules, identify the source of truth:

1. Project architecture document, such as `docs/architecture.md`.
2. Explicit user-approved directory/layer mapping.
3. Existing lint rules or import conventions.
4. Existing project structure, only when no stronger source exists.

Do not invent lint rules from abstract layer names alone. End-User, Domain, Shared, and Data are abstract concepts, not enforceable folder names unless the project maps them to real directories.

If there is no project document or explicit mapping, first establish the mapping through `brownfield.md` or a user-approved architecture document before enforcing it.

## Lint-able vs Judgment Rules

Separate rules before implementation.

Usually lint-able:

- Real folder/path import direction.
- Forbidden imports from lower-level folders to higher-level folders.
- Data execution access limited to selected directories.
- Restricted package imports in selected folders.

Usually not fully lint-able:

- Whether a component is general-purpose UI or domain-aware UI.
- Whether code encodes business rules indirectly.
- Whether a custom hook hides too much flow control.
- Whether a type-only import leaks higher-level context.

Keep judgment-heavy rules in architecture documentation or code review guidance. Do not pretend they are fully enforced by lint rules.

## Implementation Checklist

1. Confirm the user wants tool enforcement, not only documentation.
2. Check the package manager.
3. Check whether ESLint uses flat config or legacy config.
4. Check existing lint scripts and current lint failures.
5. Check current documentation for selected ESLint/plugin syntax before editing.
6. Encode only approved real directories and import directions.
7. Do not include directories that were not selected or mapped.
8. Do not define OpenAPI generated outputs as boundary elements.
9. Run lint after configuration.
10. If architecture documentation exists, add only a short note that selected rules are tool-enforced. Do not put setup details in the architecture document.

If the user declines tool enforcement, do not configure tools and do not add an absence note to documentation.

## Output Rules

When reporting or proposing enforcement:

- State the rule source used.
- State which rules are tool-enforced.
- State which rules remain human-judgment rules.
- State any directories or rules intentionally omitted because they were not approved or not lint-able.
