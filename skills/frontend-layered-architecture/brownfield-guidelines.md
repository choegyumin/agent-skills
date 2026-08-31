# Existing Project (Brownfield) Guidelines

Use this file from [`brownfield.md`](./brownfield.md) in either case:

- An existing frontend project has no documented or approved architecture rules, and its design is not consistently recognizable.
- The existing design is intentional, and the user proposes or requests adding, removing, renaming, or reorganizing directories or directory roles.

Do not use this file for ordinary placement inside an intentional structure when the user has not requested a structural change.

## Workflow

### Intentional Structure Change

1. Use documented or approved rules and consistently recognizable roles, dependency directions, and external data boundaries as the source of truth.
2. Identify the requested directory or directory-role change, then check whether it preserves or clarifies those responsibilities and boundaries.
3. Prefer existing terminology and structural patterns. Treat the references below as role and dependency checks, not mandatory directory names or a replacement architecture.
4. Limit the work to the requested change and directly affected code. If part of the request breaks a boundary, reject only that part and give the smallest safe alternative.

### Unstructured Project

1. Inspect enough relevant and adjacent code to distinguish a consistent design from an isolated file. If roles and boundaries become recognizable, return to `brownfield.md`.
2. Otherwise, apply the baseline below to new and changed code only. Do not migrate the entire codebase unless the user explicitly requests it.
3. Preserve any existing directory that serves the Data role. If none exists, create `data/`; do not impose a fixed child-directory structure inside it.

After either workflow, use `brownfield.md` for ordinary placement, extraction, and import decisions. Route documentation and tool enforcement to `writing-docs.md` and `enforcing-rules.md` when requested.

## Baseline Directory Structure

Apply this directory structure only in the Unstructured Project workflow.

```txt
src/
  pages/
  widgets/

  parts/
  features/

  ui/
  utils/

  data/
```

Apply project decisions before using the structure:

- Reuse an existing directory that already serves the Data role instead of creating `data/`.
- If no existing directory serves the Data role, create `data/`.
- Do not impose fixed child directories inside the Data layer. Endpoint, schema, adapter, and contract roles may be organized according to project needs.
- Add framework-required directories or renames only when the framework requires them. For example, Next.js App Router may use `app/` instead of `pages/`; Vite React does not require renaming `pages/`.

## Directory Role Reference

| Directory | Role | Abstract Layer | Description |
| --- | --- | --- | --- |
| `pages` | Screen-level UI orchestration | End-User | Page/route-level components. They handle UI flow, data fetching, and orchestration. As the direct layer delivered to users, they may have every type of dependency. |
| `widgets` | Standalone feature UI orchestration | End-User | Independently functioning components. They may directly depend on most external data and state such as APIs and stores. Direct dependency on URL state or routes is allowed but not recommended. Examples: `<NewArrivalsSection shopId={shopId} />`, `<AuthorizationDialog onComplete={onComplete} />`. |
| `parts` | Domain-aware UI presentation | Domain | The lowest-level components that express domain language as UI. They understand business requirements or context but do not depend on external services, so direct access to external data or state such as API calls, queries, routers, and stores is not allowed. Example: `<ProductCard name={product.name} />`. |
| `features` | Reusable business rules, similar to Clean Architecture Entities and Use Cases | Domain | Reusable business rules, validation, calculations, and feature flags. They exclude API calls and external service access. Compose `features` from pure functions, modules, types, and constants. Examples: `canBuyProduct(product)`, `isBetaEnabled(user)`. |
| `ui` | General-purpose UI presentation | Shared | Pure general-purpose UI components similar to a design system. Examples: `<Button />`, `<Switch />`. |
| `utils` | General-purpose utility logic | Shared | General-purpose utilities and wrappers that receive application-specific state, policy, and actions through parameters. |
| `data` | External data contracts and access boundary | Data | Data-role directory selected from the existing project structure; its child roles are organized according to project needs. |

Notes:

- Think again before adding `widgets`. Most code is sufficiently handled by inlining it in `pages` or abstracting it into `parts` or `ui`. Do not add `widgets` merely to reduce the amount of code needed for reuse.
- `features` is the layer that best reveals real-world business requirements. It is closest to Clean Architecture Entities and Use Cases in this structure, but it must not directly participate in rendering or external service execution. Delegate rendering to `parts`, and compose `features` from pure functions, modules, types, and constants.
- Treat Data as external contract code consumed by the frontend. It may live inside the repository or be written by frontend developers; that does not change its Data role.

## Dependency Rules

Except for the Data layer, the default import direction is `pages -> widgets -> parts -> features -> ui -> utils`. Reverse imports are forbidden.

Rules:

- Within the Data layer, keep external contracts and execution boundaries separate from End-User and Domain responsibilities, using project-appropriate child roles.
- When `pages` and `widgets` access files in the same layer, they are limited to internal private modules. For example, a product list page must not import a product detail page.
- `pages` and `widgets` may access all Data layer code.
- `parts` and `features` may access only Data layer schema/type code. They must not access Data layer execution code.
- `ui` and `utils` must not depend on business rules, routing, stores, query client libraries, API schemas, or API execution code.
- When `features -> ui` is used, rendering JSX or importing components/hooks is forbidden. This dependency should mainly be used for types or data transformation.

## Placement Reference

| Example Code | Recommended Location | Placement Cue |
| --- | --- | --- |
| `<ProductDetailPage />` | `pages/` |  |
| `<NewArrivalsSection shopId={shopId} />` | `widgets/` |  |
| `<ProductCard name={product.name} />` | `parts/` |  |
| `toAvatarPropsFromUser(user)` | `parts/` | Maps domain-accessible data into a reusable UI presentation model |
| `<Button onClick={handleClick} />` | `ui/` |  |
| `toDisplayDate(date)` | `ui/` | Formatting depends on design-system display rules |
| `canBuyProduct(product)` | `features/` |  |
| `isNullableOrEmpty(value)` | `utils/` |  |
| `getProductsAPI(payload)` | Data-role directory (fallback: `data/**/*`) | API request execution |
| `productsQueryOptions(payload)` | Data-role directory (fallback: `data/**/*`) | Declare alongside the regular function it uses. |
| `toProductFromProductDTO(dto)` | Data-role directory (fallback: `data/**/*`) or `features/` | Keep external DTO adaptation in Data; keep Domain models and business rules in `features/`. |

## Response

### Intentional Structure Change

- Explain only the affected roles, dependency direction, and external data boundaries in the project's terminology.
- Limit the response to the requested change. Do not label the design unstructured or present baseline directory names as mandatory.

### Unstructured Project

- State that the design is unstructured, then show the baseline architecture and dependency direction.
- Apply it to new and changed code only unless broader migration is explicitly requested. Do not ask for approval first.
