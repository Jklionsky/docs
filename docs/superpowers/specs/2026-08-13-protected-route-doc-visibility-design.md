# Protected Route Documentation Visibility Design

## Goal

Make the person-email and alert route access requirements immediately visible on the Fundable API pricing page and on each protected endpoint page.

## Current state

The deployed OpenAPI descriptions correctly identify Pro+, Enterprise, and API eligibility, but Mintlify places that copy inside the generated operation content. The standalone `/usage` page was not updated in the prior release: it omits `/person/email` and incorrectly describes the two alert endpoints as credit-metered.

## Documentation changes

The `/usage` pricing table will add `GET /person/email` with a cost of five credits for a new email unlock and zero credits when the same user has already unlocked it. The alert rows will state that both alert endpoints consume zero credits.

A new “Plan-gated endpoints” section on `/usage` will state:

- `GET /person/email` is available on non-trial Pro+, Enterprise, and API plans.
- `GET /alerts` and `GET /alerts/configurations` are available on Pro+, Enterprise, and API plans.
- Alert requests do not consume credits.

The existing stale alert-credit bullets and examples on `/usage` will be replaced with the implemented behavior.

Each of these endpoint MDX pages will receive a prominent note directly after its frontmatter:

- `api-reference/people/email.mdx`: non-trial Pro+, Enterprise, or API requirement; five credits for a new unlock; zero credits for a repeat unlock by the same user.
- `api-reference/alerts/list.mdx`: Pro+, Enterprise, or API requirement; zero credits consumed.
- `api-reference/alerts/configurations.mdx`: Pro+, Enterprise, or API requirement; zero credits consumed.

The existing OpenAPI descriptions and 403 schemas remain unchanged because they already express the correct contract.

## Validation and release

Run `mintlify openapi-check openapi.json`, `mintlify validate`, and `git diff --check`. Inspect the generated route references to ensure all MDX pages still resolve. Commit and push the docs repository's `main` branch so Mintlify deploys the correction.
