# Good and Bad Tests

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

## Good Tests

### Integration style

Test through real interfaces, not mocks of internal parts.

```ts
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- Has one logical assertion per test; several assertion statements may establish it

## Bad Tests

### Horizontal slicing

Writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: they test the _shape_ of things rather than user-facing behavior, become insensitive to real changes, and commit to a test structure before the implementation is understood. Work in **vertical slices** instead: one test → one implementation → repeat. Each test is a **tracer bullet** that responds to what the previous cycle taught you.

### Mechanical regression tests

Continuing to assert behavior that a requirement change intentionally modified or removed. Update or delete those tests to match the new expected behavior. Write a regression test only when fixing a defect to prevent that defect from recurring.

### Implementation-detail tests

Mocking internal collaborators, testing private methods, or verifying through a side channel couples tests to internal structure. Querying the database instead of using the interface is one example. The tell: the test breaks when you refactor but behavior has not changed.

```ts
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```ts
// BAD: Bypasses the interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: Verifies through the interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

### Tautological tests

When an assertion recomputes the expected value the same way as the code (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, or a constant asserted equal to itself), the test passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, or the specification.

```ts
// BAD: Expected value is recomputed the way the code computes it
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, item) => sum + item.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: Expected value is an independent, known literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```
