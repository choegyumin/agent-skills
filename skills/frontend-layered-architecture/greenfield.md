# Designing the Directory Structure for a New Frontend Project

Use this document when there is no codebase yet, or when a frontend foundation is still being designed and you need to prepare a structure proposal.

This assumes the project is not large enough to need a monorepo, and provides the minimum implementation directory structure for designing an ideal frontend architecture.

Application conditions:

- The user has not explicitly instructed a specific directory structure.
- Propose the directory structure and get user approval before creating files, changing settings, or recording project documentation.

This document is an onboarding guide for actually configuring a new project. Therefore, the directory structure below is not an example; it is the design to apply. Unless there are explicit user instructions or framework rules, do not reinterpret it with other structures or names.

In existing codebases, ignore this document completely unless the user explicitly instructs you to check it. Existing structure, team rules, and user instructions take precedence.

## Design Sequence

Follow this sequence strictly as a turn-by-turn workflow. At each turn, handle only the first unresolved step.

- ⚠️ ASK AT MOST ONE USER-DECISION QUESTION PER RESPONSE.
- After asking a user-decision question, stop and wait for the user's answer before continuing the sequence.
- Do not ask decision questions outside this sequence unless the user explicitly raises a separate topic.

1. Ask whether to use OpenAPI code generation.
2. Ask which Repository layer entry points to use.
3. Apply directory name changes required by framework rules.
4. Propose the directory structure based on the selected options.
5. Explain dependencies between directories.
6. After the top-level structure draft is complete, ask whether the user wants to decide the topics in `Follow-up Decisions After the Initial Structure` now.
7. Ask where to record the selected final structure and decided rules in project documentation.
8. If the user approves documentation, MUST read and follow [`writing-docs.md`](./writing-docs.md) before writing or updating project documentation.
9. After documentation is written and the user has answered the adjustment question, ask whether to configure `eslint-plugin-boundaries`.
10. If approved, enforce the rules through ESLint configuration and, if documentation was already written, update it only with a short note that those rules are also enforced by ESLint.

## User Choice Options

### 1. Whether to Use OpenAPI Code Generation

Ask whether the API client and API schemas will be generated from OpenAPI. This choice first determines whether to create the `api/` layer manually.

#### Option A: Use a Manual API Layer

Keep the API client and API schemas directly in the project.

- Create `api/`, `api/endpoints/`, and `api/schemas/`.

#### Option B: Use OpenAPI-Based Generated Outputs

OpenAPI generated outputs replace the API client and API schema roles.

- Do not create `api/`, `api/endpoints/`, or `api/schemas/`.
- Treat generated clients and schemas as the same layer as `api/*`.
- Generated outputs may take many forms, including pure API clients, endpoint functions, schemas, and Query/Mutation Options for TanStack Query.
- When configuring `eslint-plugin-boundaries`, exclude OpenAPI generated outputs from the automation rules.

### 2. Repository Layer Entry Points

Ask whether to add a `repos/` layer to control the impact radius of external API changes. `repos` defines a layer role only; it does not enforce a specific code pattern such as Repository Classes.

`repos/queries/` and `repos/adapters/` can be used together. If either is selected, also create `repos/schemas/` for DTO transformation types/schemas.

#### Option A: Use `repos/queries/`

Choose this when directly defining Query/Mutation Options for a Query Client library such as TanStack Query.

- Create `repos/`, `repos/queries/`, and `repos/schemas/`.
- `repos/queries/` may perform DTO Transformation, but it is not required.
- Regardless of DTO Transformation, Query/Mutation Options belong in `repos/queries/` because they define Query Client behavior.

#### Option B: Use `repos/adapters/`

Choose this when providing API adapter functions. An API adapter function calls an API endpoint and returns a response with DTO Transformation applied.

- Create `repos/`, `repos/adapters/`, and `repos/schemas/`.
- Do not choose this when DTO Transformation is not needed. In that case, use `api/` or OpenAPI generated outputs directly.
- API adapter functions belong in `repos/adapters/`.

#### Option C: Use Both

Choose this when both Query/Mutation Options and API adapters are needed.

- Create `repos/`, `repos/queries/`, `repos/adapters/`, and `repos/schemas/`.

#### Option D: Do Not Use a Repository Layer

Do not add a frontend-owned external data access layer.

- Do not create `repos/`.
- Higher layers use `api/` or OpenAPI generated outputs directly.

