# Frontend Layer Boundary Best Practices

Use this file only as a boundary reference after the main routed document leaves a judgment uncertain.

Do not use this file as a directory template, greenfield proposal, or reason to reshape an existing project. Prefer the project’s documented structure and current conventions.

## Example Role Map, Not a Template

The names below are examples for understanding roles. Do not rename or reshape a project to match them.

| Example name | Role | Layer |
| --- | --- | --- |
| `pages` | Screen-level UI orchestration | End-User |
| `widgets` | Standalone feature UI orchestration | End-User |
| `parts` | Domain-aware UI presentation | Domain |
| `features` | Reusable business rules, similar to Clean Architecture Entities and Use Cases | Domain |
| `ui` | General-purpose UI presentation | Shared |
| `utils` | General-purpose utility logic | Shared |
| `api` | External data boundary | Data |

## Boundary Examples

### API Calls Inside a Shared Component

Bad:

```tsx
// shared/ProductCard.tsx
function ProductCard({ productId }: { productId: string }) {
  const { data } = useQuery(productSummaryQueryOptions(productId));
  return <Card>{data.name}</Card>;
}
```

Why it is bad:

- A reusable UI component takes on API calling responsibility.
- Every consumer of this component becomes dependent on the API.

Safer approach:

```tsx
// shared/ProductCard.tsx
function ProductCard({ name }: { name: string }) {
  return <Card>{name}</Card>;
}
```

- Fetch data in the Domain layer or above.
- Pass only display values into Shared layer components.

### Business Rules Inside the Shared Layer

Bad:

```tsx
// shared/ProductCard.tsx
function ProductCard({ product }: { product: ProductSummary }) {
  const canBuy = product.status === "ACTIVE" && product.stock > 0;
  return <Button disabled={!canBuy}>Buy</Button>;
}
```

Or:

```ts
// shared/canBuyProduct.ts
function canBuyProduct(product: ProductSummary) {
  return product.status === "ACTIVE" && product.stock > 0;
}
```

Why it is bad:

- An implementation that should remain pure directly evaluates business rules.

Safer approach:

```tsx
// domain/canBuyProduct.ts
function canBuyProduct(product: ProductSummary) {
  return product.status === "ACTIVE" && product.stock > 0;
}

// shared/ProductCard.tsx
function ProductCard({ disabled }: { disabled: boolean }) {
  return <Button disabled={disabled} />;
}

<ProductCard disabled={!canBuyProduct(product)} />;
```

- Evaluate business rules in the Domain layer.
- Pass only display values into Shared layer components.

### Shared Component Depends on API Schemas

Bad:

```tsx
// shared/ProductCard.tsx
function ProductCard({ outOfStock, stock }: Partial<ProductSummary, "outOfStock"> | Partial<ProductDetail, "stock">) {
  const soldout = outOfStock || stock < 0;
  return <Tag>{soldout ? "Sold Out" : "In Stock"}</Tag>;
}

<ProductCard {...productSummary} />
<ProductCard {...productDetail} />
```

Why it is bad:

- The component is strongly affected by API schema changes.
- If higher-level consumers have different API responses, the props must keep expanding.

Safer approach:

```tsx
// shared/ProductCard.tsx
function ProductCard({ soldout }: { soldout: boolean }) {
  return <Card>{soldout ? "Sold Out" : "In Stock"}</Card>;
}

<ProductCard soldout={productSummary.outOfStock} />
<ProductCard soldout={productDetail.stock < 0} />
```

If you want to reduce duplication:

```tsx
// domain/toProductCardProps.ts
function toProductCardPropsFromProductDetail(product: ProductDetail) {
  return { soldout: product.stock < 0 };
}

<ProductCard {...toProductCardPropsFromProductDetail(productDetail)} />;
```

- Calculate values per API schema, then pass only display values into the component.
- If duplication matters, create conversion functions per API schema.

### Hiding the Whole Flow Inside a Custom Hook

Bad:

```ts
// shared/useProductEditor.ts
function useProductEditor() {
  const { productId } = useParams();
  const form = useForm();
  const mutation = useMutation(updateProductMutationOptions());
  const save = useCallback(() => {
    mutation.mutate({ productId, ...form.getValues() });
  }, [form, mutation]);

  // Logic that blocks leaving the page while the form is dirty
  // `useBlocker()`, `useBeforeUnload()`, etc.

  return { form, save };
}
```

Why it is bad:

- Too many responsibilities and dependencies were assigned while writing everything inside a custom hook.
- Logic is trapped inside the custom hook, creating hidden dependencies and preventing the component from controlling the flow directly.
- Reusing this kind of custom hook can cause serious flow-control problems.

Safer approach:

```tsx
// shared/useNavigationBlocker.ts
type UseNavigationBlockerOptions = { shouldBlock: boolean; confirm: () => Promise<boolean>; onProceed: () => void };
function useNavigationBlocker({ shouldBlock, confirm, onProceed }: UseNavigationBlockerOptions) {
  // ...
}

// pages/ProductEditor.tsx
function ProductEditor() {
  const { productId } = useParams();
  const { formState: { isDirty } } = useForm();
  const { mutate: save } = useMutation(updateProductMutationOptions());

  useNavigationBlocker({
    shouldBlock: isDirty,
    confirm: Dialog.confirm,
    onProceed: () => {/* ... */},
  });

  return <form>{/* ... */}</form>;
}
```

- Move dependencies that the component should own back into the component.
- Refactor according to the remaining responsibility of the custom hook.

## Common Mistakes

| Mistake | Alternative |
| --- | --- |
| Judging layers by folder name only | Look at actual responsibility, import direction, external dependencies, and documented rules together. |
| Putting code in a low-level shared folder only because it is reused | Judge by what the code directly knows and depends on, not by reuse scope. |
| Assuming code in the same abstract layer may freely reference other code in that layer | Distinguish dependency direction by implementation role and responsibility even within the same layer. |
| Moving pure UI upward only because it contains domain words | Check project rules and whether the code-level dependencies are pure. |
| Treating business rules as pure UI concerns because they affect rendering | Keep pure UI props-based; evaluate business rules in a higher-level or domain-appropriate role and pass display state down. |
| Assuming `import type` permits dependencies on a higher layer | Ask whether it would also be acceptable to declare the type in the lower layer and make the higher layer depend on it. |
| Strongly demanding a large structural change in an existing project | Improve within the scope of the work, and mention bigger issues lightly. |
