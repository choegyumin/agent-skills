# Enforcing Architecture Rules

Use this file when the user wants approved architecture rules enforced through ESLint, CI, import boundary checks, or similar automation.

Do not choose architecture here. Use the approved project architecture as the source of truth. If real directory roles and dependency directions are not established, return to `brownfield.md` or `greenfield.md` first.

## Default Tool

Use `eslint-plugin-boundaries` unless the project already uses another suitable tool or the user selects one.

Before editing:

- Identify the project's linter or boundary-enforcement package and its installed version.
- Check the current official documentation or Context7 for setup instructions applicable to the selected tool and installed version. Configuration differs across ESLint, Oxlint, other tools, and package versions.
- Add `eslint-plugin-boundaries` with the project package manager if it is selected and not installed.
- Preserve the project's lint runner and configuration style. Adapt the reference syntax to the selected tool and installed version instead of silently upgrading or replacing them.

## Reference Flat Config

This complete example targets ESLint v10 and `eslint-plugin-boundaries` v7.2. It shows all Greenfield layer roles while representing each Data role as one file for a compact reference. It assumes each element role groups code into child namespaces. Replace it with the approved project paths, grouping convention, and dependency directions. Omit unselected roles and map generated OpenAPI paths when generation is selected.

```js
import { posix as path } from "node:path";

import boundaries from "eslint-plugin-boundaries";

/**
 * @typedef {"element" | "file"} BoundaryKind
 * @typedef {string} BoundaryType
 * @typedef {"internal" | "child" | "parent" | "descendant" | "ancestor" | "sibling" | "uncle" | "nephew"} BoundaryRelationship
 * @typedef {object} BoundaryLayer
 * @property {BoundaryKind} kind
 * @property {BoundaryType} type
 * @property {string} pattern
 * @property {BoundaryRelationship[]} [relationships]
 * @property {BoundaryType[]} dependencies
 */

/** @type {BoundaryLayer[]} */
const boundaryLayers = [
  {
    kind: "element",
    type: "end-user:page",
    pattern: "src/pages",
    relationships: ["internal"],
    dependencies: ["end-user:widget", "domain:part", "domain:feature", "shared:ui", "shared:util", "data:adapter", "data:endpoint", "data:contract", "data:schema"],
  },
  {
    kind: "element",
    type: "end-user:widget",
    pattern: "src/widgets",
    relationships: ["internal", "sibling"],
    dependencies: ["domain:part", "domain:feature", "shared:ui", "shared:util", "data:adapter", "data:endpoint", "data:contract", "data:schema"],
  },
  {
    kind: "element",
    type: "domain:part",
    pattern: "src/parts",
    relationships: ["internal", "sibling"],
    dependencies: ["domain:feature", "shared:ui", "shared:util", "data:contract", "data:schema"],
  },
  {
    kind: "element",
    type: "domain:feature",
    pattern: "src/features",
    relationships: ["internal", "sibling"],
    dependencies: ["shared:ui", "shared:util", "data:contract", "data:schema"],
  },
  {
    kind: "element",
    type: "shared:ui",
    pattern: "src/ui",
    relationships: ["internal", "sibling"],
    dependencies: ["shared:util"],
  },
  {
    kind: "element",
    type: "shared:util",
    pattern: "src/utils",
    relationships: ["internal", "sibling", "child", "descendant"],
    dependencies: [],
  },
  {
    kind: "file",
    type: "data:adapter",
    pattern: "src/data/adapters.ts",
    dependencies: ["data:endpoint", "data:contract", "data:schema"],
  },
  {
    kind: "file",
    type: "data:endpoint",
    pattern: "src/data/endpoints.ts",
    dependencies: ["data:schema"],
  },
  {
    kind: "file",
    type: "data:contract",
    pattern: "src/data/contracts.ts",
    dependencies: ["data:schema"],
  },
  {
    kind: "file",
    type: "data:schema",
    pattern: "src/data/schemas.ts",
    dependencies: [],
  },
];
const boundaryKinds = Object.fromEntries(boundaryLayers.map(({ kind, type }) => [type, kind]));

export default [
  {
    ...boundaries.configs.recommended,
    files: ["src/**/*.{js,jsx,ts,tsx}"],
    plugins: { boundaries },
    settings: {
      ...boundaries.configs.recommended.settings,
      "boundaries/elements-single-match": false,
      "boundaries/elements": boundaryLayers
        .filter(({ kind }) => kind === "element")
        .flatMap(({ type, pattern }) => [
          { type, partialMatch: false, pattern: path.join(pattern, "*") },
          { type, partialMatch: false, pattern: path.join(pattern, "**") },
        ]),
      "boundaries/files": boundaryLayers
        .filter(({ kind }) => kind === "file")
        .map(({ type, pattern }) => ({ category: type, pattern })),
    },
    rules: {
      ...boundaries.configs.recommended.rules,
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          checkAllOrigins: false,
          checkInternals: boundaryLayers
            .filter(({ kind }) => kind === "element")
            .some(({ relationships = [] }) => !relationships.includes("internal")),
          policies: boundaryLayers.flatMap(
            ({ kind, type, relationships = [], dependencies: rawDependencies }) => {
              const elementDependencies = rawDependencies.filter((dependency) => boundaryKinds[dependency] === "element");
              const fileDependencies = rawDependencies.filter((dependency) => boundaryKinds[dependency] === "file");
              const dependencies = [
                ...(elementDependencies.length > 0 ? [{ element: { type: elementDependencies } }] : []),
                ...(fileDependencies.length > 0 ? [{ file: { categories: { anyOf: fileDependencies } } }] : []),
              ];

              const from = kind === "element"
                ? { element: { type } }
                : { file: { categories: type } };

              return [
                // Relationships Policy
                kind === "element" && {
                  from,
                  allow: {
                    to: { element: { type } },
                    dependency: { relationship: { to: relationships } },
                  },
                },
                // Dependencies Policy
                dependencies.length > 0 && {
                  from,
                  allow: { to: dependencies },
                },
              ].filter(Boolean);
            },
          ),
        },
      ],
    },
  },
];
```

## Adaptation Rules

- Map each approved role to `<abstract-layer>:<project-role>`, such as `domain:feature`, and keep its `kind`, pattern, allowed dependency types, and namespace relationships in one boundary entry.
- For element entries, use `path.join(pattern, "*")` to create child namespace elements and `path.join(pattern, "**")` to supply their shared parent. Keep `"boundaries/elements-single-match": false` so both descriptors participate in the element hierarchy.
- For file entries, use the exact pattern in `boundaries/files`; do not append element wildcards. Source and target permissions use file categories instead of element types.
- Use `relationships: ["internal"]` when only imports within the same namespace are allowed, or add `"sibling"` when namespaces of the same role may import each other. Internal imports are checked only when at least one element boundary omits `"internal"`. The shared-parent descriptor also classifies files directly under the pattern as one directory-level element.
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
