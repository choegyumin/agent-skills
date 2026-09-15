---
name: tidy-tests
description: Use after implementation or refactoring, or during test-quality review, to tidy up tests left behind. Removes temporary or duplicate tests, restores `.only` or `.skip`, or cleans orphaned test resources; not for merely adding tests or running tests. Do not apply mechanically during implementation just because the work follows TDD; use only when the user asks for test-tidying or an explicit test-tidying phase begins.
---

# Tidy Tests

Work can produce tests that help diagnose a problem or reach Green but do not belong in the final result. This is unavoidable in agentic coding, where verification is a necessary part of the workflow. Do not try to prevent these tests from being created; tidy them up after the work.

During tidying, remove temporary tests and remove or merge duplicate tests. Do not expand the scope into general test quality improvements or a search for missing tests.

## Working Mode

- If the user asks for an **investigation**, do not modify files. Report the problem locations, the basis for each decision, and the recommended actions.
- If the user asks for a **modification**, make the changes without seeking separate permission, then report the results.
- If the skill is invoked without further instruction, follow the current session's mode. If the agent was editing files, modify them. If the agent was discussing the work with the user, investigate. If the context does not indicate either mode, investigate.

## Procedure

1. **Set the scope:** Honor the scope specified by the user. If none is specified, cover only tests added or changed during the current work and tests directly related to the changed behavior.
2. **Establish the basis:** Check the user's instructions, specifications, agreed public interfaces, why each test was created during the current work, and which contract it currently protects. Do not treat the implementation or whether the tests pass as the sole source of truth.
3. **Remove or merge tests:** Remove test cases or assertions whose temporary purpose has ended, and remove or merge truly redundant test cases that another test fully replaces. Ask the user when there is not enough evidence to determine which current contract a test protects or how its role relates to another test.
4. **Clean up residue:** Remove imports, fixtures, helpers, mocks, snapshots, and test-only files that became unused after tests were removed or merged. Restore any `.only`, `.skip`, retry, or timeout added temporarily during the current work to its original state.
5. **Finish:** Run the affected tests with project-defined commands. Fix defects introduced by the cleanup and run the tests again. Report why each change was made and the final result.

Do not use tidying as a reason to add tests or search for missing tests. Do not expand beyond removing temporary tests and removing or merging duplicate tests into general test quality improvements. Do not change product behavior, public interfaces, or agreed test boundaries.

## Decision Criteria and Examples

### Transience — Throwaway Test and Regression Test

A test that was needed to reach Green during the work but no longer protects a contract is a Throwaway Test. A test that protects a contract still requiring verification is a Regression Test. Do not remove a test merely because it was created during the work; distinguish between the two.

**Handling principles**

- If the entire test case is a Throwaway Test, delete the case.
- If temporary assertions are mixed into a Regression Test case, remove those assertions instead of the case.
- Keep a test as a Regression Test when there is an ongoing reason for it, such as authorization, security, legal requirements, compatibility, or preventing the recurrence of a confirmed bug.
- If a test appears to be a Throwaway Test but there is not enough evidence to distinguish it from a Regression Test, mark it as a Transience candidate and ask the user.

#### Example 1: A test that verifies only that a change was made

- **User instruction:** "Remove the Save button from the profile editing screen."
- **Agent action:** Adds a case that confirms the button was removed.

```ts
test("removes the Save button from the profile editing screen", () => {
  render();
  expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
});
```

- **Decision:** This test only confirms that the change was made and does not protect any behavior, so it is a Throwaway Test.
- **Action:** Remove the test case.

#### Example 2: An assertion unrelated to the test case's intent that verifies a change was made

- **User instruction:** "Change the Save button text to 'Done' on the profile editing screen."
- **Agent action:** Adds assertions that confirm the text change.

```ts
test("user updates their profile bio", async ({ page }) => {
  await page.goto("/profile");
  await page.getByRole("button", { name: "Edit profile" }).click();
  await page.getByLabel("Bio").fill("Updated bio");

  // Temporary assertions that only confirm the change
  expect(page.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
  expect(page.queryByRole("button", { name: "Done" })).toBeVisible();

  await page.getByRole("button", { name: "Done" }).click();
  await expect(page.getByRole("status")).toHaveText("Profile saved");
  await expect(page.getByText("Updated bio")).toBeVisible();
});
```

