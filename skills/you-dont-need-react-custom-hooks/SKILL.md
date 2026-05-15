---
name: you-dont-need-react-custom-hooks
description: Use when React component or custom hook work may involve extracting hooks, changing hook responsibilities, or hiding dependencies behind custom hooks
---

# You Don't Need React Custom Hooks

## Overview

A React custom hook is not the default unit of abstraction; it is the last option. Custom hooks make it easy to add dependencies and side effects, which can give a module too many responsibilities and create tight coupling internally. These hidden dependencies make code harder to trace, so modules that depend on React need stricter responsibility boundaries than ordinary modules.

This skill does not ban custom hooks. Instead, before creating one, first check whether an ordinary module is enough. Use a hook only when its concern, responsibility, role, and dependencies are clear.

## When to Use

Use this skill when:

- Evaluating React component or custom hook code
- Designing or implementing a new React component or custom hook
- Refactoring an existing custom hook or extracting a new custom hook from a React component

Do not use this skill when:

- Refactoring ordinary functions or modules unrelated to React
- Only calling an already validated general-purpose hook, without creating or modifying a hook

## Core Rules

Before creating or suggesting a custom hook, always ask:

1. Can this logic be expressed as an ordinary function or module without React hooks?
2. Can the custom hook's single responsibility be stated in one sentence?
3. Are this hook's dependencies also dependencies that its callers should be allowed to own?
4. If this hook were deleted and inlined into the caller, would the code become clearer?

Do not print these questions as a mechanical checklist. But when creating, suggesting, or refactoring a custom hook, naturally explain why the code must be a hook instead of being inlined into the component or extracted as an ordinary function/module.

## Alternatives to Consider First

Consider smaller alternatives before a custom hook.

| Situation | Prefer first |
| --- | --- |
| Calculation, data transformation, validation, API calls | Ordinary function/module |
| Event handlers or small composition logic used by one component | Component-local logic |
| UI responsibility has become too large | Candidate for component redesign |
| State or control flow is hard to follow | Candidate for component redesign |

The first two alternatives are immediately applicable. The last two should expose a structural problem instead of hiding it behind a hook. If the structural change is in scope, apply Kent Beck's Tidy First principle and make the structural change first. If it is out of scope, propose it as a separate refactoring.

## Invalid Reasons for Creating a Hook

The following are not valid reasons to create a custom hook.

| Bad rationale | Response |
| --- | --- |
| "The component is too long" | Length is not a reason to extract a hook. |
| "There is duplicated code" | The duplication may be accidental, or an ordinary function may be enough. |
| "It separates concerns and makes the call site cleaner" | Responsibility, role, and dependencies matter more. Do not hide dependencies the caller should know about. |
| "It becomes easier to test" | Prove that testing becomes easier because this must be a hook. Prefer an ordinary function first. |

## Always Good Custom Hooks

### React state transitions are the core responsibility

This applies when state values and state transitions are the hook's essential responsibility. These hooks do not directly depend on external data.

Examples:

```ts
useDisclosure();
useSelection();
useStepper();
useToggle();
useDebouncedValue(value, delay);
```

### React lifecycle/effects are the core responsibility

This applies when the logic cannot be expressed as an ordinary function and React rendering, subscriptions, cleanup, refs, or DOM integration are central to solving the problem.

Examples:

```ts
useWindowSize();
useIntersectionObserver(ref);
useFocusTrap(ref);
useOnClickOutside(ref, handler);
useWhiteboardInteraction(ref, handlers);
useQuery(queryOptions);
useChatRoomSubscription(roomId, client);
useGeolocation();
```

## Always Bad Custom Hooks

### Thin wrappers

Do not create a wrapper that only renames an existing dependency. In these cases, it is usually better to create an ordinary function for the arguments passed into the existing hook or for the value returned from it.

Examples:

```ts
useUserProfileQuery(userId);
useWorkspaceRouteParams();
useCurrentWorkspace();
```

```ts
// Bad
function useUserProfileQuery(userId: string) {
  return useQuery(userProfileQueryOptions({ userId }));
}

// Good
const query = useQuery(userProfileQueryOptions({ userId }));
```

```ts
// Bad
function useWorkspaceRouteParams() {
  const params = useParams();
  return useMemo(() => parseWorkspaceRouteState(params), [params]);
}

// Good
const params = useParams();
const { workspaceId } = useMemo(() => parseWorkspaceRouteState(params), [params]);
```

