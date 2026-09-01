---
name: business-logic-in-components
description: Use whenever discussing, designing, implementing, modifying, reviewing, or refactoring component-based UI development (React, Vue, Angular, Svelte, SolidJS, Astro, Flutter widgets, SwiftUI views, etc.). Provides the meanings and boundaries of domain and presentation concerns.
---

# What is Business Logic in Component-Based UI Development?

This guidance applies to all component-based UI development that composes independent UI units such as components, widgets, views, and composables. Only the examples use React syntax.

## Core Principle

In component-based UI development, business logic is primarily determined by UI and feature requirements and changes with them. It is therefore natural for business logic to exist in components. However, Business Logic does not always equal Business Rules.

For some people, Business Logic means only code that expresses Business Rules. For others, it also includes code that presents those rules on screen and implements their behavior. The term Business Logic is ambiguous in modern usage and adds confusion, so stop using it. Use the following terms instead.

| Term | Meaning |
| --- | --- |
| **Business Rules** | Real-world policies, conditions, constraints, and calculation methods defined for a product or organization. This refers to the rules themselves, not code. |
| **Domain Logic** | Code that expresses Business Rules. |
| **Presentation Logic** | Code coupled to a component. Even when it expresses Business Rules, code coupled to a component is Presentation Logic, not Domain Logic. |
| **UI Logic** | A subset of Presentation Logic. It handles UI presentation and general interactions such as expansion, selection, focus, and animation, rather than product-specific requirements. For example, shadcn/ui consists entirely of UI Logic. |

## Distinguish Them by Layer

Distinguish Domain Logic from Presentation Logic by role and owning layer. The directory structure is the most direct way to reveal these layers.

- Logic coupled to a component belongs to the Presentation/Application Layer.
- The Domain Layer owns Business Rules that can be defined and executed without a UI.
- The Presentation Layer may use Domain Logic, but the Domain Layer must not depend on Presentation concerns.

Do not immediately call a condition or calculation in UI code Domain Logic merely because it appears to express Business Rules. While coupled to the UI, it remains Presentation Logic. Treat it as a **Domain Logic candidate** worth isolating.

```tsx
// components/expense-approval.tsx
function ExpenseApproval({ employee, expense }) {
  // This expresses a Business Rule, but it is Presentation Logic because it is coupled to the UI.
  const canApprove =
    employee.role === "manager" && expense.amount <= employee.approvalLimit;

  return <button disabled={!canApprove}>Approve</button>;
}
```

The approval rule becomes Domain Logic once it is separated from the UI and owned by the Domain Layer.

```ts
// domain/expense-approval.ts
export function canApproveExpense(employee, expense) {
  return employee.role === "manager" && expense.amount <= employee.approvalLimit;
}
```

## Not Every Code Extraction Is Layer Separation

Moving code to a particular file or directory, or renaming it, does not change its layer. Presentation Logic remains Presentation Logic when extracted into a separate function, hook, controller, or presenter without changing its role or dependencies.

For example, when a controller in React's Controller Pattern has a one-to-one relationship with a specific component and owns that component's state and behavior, treat both as one component implementation. This does not separate Domain Logic. It is only a physical separation of Presentation Logic, similar to writing a Presenter in MVP.

```tsx
// components/expense-approval/controller.ts
function useExpenseApprovalController(expense) {
  const mutator = useApproveExpenseMutation();

  function approve() {
    mutator.mutate(expense.id);
  }

  return { approve, isPending: mutator.isPending };
}

// components/expense-approval/index.tsx
function ExpenseApproval({ expense }) {
  const controller = useExpenseApprovalController(expense);
  return <button onClick={controller.approve}>Approve</button>;
}
```

The code is split across files, but both files still contain Presentation Logic.
