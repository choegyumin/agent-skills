---
name: component-managing-state
description: "Use whenever designing, implementing, modifying, reviewing, or refactoring component-based UI development (React, Vue, Angular, Svelte, SolidJS, Astro, Flutter widgets, SwiftUI views, etc.). Guides decisions about state ownership, lifting state up, avoiding prop drilling, passing children and slots, Containment and Specialization."
---

# Managing State in Component-Based UI Development

This skill provides patterns for choosing which component should own state and logic, then keeping those responsibilities cohesive. It applies to any approach that composes independent UI units such as components, widgets, views, or composables. Only the examples use React syntax.

## Shared Premise

Component-based UI development starts by dividing requirement-driven UI design into functional UI units. Therefore, the first factor in deciding where state and logic belong is **UI design**, not a programming principle.

A UI unit here is not an individual component. It is a component set that renders one visually complete UI. A UI unit may contain other UI units, and each nested component set may have its own root and ownership. Apply the Proximity Principle at the **component-set** level rather than the individual-component level. State used only by a child is still proximate when it lives at the root of that child's component set.

UI design determines the following ownership boundaries within a component set:

- Which component serves as the component-set root and orchestrates state and the logic that depends on it?
- Which descendant components should directly own independent responsibilities and their logic? Is that code truly delegated?
- Which component owns the content, and which component only places that content? How should they compose?

Do not mechanically co-locate state and logic in the nearest individual consumer. Applying proximity only at the individual-component level is bad design. Do not treat the current file structure or usage site as the ownership decision. Identify the UI unit and the component set that implements it first.

## Router

Route by the required design decisions, not terms in the user's request. Read only the necessary documents, and read both when the decisions overlap.

| Purpose | Read |
| --- | --- |
| Identify UI units; choose ownership for state, state-dependent logic, and coordinated flow; lift state up | [`state-ownership.md`](./state-ownership.md) |
| Decide who owns or constructs content; design how a layout or wrapper receives and places caller-owned content through children, slots, or equivalent APIs; build a specialized component from a generic UI primitive; choose Containment or Specialization | [`component-composition.md`](./component-composition.md) |
| Decide both state or user-flow ownership and content construction or placement—for example, lift state to a root that also supplies layout content, or define interaction-state and content boundaries for a component built on a generic UI primitive | Read [`state-ownership.md`](./state-ownership.md) first, then [`component-composition.md`](./component-composition.md) |

## Scope

- During first implementation, do not initially co-locate state in the nearest consumer. Identify the UI unit and the component set that implements it from the requirements and UI design first.
- During refactoring, do not treat the current prop flow or component boundaries as evidence of the intended design.
- UI design does not require a separate mockup. If none exists, infer it from the requirements and from names, rendered structure, and user interactions in the code. Treat names and current component or file boundaries as clues to intent, not as answers by themselves.
