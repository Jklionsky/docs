# Protected Route Documentation Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make person-email pricing and all three protected-route plan requirements immediately visible in Mintlify.

**Architecture:** Update the standalone pricing source and add static Mintlify notes to the three thin OpenAPI route pages. Leave the already-correct OpenAPI operations and generated bundles unchanged, validate the complete docs tree, then push docs `main`.

**Tech Stack:** MDX, Mintlify, OpenAPI 3.0.

## Global Constraints

- `GET /person/email` is available on non-trial Pro+, Enterprise, and API plans.
- A new person-email unlock costs five credits; a repeat unlock by the same user costs zero credits.
- `GET /alerts` and `GET /alerts/configurations` are available on Pro+, Enterprise, and API plans and consume zero credits.
- Do not edit generated OpenAPI JSON because the OpenAPI contract is already correct.

---

### Task 1: Correct pricing and access guidance

**Files:**
- Modify: `usage.mdx`

**Interfaces:**
- Consumes: the deployed access and credit behavior
- Produces: the canonical human-readable pricing and plan-gating summary

- [ ] **Step 1: Capture the stale-content failure**

Run:

```bash
rg -n 'person/email|1 credit/deal|Alert results.*cost|Plan-gated endpoints' usage.mdx
```

Expected: no person-email or plan-gated match, with stale alert-credit matches present.

- [ ] **Step 2: Update the endpoint table and access section**

Add this table row after `GET /person`:

```mdx
| `GET /person/email` | Unlock a verified email for a person | 5 credits/new unlock; repeat unlocks free |
```

Set both alert rows to `Free`, replace the stale alert-credit paragraph with a “Plan-gated endpoints” section, and replace the stale How Credits Work bullets with:

```mdx
- **Person email unlocks** (`/person/email`) cost **5 credits for a new unlock** and **0 credits when the same user already unlocked that email**.
- **Alert endpoints** (`/alerts`, `/alerts/configurations`) consume **0 credits**.
```

- [ ] **Step 3: Verify corrected usage copy**

Run:

```bash
rg -n 'person/email|Plan-gated endpoints|consume \*\*0 credits\*\*|1 credit/deal|Alert results.*cost' usage.mdx
```

Expected: corrected email/access/zero-credit matches and no stale alert-credit matches.

### Task 2: Add prominent route-page notes

**Files:**
- Modify: `api-reference/people/email.mdx`
- Modify: `api-reference/alerts/list.mdx`
- Modify: `api-reference/alerts/configurations.mdx`

**Interfaces:**
- Consumes: each route page's existing `openapi:` frontmatter
- Produces: visible plan and credit callouts above generated operation content

- [ ] **Step 1: Add the person-email note**

Append after frontmatter:

```mdx
<Note>
  **Plan requirement:** Available on non-trial Pro+, Enterprise, and API plans.
  A new email unlock costs **5 credits**; requesting an email the same user has
  already unlocked costs **0 credits**.
</Note>
```

- [ ] **Step 2: Add the alert notes**

Append after frontmatter in both alert pages:

```mdx
<Note>
  **Plan requirement:** Available on Pro+, Enterprise, and API plans. This
  endpoint does not consume credits.
</Note>
```

- [ ] **Step 3: Verify all three notes and route references**

Run:

```bash
rg -n 'Plan requirement|openapi:' api-reference/people/email.mdx api-reference/alerts/list.mdx api-reference/alerts/configurations.mdx
```

Expected: one route reference and one plan note in each file.

### Task 3: Validate and deploy Mintlify

**Files:**
- Test: `usage.mdx`
- Test: `api-reference/people/email.mdx`
- Test: `api-reference/alerts/list.mdx`
- Test: `api-reference/alerts/configurations.mdx`

**Interfaces:**
- Consumes: Tasks 1–2
- Produces: a validated docs commit deployed from `main`

- [ ] **Step 1: Verify all endpoint pages resolve**

Run the route-reference Python check from the `fundable-openapi-docs` skill.

Expected: `All endpoint pages resolve`.

- [ ] **Step 2: Validate OpenAPI and Mintlify**

Run:

```bash
mintlify openapi-check openapi.json
mintlify validate
git diff --check
```

Expected: all commands pass.

- [ ] **Step 3: Commit and deploy**

Run:

```bash
git add usage.mdx api-reference/people/email.mdx api-reference/alerts/list.mdx api-reference/alerts/configurations.mdx docs/superpowers/plans/2026-08-13-protected-route-doc-visibility.md
git commit -m "clarify protected API pricing and access"
git push origin main
```

Expected: docs `main` advances and Mintlify begins deployment.