## Directory Structure

The structure below is the maximum structure when OpenAPI code generation is not used and all optional directories are selected. Depending on the selected options, `api/*` and `repos/*` may be omitted.

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
    adapters/
    queries/
    schemas/
```

## Directory Roles

| Directory | Role | Abstract Layer | Description |
| --- | --- | --- | --- |
| `pages` | Screen-level UI orchestration | Application | Page/route-level components. They handle UI flow, data fetching, and orchestration. As the direct layer delivered to users, they may have every type of dependency. |
| `widgets` | Standalone feature UI orchestration | Application | Independently functioning components. They may directly depend on most external data and state such as APIs and stores. Direct dependency on URL state or routes is allowed but not recommended. Examples: `<NewArrivalsSection shopId={shopId} />`, `<AuthorizationDialog onComplete={onComplete} />`. |
| `parts` | Domain-aware UI presentation | Domain | The lowest-level components that express domain language as UI. They understand business requirements or context but do not depend on external services, so direct access to external data or state such as API calls, queries, routers, and stores is not allowed. Example: `<ProductCard name={product.name} />`. |
| `features` | Reusable business rules, similar to Clean Architecture Entities and Use Cases | Domain | Reusable business rules such as product policy, validation, calculations, and feature flags. They exclude API calls and external service access. Compose `features` from pure functions, modules, types, and constants. Examples: `canBuyProduct(product)`, `isBetaEnabled(user)`. |
| `ui` | Generic UI presentation | Foundation | Pure generic UI components similar to a design system. Examples: `<Button />`, `<Switch />`. |
| `utils` | Generic utility logic | Foundation | Generic utilities such as pure functions, browser built-in API extensions, and generic React custom hooks. |
| `api` | Data | Data | External API access layer. |
| `api/endpoints` | Data | Data | API endpoint functions and API request/response execution boundaries. |
| `api/schemas` | Data | Data | API Request/Response and DTO types. |
| `repos` | Data | Data | Data access adapter layer for controlling the impact radius of external API changes. |
| `repos/adapters` | Data | Data | API adapter functions. |
| `repos/queries` | Data | Data | Query/Mutation Options. |
| `repos/schemas` | Data | Data | DTO mappers and transformation types/schemas. |

Notes:

- Think again before adding `widgets`. Most code is sufficiently handled by inlining it in `pages` or abstracting it into `parts` or `ui`. Do not add `widgets` merely to reduce the amount of code needed for reuse.
- `features` is the layer that best reveals real-world business requirements. It is closest to Clean Architecture Entities and Use Cases in this structure, but it must not directly participate in rendering or external service execution. Delegate rendering to `parts`, and compose `features` from pure functions, modules, types, and constants.
- `repos` adjusts interfaces so external API changes do not propagate directly to the Application/Domain layers, and it does not enforce a specific code pattern such as Repository Classes.
- Add framework-provided directories such as `assets` or `public` as needed.

## Dependency Relationships

Except for the Data layer, the default import direction is `pages -> widgets -> parts -> features -> ui -> utils`. Reverse imports are forbidden.

Rules:

- Except for the Data layer, the default import direction is `pages -> widgets -> parts -> features -> ui -> utils`.
- Inside the Data layer, the default import direction is `repos -> api`.
  - Inside `repos`, the default import direction is `repos/queries -> repos/adapters -> repos/schemas`.
  - Inside `api`, the default import direction is `api/endpoints -> api/schemas`.
- Depending on the selected directory structure, `api/*` or `repos/*` may not exist.
- When `pages` and `widgets` access files in the same layer, they are limited to internal private modules. For example, a product list page must not import a product detail page.
- `pages` and `widgets` may access all Data-layer code, including OpenAPI generated outputs, `api/*`, and `repos/*`.
- `parts` and `features` may access only schema code in the Data layer, such as OpenAPI generated schema/types, `api/schemas`, and `repos/schemas`. They must not access Data-layer execution code such as API clients, endpoint/adapter functions, or query/mutation options.
- When `features -> ui` is used, rendering JSX or importing components/hooks is forbidden. This dependency should mainly be used for types or data transformation.

## Placement Examples

| Code | Recommended Location |
| --- | --- |
| `<NewArrivalsSection shopId={shopId} />` | `widgets/` |
| `<ProductCard name={product.name} />` | `parts/` |
| `toProductCardPropsFromProductDetail(product)` | `parts/` |
| `canBuyProduct(product)` | `features/` |
| `getProductsAPI()` | `api/endpoints/` |
| `getProductsAdapter()` | `repos/adapters/` |
| `productsQueryOptions()` | `repos/queries/` |
| `toProductFromProductDTO(dto)` | `repos/schemas/` |
| `formatCurrency(price)` | `utils/` |

## Application Principles

- When there is no codebase and the user has not proposed a structure, treat this document’s directory structure as the baseline to apply. Do not replace it with another architecture style, reinterpret it with different layer names, or rename directories based on preference.
- Changes based on framework rules are allowed. For example, with Next.js App Router, use `app/` instead of `pages/`.
- Do not add directories outside the selected structure unless framework conventions require them or the user explicitly decides to add them during the design conversation. Do not add speculative directories because they may become useful later or because similar projects often use them.
- If the user instructs a specific directory structure, do not demand that this document’s structure be followed exactly. Instead, verify whether the instructed structure satisfies the intent of the `frontend-layered-architecture` skill: adding a domain abstraction layer, isolating external data contracts, and designing correct dependency direction between layers. If it does not, propose improvements.

## Follow-up Decisions After the Initial Structure

- This document defines only the top-level boundaries for the initial structure. Detailed subfolder structures inside each layer, barrel files, and co-location rules are follow-up discussion topics after the top-level structure draft is complete.
- After the top-level structure draft, ask whether to decide these three follow-up topics now: layer-internal grouping strategy, whether to use barrel files, and whether to co-locate related files.
- For the Data layer, the agent must not proactively propose domain-based subgroup structure. If the user explicitly wants it, accept it, but the agent using this skill must not ask about or propose it first.
- Do not ask about file naming separately. By default, match implementation names and file names. Make exceptions only when the user presents special requirements.

## Recording and Automating Layer Relationships

Once the top-level structure and follow-up decisions are confirmed, ask which project document should record them. If the user does not specify a file, suggest candidates such as `README.md` or `ARCHITECTURE.md` and get approval.

When asking for the document location, briefly explain that if these decisions are not recorded in documentation, follow-up decisions such as file naming, co-location, and layer subfolder structure may not be preserved as project rules and may evaporate after the conversation.

If the user approves documentation:

- Stop using this document as the writing guide for the project document.
- MUST read and follow [`writing-docs.md`](./writing-docs.md) before writing or updating any project document.
- Write only the selected final structure and the current project rules.
- After writing documentation, ask whether the recorded rules need adjustment before moving on. Do not ask about ESLint automation in the same response.
- After the user answers the adjustment question, return to this section and continue to the ESLint automation decision.

If the user declines or asks to skip documentation at any point:

- Do not write documentation.
- Before proceeding, briefly explain that follow-up decisions not recorded in documentation may not be preserved as project rules.

After the documentation step has been completed or skipped, ask the user whether to automate import rules with `eslint-plugin-boundaries`.

If the user approves ESLint automation:

- Do not just propose it verbally. Install and configure `eslint-plugin-boundaries` directly.
- First check which package manager the project uses.
- Then check whether the project uses ESLint flat config or legacy config.
- Check the latest documentation for actual configuration syntax when working. Use Context7 if available.
- Express the dependency relationships above as boundaries rules according to the selected options, except OpenAPI generated outputs.
- Run lint after configuration to verify that the rules work.
- If documentation was written, add only a short note that the configured import rules are also enforced by ESLint.

If the user declines ESLint automation:

- Do not configure ESLint.
- If ESLint is not configured, do not add text to the documentation saying that ESLint is absent.

Automation goals:

- Define each top-level directory as a boundaries element type.
- Define directories with roles different from their parent directory, such as `api/endpoints`, `api/schemas`, `repos/adapters`, `repos/queries`, and `repos/schemas`, as separate types.
- Omit directories that were not selected. For example, omit `api/` if OpenAPI generated outputs replace it, and omit `repos/` if no repository entry point was selected.
- Do not define OpenAPI generated outputs themselves as boundaries elements or rules.
- Put only the allowed import directions from the “Dependency Relationships” section into the rules.
- Role-specific caveats must not narrow the allowed import directions; automating such exceptions would make the rules too complex.
- Do not implement “limited to internal modules of the same role” in configuration.
- Unless the user explicitly requests additional enforcement, do not enforce each base layer’s internal grouping, barrel-file usage, or co-location rules through configuration.
