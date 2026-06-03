# Recommendations: make bad filter permalinks fail loudly

> Internal note for the API team — not part of the published docs site (not in
> `docs.json` navigation). Companion to the user-facing
> [Filtering & Permalinks](api-reference/filtering.mdx) guide.

## Problem

`locations`, `industries`, and `super_categories` on the list endpoints (`/deals`,
`/companies`, `/investors`, `/people`) and the alerts filters are free-text string
arrays. When a caller passes a value that isn't an exact permalink (e.g.
`"San Francisco"` instead of `"san-francisco-california"`, or `"fintech"` instead of
`"fintech-e067"`), the filter is **silently dropped** — the request returns zero or
unrelated results with a `200` and no indication anything was wrong. Callers have no
feedback loop, so they keep guessing.

Documentation (this PR) reduces the error rate but cannot eliminate silent failure.
The fixes below close it at the source.

## Recommendations, in priority order

### 1. Validate permalinks server-side → `422` with suggestions (highest leverage)

Reject unknown `locations` / `industries` / `super_categories` values with a `422`,
mirroring the pattern **already implemented for `financing_types`** — see
`docs/openapi/openapi-companies.yaml:1425-1443`, which returns:

```
Invalid financing type(s): series-a. Valid options are: SERIES_A, SERIES_B, SEED, ...
```

Apply the same shape to permalink filters, and use the existing fuzzy matcher that
powers `/industry/search` and `/location/search` to add a "did you mean":

```
Unknown industry permalink 'fintech'. Did you mean 'fintech-e067'?
```

Canonical source lists already exist:
- `features/alerts/dictionaries/industries.json` (789 industries)
- `features/alerts/dictionaries/super_categories.json` (49 super categories)
- `features/alerts/dictionaries/super_cat_mapping.json` (industry → super-category)
- location search index (backs `/location/search`)

This turns a silent miss into a self-correcting error. It is the single change that
would most reduce support load.

### 2. Echo applied filters in the response `meta`

Return what the server actually matched, e.g.:

```json
"meta": { "applied_filters": { "industries": ["fintech-e067"], "locations": [] } }
```

Even without (1), this lets callers see when a value was dropped. Cheap to add and
complementary to validation.

### 3. (Optional) Accept human labels and auto-resolve

Let the list endpoints accept a display name, resolve it via the same fuzzy index,
and report the chosen permalink in `meta.applied_filters`. Lower priority — only
worth doing after (1), and ambiguous names (multiple matches) still need a clear
rule (reject vs. pick best).

### 4. Unify the Alerts `financing_types` format

The Alerts API accepts human-readable round names (`["Series A", "Series B"]`) while
`/deals` and `/companies` use the canonical enum (`[{ "type": "SERIES_A" }]`). Same
concept, two formats — see `docs/openapi/openapi-alerts.yaml:677`. Either migrate
alerts to the enum or add a server-side normalizer that accepts both, then remove the
"known inconsistency" note from the docs.

## Once shipped

Update the user-facing docs to drop the "silently ignored" warnings on validated
fields, and update the verification step in the docs to assert a `422` (instead of
silent zero results) for a bogus permalink.