## Custom Hooks That Require Judgment

Business-logic hooks can be acceptable, but they are not always good. Most bad custom hooks happen here.

Examples:

```ts
useUserProfileForm(initialProfile);
useCheckoutPaymentSelection(paymentMethods);
useProductImageCarousel(images);
useCommentComposer(initialText);
```

Judge them by whether the hook's responsibility is clear, whether it hides dependencies the caller should know about, and whether it traps logic inside the hook in a way that makes the component unable to control the flow.

### Bad custom hook smells

These are signs that responsibility boundaries have become blurry.

```ts
const {
  user,
  isLoading,
  error,
  refetch,
  selectedTab,
  navigateTab,
  form,
  setForm,
  submit,
  notify,
} = useUserProfile();
```

This hook hides dependencies on external data fetching, tab state, routing, form state and submission, and notifications. The component became shorter, but the behavior became harder to predict.

Better directions:

- Put calculations, validation, and transformation in ordinary functions.
- Keep external data fetching inline in the component with hooks such as `useQuery`, or make a separate hook only when appropriate.
- Keep form state inline in the component with hooks such as `useForm`, or make a separate hook only when appropriate.
- Keep routing and notifications inline in the component, and pass handlers as arguments when needed.
- Split the component if its responsibility is too large. But avoid pushing too much state or logic into child components in a way that makes the flow harder to follow.
- Code complexity is bounded by business complexity plus overhead. If the design is sound and the component is only orchestrating behavior but the code is still complex, consider a Controller Pattern Hook only if the project already uses that pattern.

Inlining can be better than abstraction. A component that is longer because it uses lifting state up but still controls the flow is better than a shorter component whose dependencies and flow are hard to understand. An ideal component is composed from small modules, not from one large hook.

### When Controller Pattern Hooks Are Acceptable

A Controller Pattern Hook is a project-specific design strategy, not a general recommendation. It is allowed only when the project already uses this pattern. The project may call it by another name, so before introducing it, directly confirm that code similar to the examples already appears repeatedly.

A Controller Pattern Hook separates business logic from UI to improve readability or testing strategy. It always has a 1:1 relationship with a component, and it contains all of that component's code except rendering/markup.

The responsibility of a Controller Pattern Hook is "the target component's functionality/behavior," so its internal logic can be tightly coupled and can perform multiple roles. However, it cannot own responsibilities that the target component itself could not own. In other words, a Controller Pattern Hook is only code separation, so it follows the rules for React components, not special rules for custom hooks.

Example:

```tsx
export function CheckoutPage() {
  const controller = useCheckoutPageController();

  return (
    <section>
      <h2>Checkout</h2>
      <CheckoutForm
        paymentMethods={controller.availablePaymentMethods}
        selectedPaymentMethodId={controller.selectedPaymentMethodId}
        onPaymentMethodChange={controller.selectPaymentMethod}
        onSubmit={controller.submit}
      />
    </section>
  );
}
```

Allowed only when:

- It has a 1:1 relationship with a specific component.
- It is colocated in the same directory.
- Its name clearly says it is a controller.
- It is not intended for reuse.
- It owns only responsibilities that the target component may own.
- This pattern is already used in the project.

If one Controller Pattern Hook starts being used by multiple components, that is a failure signal. If you want to split a Controller Pattern Hook into multiple hooks, the problem is not custom-hook design; revisit the component/layer design.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Naming a hook broadly, such as `useSomething`, without revealing its responsibility | Narrow the name and return value so they express one role. |
| Sharing a hook because code is duplicated | Check the current responsibility boundary, dependencies, fit, and whether the duplication is accidental. |
| Creating a hook because the component is long | First check whether an ordinary function, ordinary module, or component split is possible. |
| Hiding dependencies inside a hook that the caller should know about | Keep dependencies the caller must control at the call site. |
| Trapping responsibility inside a hook that the component should not own | Move the responsibility elsewhere or redesign the structure so the caller does not own it. |

## Final Rule

Custom hooks are not a tool for shortening code. Choose a custom hook only when React dependencies such as state, effects, lifecycle, subscriptions, cleanup, or refs are essential to a single responsibility. If existing custom-hook code violates this standard, before splitting it into more hooks, first check whether it can be moved back into ordinary functions, ordinary modules, or component-local logic, and propose that as a separate refactoring when needed.
