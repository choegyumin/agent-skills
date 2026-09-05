# Test Doubles

Use test doubles only at **system boundaries**:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Do not use test doubles for:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for test doubles

At system boundaries, design interfaces that are easy to replace with test doubles.

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```ts
// Easy to replace with a test double
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to replace with a test double
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```ts
// GOOD: Each function can be replaced independently
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch("/orders", { method: "POST", body: data }),
};

// BAD: The test double requires conditional logic
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means:

- Each test double returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint
