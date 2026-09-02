# Terms

This skill classifies tests along one axis: whether they preserve a user scenario.

| Category | Definition |
| --- | --- |
| **User Journey Test** | A test that preserves a user's situation, actions, goal, and observed outcome as one scenario. |
| **Focused Test** | A test that does not preserve an entire user scenario and instead focuses on a specific rule, invariant, transformation, contract, collaboration, or technical property. |

This classification draws on Martin Fowler's User Journey Test. Fowler describes a User Journey Test as covering the complete interaction through which a user achieves a goal, while detailed variations in behavior are better checked by more focused tests. This skill calls the latter **Focused Tests**.

This classification is separate from test scope, such as unit, component, integration, or E2E, and from test purpose, such as acceptance, regression, characterization, or contract testing. For example, the same acceptance criterion can be verified in different forms.

## Example: Remote Area Surcharge

User story:

> As a buyer, I want to know the additional delivery charge for my address before placing an order.

Acceptance criterion:

> When the delivery postal code is in a remote area, the Remote Area Surcharge is `$15`.

### Focused Test

The following unit test checks only the domain logic. It verifies the acceptance criterion but does not preserve a user scenario, so it is a Focused Test. A User Journey Test is therefore not synonymous with an Acceptance Test.

```ts
test("charges a $15 remote-area surcharge for a specified postal code", () => {
  const surcharge = calculateRemoteAreaSurcharge("99557");

  expect(surcharge).toBe(15);
});
```

### E2E User Journey Test

The following E2E test checks the complete user scenario. It verifies the same acceptance criterion, but covers the journey from selecting a product to reviewing delivery charges before checkout rather than isolating one story or criterion. It is therefore a User Journey Test.

```ts
test("buyer can review applicable delivery charges before checkout", async ({ page }) => {
  await page.goto("/products");

  await page.getByRole("link", { name: "Mechanical keyboard" }).click();
  await page.getByRole("button", { name: "Add to cart" }).click();
  await page.getByRole("link", { name: "Cart" }).click();
  await page.getByLabel("Delivery postal code").fill("99557");
  await page.getByRole("button", { name: "Check delivery charges" }).click();

  await expect(page.getByText("Remote Area Surcharge: $15")).toBeVisible();
});
```

### User Journey Test that is not E2E

A User Journey Test commonly runs as an E2E test (or Broad Stack Test), but not always. The following test preserves the same complete user scenario while using a simulated DOM instead of a browser. It is still a User Journey Test. A User Journey Test is therefore not synonymous with an E2E Test.

```tsx
test("buyer can review applicable delivery charges before checkout", async () => {
  const user = userEvent.setup();
  const router = createMemoryRouter(appRoutes, { initialEntries: ["/products"] });
  render(<RouterProvider router={router} />);

  await user.click(await screen.findByRole("link", { name: "Mechanical keyboard" }));
  await user.click(screen.getByRole("button", { name: "Add to cart" }));
  await user.click(screen.getByRole("link", { name: "Cart" }));
  await user.type(screen.getByLabelText("Delivery postal code"), "99557");
  await user.click(screen.getByRole("button", { name: "Check delivery charges" }));

  expect(await screen.findByText("Remote Area Surcharge: $15")).toBeVisible();
});
```

**User Journey Test and Focused Test describe what a test focuses on.** A test case focuses either on a user scenario or on something more specific. This axis does not conflict with the test's purpose, scope, or a strategy such as TDD, BDD, or ATDD.

## References

Do not open these references by default. When the user asks for official evidence, sources, or quotations, read only relevant documents.

- [User Journey Test — martinfowler.com](https://martinfowler.com/bliki/UserJourneyTest.html)
- [Story Test — martinfowler.com](https://martinfowler.com/bliki/StoryTest.html)
