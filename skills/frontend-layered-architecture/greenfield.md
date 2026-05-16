# Designing the Directory Structure for a New Frontend Project

Use this document when there is no codebase yet, or when a frontend foundation is still being designed and you need to prepare a structure proposal.

This assumes the project is not large enough to need a monorepo, and provides the minimum implementation directory structure for designing an ideal frontend architecture.

Application conditions:

- The user has not explicitly instructed a specific directory structure
- You will propose the structure to the user and get approval before creating files, changing settings, or writing documentation

This document is an onboarding guide for actually configuring a new project. Therefore, the directory structure below is not an example; it is the design to apply. Unless there are explicit user instructions or framework conventions, do not reinterpret it with other structures or names.

In existing codebases, ignore this document completely unless the user explicitly instructs you to check it. Existing structure, team rules, and user instructions take precedence.

## Design Sequence

1. Decide whether to use a Query/Mutation pattern.
2. Decide whether to implement DTO Transformation responsibility.
3. Decide how to separate Foundation UI.
4. Adjust directory names according to framework conventions.
5. Propose the directory structure based on the selected options.
6. Explain dependencies between directories.
7. Ask the user whether to configure `eslint-plugin-boundaries`.
8. If approved, enforce the rules through ESLint configuration. If declined, ask again whether to record the rules in documentation and where.

## User Choice Options

### 1. Whether to Use a Query/Mutation Pattern

Ask whether the project will use a Query/Mutation pattern for server state or external data state management. Recommend Option A by default.

If Option A is chosen but it is not yet decided whether to use a library or implement it manually, suggest a suitable option such as TanStack Query based on the conversation so far.

#### Option A: Use the Pattern

Add a Repositories layer for managing Query/Mutation Options.

- Add the Repositories layer. Create `repos/` and `repos/queries/`.

#### Option B: Do Not Use the Pattern

Do not add a Repositories layer for managing Query/Mutation Options.

- Create no folders for this.

### 2. Whether to Implement DTO Transformation Responsibility

DTO Transformation is used to isolate client code from the impact of API changes. Explain the tradeoff and recommend the option that fits the user’s project.

#### Option A: Implement the Responsibility

Implement DTO Mapper functions and transformation types/schemas. This increases stability but also increases duplicate code.

It is useful for apps where backend and frontend deployment timing is hard to control, such as apps that must go through app-store review. It can also be replaced by having the backend guarantee backward compatibility.

- Add the Repositories layer. Create `repos/` and `repos/schemas/`.

#### Option B: Do Not Implement the Responsibility

Do not implement DTO Mapper functions or transformation types/schemas.

Deployment stability is lower, but there is no duplicate code and the structure stays simple. This is useful for web services.

- Create no folders for this.

### 3. How to Separate Foundation UI

Foundation UI is organized as either one folder or two folders depending on project choice. Recommend Option A for larger projects and Option B for smaller projects.

#### Option A: `ui` + `parts` Folders (Distinguish Whether Domain Language Is Included)

`ui` contains only generic components unrelated to the product and without domain language, similar to a design system. Examples: `Button`, `Dialog`, `TextField`, `Spinner`.

`parts` contains components that include domain language but are still pure generic components at the code level. Examples: `ProductCard`, `OrderStatusTag`, `WorkspaceLayout`.

With this option, `ui` cannot reference `api/schemas/` or `repos/schemas/`; only `parts` can reference them for expressing prop types.

#### Option B: Single `ui` Folder (Ignore Whether Domain Language Is Included)

`ui` contains all pure UI components regardless of whether they include domain language. Examples: `Button`, `Modal`, `ProductCard`, `OrderStatusTag`, `WorkspaceLayout`.

With this option, `ui` may include domain language, so it may reference `api/schemas/` and `repos/schemas/` for expressing prop types.

## Directory Structure

The structure below is described based on Option A. `parts` and `repos` are added or removed depending on the selected options.

```txt
src/
  pages/
  widgets/
  parts/
  ui/

  features/
  utils/

  api/
    endpoints/
    schemas/
  repos/
    queries/
    schemas/
```

## Directory Roles

| Directory | Role | Abstract Layer | Description |
| --- | --- | --- | --- |
| `pages` | UI + Business Logic | Delivery | Page/route-level components and private modules. Knows URL context and page flow, and directly implements features or orchestrates pieces. |
| `widgets` | UI + Business Logic | Domain | Independently complete functional components and private modules. Must not directly depend on URL context (routes), but may directly depend on most external data and state such as API, repos, store, and form state. |
| `parts` | UI | Foundation | Pure generic components that include domain language at the name/meaning level. May reference schemas to express prop types depending on the selected directory structure. |
| `ui` | UI | Foundation | Pure UI components similar to a design system. Depending on the selected directory structure, it may also absorb the role of `parts`. |
| `features` | Business Logic | Domain | Reusable business logic such as data calculation, validation, and feature flags. |
| `utils` | Utility Logic | Foundation | Generic utilities such as pure functions, browser built-in API extensions, and generic React custom hooks. |
| `api` | Data | Data | API Client. |
| `api/endpoints` | Data | Data | API endpoint functions and API request/response execution boundaries. |
| `api/schemas` | Data | Data | API Request/Response and DTO types. |
| `repos` | Data | Data | Frontend-controlled external data access layer. Query Client. May be omitted depending on the selected directory structure. |
| `repos/queries` | Data | Data | Frontend-controlled Query/Mutation Options. May be omitted depending on the selected directory structure. |
| `repos/schemas` | Data | Data | DTO mappers and transformation types/schemas. Data code that is affected by API changes but controlled by the frontend. May be omitted depending on the selected directory structure. |

