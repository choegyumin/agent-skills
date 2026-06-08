# Greenfield Project Propose Step

Use this file only after the required design decisions are answered and before the top-level structure is approved.

This step interprets the collected answers, proposes the top-level directory structure, explains dependency direction, then asks for approval.

## Baseline Directory Structure

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

Apply selected options before presenting the final proposal:

- If OpenAPI generated outputs replace manual API code, omit `api/`, `api/endpoints/`, and `api/schemas/`; treat generated client/schema code as Data layer code.
- If no repository entry point is selected, omit `repos/`.
- If only Query/Mutation Options are selected, include `repos/queries` and `repos/schemas`.
- If only API adapters are selected, include `repos/adapters` and `repos/schemas`.
- If both repository entry points are selected, include `repos/queries`, `repos/adapters`, and `repos/schemas`.
- Add framework-required directories or renames only when the framework requires them. For example, Next.js App Router may use `app/` instead of `pages/`; Vite React does not require renaming `pages/`.

## Directory Role Reference

| Directory | Role | Abstract Layer | Description |
| --- | --- | --- | --- |
| `pages` | Screen-level UI orchestration | End-User | Page/route-level components. They handle UI flow, data fetching, and orchestration. As the direct layer delivered to users, they may have every type of dependency. |
| `widgets` | Standalone feature UI orchestration | End-User | Independently functioning components. They may directly depend on most external data and state such as APIs and stores. Direct dependency on URL state or routes is allowed but not recommended. Examples: `<NewArrivalsSection shopId={shopId} />`, `<AuthorizationDialog onComplete={onComplete} />`. |
| `parts` | Domain-aware UI presentation | Domain | The lowest-level components that express domain language as UI. They understand business requirements or context but do not depend on external services, so direct access to external data or state such as API calls, queries, routers, and stores is not allowed. Example: `<ProductCard name={product.name} />`. |
| `features` | Reusable business rules, similar to Clean Architecture Entities and Use Cases | Domain | Reusable business rules, validation, calculations, and feature flags. They exclude API calls and external service access. Compose `features` from pure functions, modules, types, and constants. Examples: `canBuyProduct(product)`, `isBetaEnabled(user)`. |
| `ui` | General-purpose UI presentation | Shared | Pure general-purpose UI components similar to a design system. Examples: `<Button />`, `<Switch />`. |
| `utils` | General-purpose utility logic | Shared | General-purpose utilities such as pure functions, browser built-in API extensions, and general-purpose React custom hooks. |
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
- `repos` adjusts interfaces so external API changes do not propagate directly to the End-User/Domain layers, and it does not enforce a specific code pattern such as Repository Classes.

## Dependency Rules

Except for the Data layer, the default import direction is `pages -> widgets -> parts -> features -> ui -> utils`. Reverse imports are forbidden.

Rules:

- Inside the Data layer, the default import direction is `repos -> api`.
  - Inside `repos`, the default import direction is `repos/queries -> repos/adapters -> repos/schemas`.
  - `repos/adapters` may call `api/endpoints` and use `api/schemas`.
  - Inside `api`, the default import direction is `api/endpoints -> api/schemas`.
- Depending on the selected directory structure, `api/*` or `repos/*` may not exist.
- When `pages` and `widgets` access files in the same layer, they are limited to internal private modules. For example, a product list page must not import a product detail page.
- `pages` and `widgets` may access all Data layer code, including OpenAPI generated outputs, `api/*`, and `repos/*`.
- `parts` and `features` may access only schema code in the Data layer, such as OpenAPI generated schema/types, `api/schemas`, and `repos/schemas`. They must not access Data layer execution code such as API clients, endpoint/adapter functions, or query/mutation options.
- `ui` and `utils` must not depend on business rules, routing, stores, query client libraries such as TanStack Query, API schemas, or API execution code.
- When `features -> ui` is used, rendering JSX or importing components/hooks is forbidden. This dependency should mainly be used for types or data transformation.

## Placement Reference

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

## Structure Proposal Rules

- When there is no codebase and the user has not proposed a structure, treat this file’s baseline directory structure as the structure to apply. Do not replace it with another architecture style, reinterpret it with different layer names, or rename directories based on preference.
- Apply framework-required changes only when the framework requires them. For example, with Next.js App Router, use `app/` instead of `pages/`.
- Do not add directories outside the selected structure unless framework conventions require them or the user explicitly decides to add them during the design conversation. Do not add speculative directories because they may become useful later or because similar projects often use them.
- If the user instructs a specific directory structure, do not demand that this file’s baseline structure be followed exactly. Instead, verify whether the instructed structure satisfies the intent of the `frontend-layered-architecture` skill: adding a domain abstraction layer, isolating external data contracts, and designing correct dependency direction between layers. If it does not, propose improvements.

## Proposal Output

In the response:

1. Summarize the selected decisions.
2. Show the proposed top-level structure.
3. Explain the dependency direction.
4. Ask whether this top-level structure and dependency direction should be used.

Do not ask follow-up convention questions in this step.
Do not ask for documentation location in this step.
Do not write files in this step.