- **Decision:** The test case is a Regression Test because it protects the user's goal and flow, but the marked assertions only confirm the change and protect no behavior.
- **Action:** Keep the Regression Test and remove only the change-verification assertions.

#### Example 3: A test that verifies an internal implementation replacement

- **User instruction:** "Remove `lodash.sortBy` and replace it with `Array.prototype.toSorted`. Keep the sorting result unchanged."
- **Current state:** An existing behavior test protects ascending price order.
- **Agent action:** Keeps the existing test and adds a case that confirms the replacement by checking which dependency is used.

```ts
// Existing test
test("returns products in ascending price order", () => {
  const items = [{ price: 3 }, { price: 1 }];

  expect(sortItems(items)).toEqual([{ price: 1 }, { price: 3 }]);
});

// New test
test("sortItems calls Array.prototype.toSorted", () => {
  const toSorted = spyOn(Array.prototype, "toSorted");

  sortItems([{ price: 3 }, { price: 1 }]);

  expect(toSorted).toHaveBeenCalled();
});
```

- **Decision:** The call test verifies that the implementation was replaced rather than protecting behavior, so it is a Throwaway Test.
- **Action:** Remove the call test and keep the existing Regression Test.
- **Exception:** If a separate requirement, such as a licensing or compatibility policy, continuously mandates a specific implementation, the test is a Regression Test and must be kept.

#### Example 4: A test for a discarded implementation

- **Work context:** Exploring ways to reduce duplicate profile requests.
- **Agent action:** Tries an approach that introduces `createProfileCache` and adds a dedicated test.
- **Final state:** The approach is discarded, and the final implementation does not use `createProfileCache`.

```ts
test("profile cache loads the same user only once", async () => {
  const loadProfile = vi.fn().mockResolvedValue(profile);
  // The function is unused by production code but still exists, so the test passes
  const cache = createProfileCache(loadProfile);

  await cache.get("user-1");
  await cache.get("user-1");

  expect(loadProfile).toHaveBeenCalledTimes(1);
});
```

- **Decision:** Both the test target and the verification method exist only for an implementation approach that is absent from the final result, so this is a Throwaway Test.
- **Action:** Remove the test case. Clean up fixtures, mocks, and helpers created only for this approach as residue.

#### Example 5: A test that intentionally verifies a contract

- **User instruction:** "`internalNote` contains sensitive information for support agents only. Do not expose it in customer API responses."
- **Agent action:** Adds a case that verifies the property is absent.

```ts
test("does not expose internal support notes in customer responses", async () => {
  const response = await getCustomer("customer-1");

  expect(response.body).not.toHaveProperty("internalNote");
});
```

- **Decision:** The absence of `internalNote` is itself an information-disclosure contract that must remain protected in external responses, so this is a Regression Test.
- **Action:** Keep the test case.

### Overlap — Redundant Test and Complementary Test

Do not treat tests as needless duplication merely because they verify some of the same behavior. A test is a Redundant Test when its contract, scenario, risk, and verification role fully overlap with another test, or when one role has been split across tests without reason. Identical test code is not the criterion.

**Decision principles**

- Do not classify a test as a Redundant Test merely because its name, code, assertions, or execution path is similar to another test.
- Do not decide whether a test is a Redundant Test or a Complementary Test based solely on whether it shares a seam with another test.
- If an existing test fully replaces a test added during the current work, the new test is a Redundant Test and should be removed.
- If removing either test would lose some verification because their assertions differ, but their verification scope and role are the same, preserve the assertions and merge the tests into one.
- If each test retains a distinct role despite some behavioral overlap, each is a Complementary Test and both should be kept. The overlapping verification is Valuable Redundancy.
- If a test appears to be a Redundant Test but there is not enough evidence to distinguish it from a Complementary Test, mark it as an Overlap candidate and ask the user.

#### Example 6: Differently named tests that verify the same behavior

- **Current state:** Two tests use the same seam to verify the same precondition, action, and result.

```ts
// Existing test
test("authenticated user retrieves their own profile", async () => {
  const response = await getProfile(authenticatedSession);

  expect(response.status).toBe(200);
  expect(response.body.id).toBe("user-1");
});

// New test
test("authenticated profile retrieval succeeds", async () => {
  const response = await getProfile(authenticatedSession);

  expect(response.status).toBe(200);
  expect(response.body.id).toBe("user-1");
});
```

- **Decision:** The existing test fully replaces the new test's contract, scenario, risk, and verification role, so each is a Redundant Test.
- **Action:** Remove the new test and keep the existing test.

#### Example 7: Tests that split verification of one result

- **Current state:** Two tests repeat the same precondition and action through the same seam, splitting verification of a single order-creation result between them.

```ts
test("checkout with a valid cart confirms the order", async () => {
  const order = await checkout(validCart, validPaymentMethod);

  expect(order.status).toBe("confirmed");
});

// A test that needlessly narrows verification of the same behavior
test("checkout with a valid cart returns an order ID", async () => {
  const order = await checkout(validCart, validPaymentMethod);

  // Assertion to merge into the test above
  expect(order.id).toBe("order-1");
});
```

- **Decision:** Neither test fully replaces the other's verification, but neither has a distinct contract, scenario, risk, or verification role. Together they needlessly split one role, so each is a Redundant Test.
- **Action:** Preserve both assertions and merge the tests into one.

#### Example 8: A User Journey Test and a Focused Test

- **Current state:** A User Journey Test and a Focused Test both verify successful checkout for a product added to a cart.

```ts
// User Journey Test that verifies representative behavior
test("user purchases a product", async ({ page }) => {
  await page.goto("/products/product-1");
  await page.getByRole("button", { name: "Add to cart" }).click();
  await page.getByRole("link", { name: "Cart" }).click();
  await page.getByRole("button", { name: "Checkout" }).click();

  await expect(page.getByRole("status")).toHaveText("Order complete");
});

// Focused Test that verifies a specific implementation
test("checkout with a valid cart confirms the order", async () => {
  const order = await checkout(validCart, validPaymentMethod);

  expect(order.id).toBe("order-1");
  expect(order.status).toBe("confirmed");
});
```

- **Decision:** The User Journey Test protects a representative journey and the connections between components, while the Focused Test protects checkout's narrow contract. Some behavior overlaps, but each is a Complementary Test.
- **Action:** Treat the overlapping verification as Valuable Redundancy and keep both tests.

### Residue

Residue is not a test itself. It consists of test execution settings changed temporarily during the work and test resources left unused after an implementation change or after tests are removed or merged.

- **Execution settings:** Restore only `.only`, `.skip`, retry, and timeout settings added or changed during the current work to their original state. Do not change existing settings.
- **Supporting resources:** After confirming they are no longer referenced, remove imports, fixtures, helpers, mocks, and snapshots made unused by the current tidying.
- **Test-only files:** Remove only tracked files whose purpose has completely disappeared because of the current tidying. Do not delete files that are not tracked by version control; report them as candidates instead.
- **Scope:** Do not clean up unrelated existing test code or resources.

## Report Format

Report the results of both investigations and modifications in a message. Write the report in the user's language. The report does not merely summarize actual changes; it records the outcome for every test, assertion, and piece of residue judged within the tidying scope. Report items that were kept and candidates requiring user confirmation, not only items that were removed or restored.

Classify each item as `Transience`, `Overlap`, or `Residue` according to the decision criteria. When one target leads to distinct decisions, such as removing a test and then removing its resources, report them as separate items.

Start with an overall summary, followed by each decision item. Items that share the same basis and classification may be grouped when doing so loses no information.