`widgets` is the place for complete Domain UI. Most code is sufficiently handled by inlining it in `pages` or abstracting it into `parts`/`ui`, so do not add `widgets` merely because something is reusable.

Directories provided by frameworks, such as `assets` or `public`, are not described here.

## Dependency Relationships

The list below defines allowed import directions. Imports not listed here are forbidden by default. Depending on the selected directory structure, `repos/*` may not exist, and `parts` may be merged into `ui`.

```txt
pages
  -> pages             # limited to internal modules of the same component
  -> widgets
  -> parts
  -> ui
  -> features
  -> utils
  -> repos
  -> repos/queries
  -> repos/schemas
  -> api
  -> api/endpoints
  -> api/schemas

widgets
  -> widgets           # limited to internal modules of the same component
  -> parts
  -> ui
  -> features
  -> utils
  -> repos
  -> repos/queries
  -> repos/schemas
  -> api
  -> api/endpoints
  -> api/schemas

parts                  # may be absorbed into the ui folder
  -> parts
  -> ui
  -> utils
  -> repos/schemas
  -> api/schemas

ui
  -> ui
  -> utils

features
  -> features
  -> utils
  -> repos/schemas
  -> api/schemas

repos/queries          # may not exist
  -> utils
  -> repos
  -> repos/queries     # limited to internal modules of the same query
  -> repos/schemas
  -> api
  -> api/endpoints
  -> api/schemas

repos/schemas          # may not exist
  -> utils
  -> api/schemas

repos                  # may not exist
  -> utils
  -> api

api/endpoints
  -> utils
  -> api
  -> api/endpoints     # limited to internal modules of the same endpoint
  -> api/schemas

api/schemas
  -> api/schemas
  -> utils

api
  -> api
  -> utils

utils
  -> utils
```

## Application Principles

- This document is the default for cases where no codebase exists and the user has not proposed a structure, so do not reinterpret it with different structures or names. Exceptions apply only when the user gives explicit instructions, framework conventions require it, or the actual project structure already exists. At this stage, do not pre-open exceptions based on possibilities.
- Changes based on framework conventions are allowed. For example, with Next.js App Router, use `app/` instead of `pages/`.
- This document defines only the top-level boundaries for the initial structure. Defer decisions about each layer’s subfolder structure and barrel files until actual implementation. Do not propose extra folders or barrel files during initial setup.
- If the user instructs a specific directory structure, do not demand that this document’s structure be followed exactly. Instead, verify whether the instructed structure satisfies the intent of the `frontend-layered-architecture` skill: adding a domain abstraction layer, isolating external data contracts, and designing correct dependency direction between layers. If it does not, propose improvements.

## Placement Examples

| Code | Recommended Location |
| --- | --- |
| `NewArrivalProducts` | `widgets/` |
| `ProductCard` | `parts/` if present, otherwise `ui/` |
| `canBuyable()` | `features/` |
| `getProducts()` | `api/endpoints/` |
| `productsQueryOptions()` | `repos/queries/` |
| `formatCurrency()` | `utils/` |

## Recording or Automating Layer Relationships

After proposing the directory structure and dependency relationships, ask the user whether to automate them with `eslint-plugin-boundaries`.

If the user approves:

- Do not just propose it verbally. Install and configure `eslint-plugin-boundaries` directly.
- First check which package manager the project uses.
- Then check whether the project uses ESLint flat config or legacy config.
- Check the latest documentation for actual configuration syntax when working. Use Context7 if available.
- Express the dependency relationships above as boundaries rules according to the selected options.
- Run lint after configuration to verify that the rules work.

If the user declines:

- Ask again whether to record the layer relationships in documentation, and if so, which file to record them in.
- Only if the user approves, record the selected directory structure and layer relationships in the README, architecture document, or another project document specified by the user.
- The document should record the directory structure, roles, and import directions.

Automation goals:

- Define each top-level directory as a boundaries element type.
- Define directories with roles different from their parent directory, such as `api/endpoints`, `api/schemas`, `repos/queries`, and `repos/schemas`, as separate types.
- Omit directories that were not selected. For example, omit `parts/` if it was not selected.
- Put only the allowed import directions from the “Dependency Relationships” section into the rules.
- Do not implement “limited to internal modules of the same role” in configuration.
- Do not enforce each base layer’s subfolder structure or barrel-file usage through configuration.
