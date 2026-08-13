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

This complete example uses the current flat-config API and covers the maximum Greenfield structure from `greenfield-propose.md`: OpenAPI generation is not used and the API adapter pattern is selected. It assumes each directory role groups code into child namespaces. Replace it with the approved project directories, grouping convention, and dependency directions. Omit unselected optional directories and map generated OpenAPI client/schema paths when generation is selected.

```js
import boundaries from "eslint-plugin-boundaries";

/**
 * @typedef {string} BoundaryElementType
 * @typedef {"internal" | "child" | "parent" | "descendant" | "ancestor" | "sibling" | "uncle" | "nephew"} BoundaryRelationship
 * @typedef {object} BoundaryLayer
 * @property {BoundaryElementType} type
 * @property {string} pattern
 * @property {BoundaryRelationship[]} relationships
 * @property {BoundaryElementType[]} dependencies
 */

/** @type {BoundaryLayer[]} */
const boundaryLayers = [
  {
    type: "end-user:page",
    pattern: "src/pages/*",
    relationships: ["internal"],
    dependencies: ["end-user:widget", "domain:part", "domain:feature", "shared:ui", "shared:utility", "data:endpoint", "data:schema", "data:adapter", "data:contract"],
  },
  {
    type: "end-user:widget",
    pattern: "src/widgets/*",
    relationships: ["internal"],
    dependencies: ["domain:part", "domain:feature", "shared:ui", "shared:utility", "data:endpoint", "data:schema", "data:adapter", "data:contract"],
  },
  {
    type: "domain:part",
    pattern: "src/parts/*",
    relationships: ["internal", "sibling"],
    dependencies: ["domain:feature", "shared:ui", "shared:utility", "data:schema", "data:contract"],
  },
  {
    type: "domain:feature",
    pattern: "src/features/*",
    relationships: ["internal", "sibling"],
    dependencies: ["shared:ui", "shared:utility", "data:schema", "data:contract"],
  },
  {
    type: "shared:ui",
    pattern: "src/ui/*",
    relationships: ["internal", "sibling"],
    dependencies: ["shared:utility"],
  },
  {
    type: "shared:utility",
    pattern: "src/utils/*",
    relationships: ["internal", "sibling"],
    dependencies: [],
  },
  {
    type: "data:endpoint",
    pattern: "src/data/endpoints/*",
    relationships: ["internal", "sibling"],
    dependencies: ["data:schema"],
  },
  {
    type: "data:schema",
    pattern: "src/data/schemas/*",
    relationships: ["internal", "sibling"],
    dependencies: [],
  },
  {
    type: "data:adapter",
    pattern: "src/data/adapters/*",
    relationships: ["internal", "sibling"],
    dependencies: ["data:endpoint", "data:schema", "data:contract"],
  },
  {
    type: "data:contract",
    pattern: "src/data/contracts/*",
    relationships: ["internal", "sibling"],
    dependencies: ["data:schema"],
  },
];

export default [
  {
    ...boundaries.configs.recommended,
    files: ["src/**/*.{js,jsx,ts,tsx}"],
    plugins: { boundaries },
    settings: {
      ...boundaries.configs.recommended.settings,
      "boundaries/elements": boundaryLayers.map(({ type, pattern }) => ({
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
          policies: boundaryLayers.flatMap(
            ({ type, relationships, dependencies }) => {
              const relationshipPolicy = {
                from: { element: { type } },
                allow: {
                  to: { element: { type } },
                  dependency: { relationship: { to: relationships } },
                },
              };
              const dependencyPolicies =
                dependencies.length === 0
                  ? []
                  : [
                      {
                        from: { element: { type } },
                        allow: { to: { element: { type: dependencies } } },
                      },
                    ];

              return [relationshipPolicy, ...dependencyPolicies];
            },
          ),
        },
      ],
    },
  },
];
```

## Adaptation Rules

- Map each approved directory role to `<abstract-layer>:<project-role>`, such as `domain:feature`, and keep its pattern, allowed dependency types, and namespace relationships in one boundary entry.
- Model each child namespace as its own element. Use `relationships: ["internal"]` when only imports within the same namespace are allowed, or add `"sibling"` when namespaces of the same role may import each other. Adapt the pattern to the approved grouping convention when namespaces are not child directories.
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
