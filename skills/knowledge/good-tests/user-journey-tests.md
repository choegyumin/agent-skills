# User Journey Tests

## Test location

Do not colocate User Journey Tests with implementation files. Keep them in a dedicated directory. Use the first applicable location in this list and do not consider the later options:

1. If the project or test tool has a dedicated directory convention suitable for User Journey Tests, use it. For example, Cucumber uses `features/` and Cypress uses `cypress/e2e/`.
2. If there is no dedicated convention but the project has a shared test root, use `journeys/` beneath it, such as `tests/journeys/`.
3. If neither exists, use a top-level `journeys/` directory.

Within that directory, organize tests by user goals and journeys, not by implementation modules or technical layers.

## Test boundary

Run User Journey Tests at the seams agreed on for the project. Include components that are relevant to the risk being verified and whose exclusion or replacement with a test double would change the user's actions or observed outcome. Do not narrow an agreed E2E seam within individual tests merely to reduce test cost. Follow [test-doubles.md](./test-doubles.md) when replacing system boundaries.

## Choosing journeys

Choose User Journey Tests around goals users want to accomplish in the system, not around individual User Stories. Several User Stories may compose or change one journey, so do not add a new User Journey Test for every User Story.

For each use case, start with one representative path. This is usually the happy path through which the user achieves the goal. Add an alternative or recovery path as a separate User Journey Test only when that path is important in its own right and provides independent user value.

Limit the suite to a small number of critical paths. Choose paths whose failure would prevent users from receiving the product's core value or would create a serious business problem.

### Example: User Stories and a user journey

Assume the buyer's core goal is to complete a product order. The following User Stories all compose the same journey:

- A buyer can add a product to the cart.
- A buyer can enter a delivery address.
- A buyer can pay by card.

**BAD:** Add separate `add to cart`, `enter delivery address`, and `pay by card` User Journey Test cases for the three User Stories. Each test preserves only part of the journey rather than the user's goal.

**GOOD:** Represent the three User Stories in one User Journey Test case named `buyer can order a product`. Not every path must be merged into one test. For example, recovering from a declined payment by using another payment method may be a separate User Journey Test when that recovery has independent user value.

## Writing scenarios

Keep one user goal in each test. The user's situation, the actions required to achieve the goal, and the outcome the user observes must form one coherent scenario.

Name the test after the goal the user achieves or the outcome they receive, not an implementation detail or individual rule. Make the test body show the sequence of user actions directly. Do not combine several paths in one test with conditional logic.

Set up state that exists before the journey through test data or public test helpers when appropriate. Do not bypass meaningful actions within the goal-seeking journey through an internal API or direct repository manipulation.

Observe results through the interface presented to the user. Assert an intermediate state only when the user needs it to decide or perform the next action. A scenario may need several assertion statements, but all of them must establish the same user goal. Do not make a User Journey Test fail because only minor copy or an implementation detail changed.

### Example: A coherent user scenario

```ts
// BAD: Combines successful payment and recovery from failure with conditional logic
test("buyer can process an order", async ({ page, paymentScenario }) => {
  // Omitted: Sign in as a test customer, add a product to the cart, and open checkout.

  await page.getByLabel("Delivery address").fill("1 Teheran-ro, Gangnam-gu, Seoul");

  if (paymentScenario === "approved") {
    await page.getByLabel("Card number").fill(validCardNumber);
    await page.getByRole("button", { name: "Place order" }).click();
  } else {
    await page.getByLabel("Card number").fill(declinedCardNumber);
    await page.getByRole("button", { name: "Place order" }).click();
    await expect(page.getByText("Payment failed")).toBeVisible();
    await page.getByLabel("Card number").fill(backupCardNumber);
    await page.getByRole("button", { name: "Place order" }).click();
  }

  await expect(page.getByRole("heading", { name: "Order confirmed" })).toBeVisible();
});

// BAD: Bypasses goal-seeking actions and outcome observation through internal interfaces
test("buyer can order a product", async () => {
  const order = await createOrderThroughInternalApi(customer, cart);
  expect(await ordersRepository.find(order.id)).toMatchObject({ status: "confirmed" });
});

// GOOD: Preserves user actions and the observed outcome as one scenario toward one goal
test("buyer can order a product", async ({ page }) => {
  // Omitted: Sign in as a test customer, add a product to the cart, and open checkout.

  await page.getByLabel("Delivery address").fill("1 Teheran-ro, Gangnam-gu, Seoul");
  await page.getByLabel("Card number").fill(validCardNumber);
  await page.getByRole("button", { name: "Place order" }).click();

  await expect(page.getByRole("heading", { name: "Order confirmed" })).toBeVisible();
});
```

The customer account and signed-in state are preconditions, so a helper may create them. Product selection through order confirmation is the goal-seeking journey, so perform and observe it through the user interface.

## Testing variations

Use one representative concrete example in each User Journey Test. Verify input combinations, boundary values, detailed error conditions, and other variations within the same journey through Focused Tests. Do not repeat the complete journey with a data table or parameterized test.

A variation may have its own User Journey Test when it changes the user's goal, action sequence, or the meaning of the observed outcome enough to become a distinct journey.

### Example: Repeating the complete journey by card network

```ts
const cards = [
  { network: "Visa", number: visaTestCard },
  { network: "Mastercard", number: mastercardTestCard },
];

// BAD: Repeats the same complete user journey for each card network
for (const card of cards) {
  test(`buyer can order a product with ${card.network}`, async ({ page }) => {
    // Omitted: Sign in as a test customer, add a product to the cart, and open checkout.

    await page.getByLabel("Delivery address").fill("1 Teheran-ro, Gangnam-gu, Seoul");
    await page.getByLabel("Card number").fill(card.number);
    await page.getByRole("button", { name: "Place order" }).click();

    await expect(page.getByRole("heading", { name: "Order confirmed" })).toBeVisible();
  });
}

// GOOD: Uses Focused Tests for card-network-specific authorization behavior
for (const card of cards) {
  test(`authorizes ${card.network} cards`, async () => {
    const result = await authorizePayment({ cardNumber: card.number, amount: 100 });
    expect(result.status).toBe("approved");
  });
}
```

Use one representative card for the complete ordering journey. Verify authorization behavior for each card network through Focused Tests.

## Maintaining journeys

When a product change alters an existing journey, update the existing User Journey Test rather than adding another test. Add a new test only for a new user goal or an independent path.

Merge tests that verify the same goal and path, and delete journeys that users no longer perform. Keep User Journey Tests as a small collection of the product's current critical user paths, not as a regression suite enumerating every system behavior.