```md
- Scope: (files and tests reviewed)
- Reviewed: (number of test cases, assertions, and resources)
- Results: (number removed, partially removed, merged, kept, restored, and requiring user confirmation)
- Verification: (commands run and results — modification reports only)

## 1. [Category] Brief description of the issue

- Target: `path:line` — test, assertion, or resource name
- Basis: (verified facts such as the current contract, its purpose during the work, and its relationship to other tests)
- Classification: (`Throwaway Test`, `Regression Test`, `Redundant Test`, `Complementary Test`, `Residue`, or a candidate in the relevant category)
- Recommendation: (remove, partially remove, merge, keep, restore, or defer based on the investigation — investigation reports only)
- Action: (removal, partial removal, merge, retention, restoration, or deferral actually performed — modification reports only)
- User confirmation: (missing evidence that prevented a decision and the question for the user — include only when the decision is deferred)
```

### Report Example — Modification Results

```md
Test tidying is complete. Decisions and actions:

- Scope: `tests/profile.spec.ts`, `tests/checkout.spec.ts`, `tests/export.spec.ts`
- Reviewed: 6 test cases, 2 individual assertions, 2 resources
- Results: 1 test removed, 2 assertions removed, 4 tests kept, 2 resources removed, 1 item requires user confirmation
- Verification: `pnpm test -- tests/profile.spec.ts tests/checkout.spec.ts tests/export.spec.ts` — 24 tests passed

## 1. [Transience] Assertions that only confirm the profile button text change

- Target: `tests/profile.spec.ts:42` — `user updates their profile bio`
- Basis: The profile-saving result remains a contract to protect, but the two assertions checking the previous and current Save button text only confirm completion of this text change.
- Classification: The test case is a `Regression Test`; each of the two assertions is a `Throwaway Test`
- Action: Kept the test case and removed only the two assertions

## 2. [Overlap] New test that duplicates an existing profile retrieval test

- Target: `tests/profile.spec.ts:78`, `tests/profile.spec.ts:91` — 2 tests for an authenticated user's profile retrieval
- Basis: Both tests use the same seam to verify the same precondition, action, and result, and the existing test fully replaces the new test's contract, scenario, risk, and verification role.
- Classification: The new test is a `Redundant Test`
- Action: Removed the new test and kept the existing test

## 3. [Overlap] Overlapping verification in checkout tests with different roles

- Target: `tests/checkout.spec.ts:12`, `tests/checkout.spec.ts:67` — product-purchase User Journey Test and checkout Focused Test
- Basis: Successful checkout overlaps, but one test protects the representative journey and connections between components while the other protects checkout's narrow contract.
- Classification: Each test is a `Complementary Test`
- Action: Kept both tests

## 4. [Transience] Test whose ongoing contract for the previous CSV format is unclear

- Target: `tests/export.spec.ts:105` — `exports a profile in the previous CSV format`
- Basis: The current code alone does not establish whether the previous CSV format remains a supported contract or was retained only for comparison during the work.
- Classification: `Transience` candidate
- Action: Deferred the decision and kept the test
- User confirmation: There is no user instruction or specification establishing whether the previous CSV format remains supported. Should this format continue to be supported?

## 5. [Residue] Fixture and import left after removing a duplicate test

- Target: `tests/fixtures/profile.ts:18`, `tests/profile.spec.ts:4` — fixture and import used only by the removed profile retrieval test
- Basis: Nothing references them after the `Redundant Test` is removed.
- Classification: `Residue`
- Action: Removed the fixture and import
```

#### Reporting the same content as investigation results

Skip verification and use `Recommendation` instead of `Action` for each item.

```md
I reviewed the tests in scope. Decisions and recommendations:

- Scope: `tests/profile.spec.ts`, `tests/checkout.spec.ts`, `tests/export.spec.ts`
- Reviewed: 6 test cases, 2 individual assertions, 2 resources
- Results: 1 test recommended for removal, 2 assertions recommended for removal, 4 tests recommended for retention, 2 resources recommended for removal, 1 item requires user confirmation

## 1. [Transience] Assertions that only confirm the profile button text change

- Target: `tests/profile.spec.ts:42` — `user updates their profile bio`
- Basis: The profile-saving result remains a contract to protect, but the two assertions checking the previous and current Save button text only confirm completion of this text change.
- Classification: The test case is a `Regression Test`; each of the two assertions is a `Throwaway Test`
- Recommendation: Keep the test case and remove only the two assertions

...omitted
```
