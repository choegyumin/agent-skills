# Enforcing Architecture Rules

Use this file when the user wants approved architecture rules enforced through ESLint, CI, import boundary checks, or similar automation.

Do not choose architecture here. Use the approved project architecture as the source of truth. If real directory roles and dependency directions are not established, return to `brownfield.md` or `greenfield.md` first.

## Default Tool

Use `eslint-plugin-boundaries` unless the project already uses another suitable tool or the user selects one.

Before editing:

- Add the plugin with the project package manager if it is not installed.
- Check the installed plugin version and current documentation.
- Preserve the project's lint runner and configuration style. Adapt the reference syntax to the installed version instead of silently upgrading it.

## Reference Flat Config

This complete example uses the current flat-config API and covers the maximum Greenfield structure from `greenfield-propose.md`: OpenAPI generation is not used and the API adapter pattern is selected. Replace it with the approved project directories and dependency directions. Omit unselected optional directories and map generated OpenAPI client/schema paths when generation is selected.

```js
import boundaries from "eslint-plugin-boundaries";

/**
 * @typedef {string} BoundaryElementType
 */

/** @type {Array<[type: BoundaryElementType, pattern: string]>} */
const boundaryElements = [
  ["end-user:pages", "src/pages"],
  ["end-user:widgets", "src/widgets"],
  ["domain:parts", "src/parts"],
  ["domain:features", "src/features"],
  ["shared:ui", "src/ui"],
  ["shared:utils", "src/utils"],
  ["data:endpoints", "src/data/endpoints"],
  ["data:schemas", "src/data/schemas"],
  ["data:adapters", "src/data/adapters"],
  ["data:contracts", "src/data/contracts"],
];

/** @type {Record<BoundaryElementType, BoundaryElementType[]>} */
const boundaryDependencies = {
  "end-user:pages": [
    "end-user:pages",
    "end-user:widgets",
    "domain:parts",
    "domain:features",
    "shared:ui",
    "shared:utils",
    "data:endpoints",
    "data:schemas",
    "data:adapters",
    "data:contracts",
  ],
  "end-user:widgets": [
    "end-user:widgets",
    "domain:parts",
    "domain:features",
    "shared:ui",
    "shared:utils",
    "data:endpoints",
    "data:schemas",
    "data:adapters",
    "data:contracts",
  ],
  "domain:parts": [
    "domain:parts",
    "domain:features",
    "shared:ui",
    "shared:utils",
    "data:schemas",
    "data:contracts",
  ],
  "domain:features": [
    "domain:features",
    "shared:ui",
    "shared:utils",
    "data:schemas",
    "data:contracts",
  ],
  "shared:ui": ["shared:ui", "shared:utils"],
  "shared:utils": ["shared:utils"],
  "data:endpoints": ["data:endpoints", "data:schemas"],
  "data:schemas": ["data:schemas"],
  "data:adapters": [
    "data:adapters",
    "data:endpoints",
    "data:schemas",
    "data:contracts",
  ],
  "data:contracts": ["data:contracts", "data:schemas"],
};

export default [
  {
    ...boundaries.configs.recommended,
    files: ["src/**/*.{js,jsx,ts,tsx}"],
    plugins: { boundaries },
    settings: {
      ...boundaries.configs.recommended.settings,
      "boundaries/elements": boundaryElements.map(([type, pattern]) => ({
        type,
        pattern,
        partialMatch: false,
      })),
    },
    rules: {
      ...boundaries.configs.recommended.rules,
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          checkAllOrigins: false,
          policies: Object.entries(boundaryDependencies).map(
            ([type, dependencies]) => ({
              from: { element: { type } },
              allow: { to: { element: { type: dependencies } } },
            }),
          ),
        },
      ],
    },
  },
];
```

## Adaptation Rules

- Map each approved directory role to `<abstract-layer>:<project-role>`, such as `domain:features`.
- Allow only approved complete element types and keep `default: "disallow"`; a shared layer prefix grants no dependency permission.
- Keep Data execution and contract paths separate when consumers have different permissions. Restrict which consumers may import generated OpenAPI paths; do not govern what generated files may import.
- Do not add unapproved directories or exceptions. When using another enforcement tool, preserve the same mapping and default-deny principle.

## Enforcement Limits

Enforce only statically detectable path, import, and package boundaries. Responsibility-level distinctions—such as whether UI is domain-aware or a hook hides orchestration—remain documentation and review rules. Passing lint does not prove architectural correctness.

## Verification

1. Run the project's existing lint command before editing to establish the baseline.
2. Apply the adapted configuration, then run the same command again.
3. When the project has a suitable fixture convention, verify one forbidden import is rejected and one approved import remains valid.

If architecture documentation exists, add only a short note that selected dependency rules are enforced by `eslint-plugin-boundaries`. Keep setup details in lint configuration.
