# Component Composition

Choose Containment or Specialization according to actual component ownership. Ordinary component composition is outside this decision.

- **Containment**: A component receives UI it does not own through `children`, slots, content projection, or an equivalent mechanism.
- **Specialization**: A generic component is configured into a component with specific meaning, behavior, and invariants.

The patterns are not mutually exclusive. A specialized component may use a Containment-based primitive internally.

## Route React Implementation Patterns

If the task only requires concrete React composition implementation patterns—such as Compound Components, Context Providers, children-based composition, or Explicit Variant Components—and does not require content ownership or Containment-versus-Specialization decisions, route to the `vercel-composition-patterns` skill.

If the task requires both ownership decisions and implementation patterns, complete the ownership decision in this document first, then use `vercel-composition-patterns` to choose the implementation pattern.

If that skill is not installed, do not invoke it or attempt to install it.

## Decide Content Ownership Before Designing the Component API

Before implementing a new component or modifying an existing API, make the following decisions. If no separate mockup exists, infer content ownership from the requirements and from names, rendered structure, and user flows in the code. Treat names and current component or file boundaries as clues to intent, not as answers by themselves. Unless the user asks for a design explanation, apply this checklist to the code rather than printing it mechanically.

1. Find nested UI units and their corresponding component sets in the requirements and UI design.
2. Find the root that owns state and user flow within each component set.
3. Within the component set for the current UI unit, distinguish components that own actual content from components that only place it.
4. Use Containment when a component only places content.
5. Consider Specialization when a component owns independent meaning and invariants.

If neither condition applies and a component merely renders concrete descendants directly, leave it as ordinary composition.

## Use Containment When a Component Owns Only Placement

Make the container unaware of its concrete content when:

- The shared concern is an outer structure, layout, style, or interaction boundary.
- The caller owns the actual subtree, its state, and its callbacks.
- The container has no reason to use the concrete content type or its props.
- The container places caller-owned content in multiple independent regions.

Implement it as follows:

- Let the caller construct the final subtree.
- Use `children` for one region and named slots for multiple regions.
- Remove descendant-specific props from the container API.
- Connect state and callbacks where the content is constructed instead of forwarding them through the container.

```tsx
function OnboardingWizardPage() {
  const { params: { step }, navigate } = useRouter();

  return (
    <WizardLayout progress={<WizardProgress step={step} />}>
      {step === "account" && (
        <AccountStep
          onNext={() => navigate("/onboarding/profile")}
        />
      )}
      {step === "profile" && (
        <ProfileStep
          onBack={() => navigate("/onboarding/account")}
          onComplete={() => navigate("/onboarding/complete")}
        />
      )}
    </WizardLayout>
  );
}
```

`WizardLayout` owns only the placement of the progress indicator and current Step. `OnboardingWizardPage` constructs the Steps and their transition flow.

## Signals That Favor Specialization

The following signals strengthen the case for Specialization. They are recommendations, not mandatory requirements, and not every signal must be present:

- Its name and role still make sense when detached from the parent UI.
- It guarantees behavior or invariants that must always hold.
- It prevents callers from repeatedly rebuilding the same configuration.
- Its internal state and UI behavior are genuinely its own responsibility.

The following reasons alone are not enough to justify Specialization:

- “This component is used only once.”
- “Naming the current JSX makes it easier to read.”
- “A prop-forwarding wrapper makes the file cleaner.”
- “Only one content shape is currently needed.”
- “Explicit props feel safer than `children`.”

These reasons may accompany a valid Specialization, but they do not establish independent responsibility or invariants by themselves. Wrapping the current content in another component is not sufficient on its own.

```tsx
function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <Dialog
      title="Confirm"
      actions={
        <>
          <button onClick={onCancel}>Cancel</button>
          <button onClick={onConfirm}>Confirm</button>
        </>
      }
    >
      <p>{message}</p>
    </Dialog>
  );
}
```

`Dialog` is a Containment component that receives caller-owned content. `ConfirmDialog` is a specialization that guarantees confirm/cancel meaning and behavior.

Reuse count is not a criterion. A component used once may own an independent responsibility, while a component used many times may still be only a wrapper around the current content.

## Do Not Steal Descendant Responsibilities

The root orchestrates state and flow for the whole component set. It should not take state and UI behavior that descendants must fulfill independently.

A descendant may directly own responsibilities such as:

- Opening and closing a disclosure
- Focus management
- Animation lifecycle
- The interaction behavior of a general-purpose input component

Do not use “independent responsibility” to hide state and logic that belong to the parent requirement. Check whether the responsibility remains intact when the component is detached from the parent UI.

## Treat Prop Forwarding as a Signal to Review Composition

When intermediate components forward state and callbacks they do not use, treat it as a strong signal to review state ownership and component responsibilities. If ownership is correct and the intermediate component only places content, consider replacing the forwarding chain with Containment.

### Prop-Forwarding Structure

```tsx
function OrdersPage() {
  const { data: orders } = useSuspenseQuery(/* ... */);
  const [selectedIds, setSelectedIds] = useState([]);

  return (
    <OrderManagement
      orders={orders}
      selectedIds={selectedIds}
      onSelectionChange={setSelectedIds}
      onDelete={() => deleteOrders(selectedIds)}
    />
  );
}

function OrderManagement({ orders, selectedIds, onSelectionChange, onDelete }) {
  return (
    <PageLayout>
      <OrdersToolbar
        selectedIds={selectedIds}
        onDelete={onDelete}
      />
      <OrdersTable
        orders={orders}
        selectedIds={selectedIds}
        onSelectionChange={onSelectionChange}
      />
    </PageLayout>
  );
}

function OrdersToolbar({ selectedIds, onDelete }) {
  return (
    <Toolbar>
      <BulkOrderActions
        selectedIds={selectedIds}
        onDelete={onDelete}
      />
    </Toolbar>
  );
}
```

`OrderManagement` fixes the current toolbar-and-table combination without owning independent behavior or invariants. The APIs of `OrderManagement` and `OrdersToolbar` become coupled to descendant data contracts.

### Containment Alternative

```tsx
function OrdersPage() {
  const { data: orders } = useSuspenseQuery(/* ... */);
  const [selectedIds, setSelectedIds] = useState([]);

  return (
    <PageLayout
      toolbar={
        <BulkOrderActions
          selectedIds={selectedIds}
          onDelete={() => deleteOrders(selectedIds)}
        />
      }
    >
      <OrdersTable
        orders={orders}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
    </PageLayout>
  );
}
```

`OrdersPage` constructs the final toolbar and table subtrees. `PageLayout` only places those subtrees in its toolbar and body regions, and no intermediate component knows order-specific props.

## Consider Refactoring an Existing Structure

If review confirms that a specialized component chain occupies a placement-only Containment boundary, consider the following transformation:

1. Find the highest component that owns the final content and state.
2. Let that component construct the final subtree directly.
3. Change intermediate layouts and wrappers to receive `children` or named slots.
4. Remove props that were only forwarded and specialized wrappers without responsibilities.
5. Reassess each specialization and preserve those with clear meaning, behavior, or invariants.

The following signals strengthen the case for this transformation:

- An intermediate component only forwards props it does not use.
- Every content combination requires another specialized component.
- Boolean or variant props switch entire subtrees.
- Escape-hatch APIs such as `renderX` or `customX` keep accumulating.

Containment does not solve every case of prop drilling. Context or a store may be appropriate when multiple independent descendants need direct access to the same data or when an ancestor cannot construct the subtree.

## Final Rule

Use Containment when a component owns only content placement. Prefer Specialization when it owns independent meaning or invariants. Let the state owner construct the final subtree, and avoid making intermediate wrappers forward descendant-specific props when a containment boundary would preserve ownership more clearly.

## References

Do not open these references by default. Read only the single relevant document when:

- The user asks for official evidence, sources, or quotations.
- A framework-specific behavior or edge case that this guide does not resolve directly affects the current decision.

Read only references relevant to the current framework and decision.

- [Composition vs Inheritance](https://legacy.reactjs.org/docs/composition-vs-inheritance.html)
- [Passing Props to a Component — Passing JSX as children](https://react.dev/learn/passing-props-to-a-component#passing-jsx-as-children)
