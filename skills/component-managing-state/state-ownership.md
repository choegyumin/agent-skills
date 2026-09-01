# State Ownership

Do not place state in the nearest consumer. Find its owner from the requirement-driven UI design, and keep the logic that depends on that state within the same ownership boundary.

## Decide Ownership Before Writing Code

Before implementing a new component or modifying an existing one, make the following decisions. Unless the user asks for a design explanation, apply this checklist to the code rather than printing it mechanically:

1. Find the **visually complete UI units** in the requirements and UI design. UI units may be nested.
2. Find the root that starts and coordinates the user flow within the component set corresponding to each UI unit.
3. Determine which UI responsibility and user flow each piece of state exists to fulfill.
4. Place state at the component-set root of the smallest UI unit that completely owns the requirement. Lift it higher only when a parent UI unit must coordinate multiple child units.

If no separate mockup exists, infer UI units from the requirements and from names, rendered structure, and user behavior in the code. Treat names and current component or file boundaries as clues to intent, but do not treat any single clue—including the current state location or prop flow—as the answer.

## Prefer UI Responsibility Over the Nearest Consumer

Prefer root ownership when any of the following is true:

- The state coordinates behavior across multiple descendant UIs.
- It participates in a higher-level user flow such as saving, submission, phase or step transitions, or navigation.
- It represents loading, error, or selection state for the component set as a whole.
- Multiple pieces of state-dependent logic need to be understood together.
- Only one child renders the state, but the root determines the feature's result.

When multiple children use the same state, their closest common parent is only the minimum possible owner. Choose the component-set root of the smallest UI unit that fully owns the requirement, and lift higher only when a parent UI unit must coordinate multiple child units.

A descendant component may independently own state such as:

- Opening and closing a disclosure
- The current position of an independent tab set or carousel
- Focus, hover, or animation state
- Temporary input state that does not affect the result of the parent feature

Do not take away responsibilities a descendant must fulfill on its own merely to centralize everything at the root. Ask: **Which component must fulfill this UI responsibility?**

## Do Not Use These Reasons to Place State

- “Only one component reads this state.”
- “This component is used only once.”
- “Putting it nearby reduces props.”
- “The current code already has this structure.”
- “Context or a store makes the forwarding code shorter.”

These reasons describe code volume and current usage relationships, not ownership of the requirement.

## Move State and Its Dependent Logic Together

After choosing the state owner:

- Put the state and its transitions in the owning component.
- Put handlers that depend on that state—such as save, submit, or branching logic—in the same component.
- Pass current values and event handlers to descendants so they can focus on presentation.
- Leave independently owned UI state inside the descendant responsible for it.

A single component implementation may span multiple files. A controller or presenter with a one-to-one relationship to a component remains part of that component when it owns the same state and flow. Keep ownership cohesive regardless of file count.

## Choose the Correct Owner During First Implementation

Do not treat Lifting State Up only as a later refactoring technique. When ownership is visible in the requirements, place state correctly during the first implementation.

The following Wizard renders multiple Steps under a single `/onboarding/:step` dynamic route. The Steps cannot render independently outside the Wizard. The Wizard owns the route parameter and the transition rules between Steps.

### Incorrect

```tsx
function OnboardingWizardPage() {
  const { params: { step } } = useRouter();

  if (step === "account") return <AccountStep />;
  if (step === "profile") return <ProfileStep />;

  return "ERROR";
}

function AccountStep() {
  const { navigate } = useRouter();

  return (
    <>
      {/* ... */}
      <button onClick={() => navigate("/onboarding/profile")}>Next</button>
    </>
  );
}

function ProfileStep() {
  const { navigate } = useRouter();

  return (
    <>
      {/* ... */}
      <button onClick={() => navigate("/onboarding/account")}>Back</button>
      <button onClick={() => navigate("/onboarding/complete")}>Complete</button>
    </>
  );
}
```

Each Step depends directly on the router and route paths, spreading the Wizard's navigation flow across descendant components.

### Correct

```tsx
function OnboardingWizardPage() {
  const { params: { step }, navigate } = useRouter();

  if (step === "account") {
    return (
      <AccountStep
        onNext={() => navigate("/onboarding/profile")}
      />
    );
  }

  if (step === "profile") {
    return (
      <ProfileStep
        onBack={() => navigate("/onboarding/account")}
        onComplete={() => navigate("/onboarding/complete")}
      />
    );
  }

  return "ERROR";
}

function AccountStep({ onNext }) {
  return (
    <>
      {/* ... */}
      <button onClick={onNext}>Next</button>
    </>
  );
}

function ProfileStep({ onBack, onComplete }) {
  return (
    <>
      {/* ... */}
      <button onClick={onBack}>Back</button>
      <button onClick={onComplete}>Complete</button>
    </>
  );
}
```

`OnboardingWizardPage` interprets the route parameter and owns the transition rules. Each Step reports user intent through callbacks without knowing the route structure.

## Repair Existing Ownership

When state lives in the wrong descendant component:

1. Move the state to the component that owns the requirement.
2. Move handlers and flows that depend on the state with it.
3. Make the descendant a controlled component that receives values and event handlers.
4. If intermediate wrappers only forward props afterward, apply Containment from [`component-composition.md`](./component-composition.md).

Do not change state ownership merely because prop drilling exists. Consider Context or a store only when multiple independent descendants need direct access to the same state. Context and stores are access mechanisms, not criteria for state ownership.

## Final Rule

First identify the UI unit from the UI design, then choose the root of its corresponding component set before placing state and state-dependent logic. Do not use the nearest consumer, reuse count, or prop count as ownership evidence. Keep the overall flow cohesive at the root while leaving independently owned UI state in the descendant responsible for it.

## References

Do not open these references by default. Read only the single relevant document when:

- The user asks for official evidence, sources, or quotations.
- A framework-specific behavior or edge case that this guide does not resolve directly affects the current decision.

Read only references relevant to the current framework and decision.

- [Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)
- [Thinking in React — Step 4: Identify where your state should live](https://react.dev/learn/thinking-in-react#step-4-identify-where-your-state-should-live)
