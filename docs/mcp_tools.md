# Public Tool Registry Reference

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

The project uses an MCP-style registry abstraction. It is an internal typed
tool boundary, not a networked MCP server. Exactly three deterministic
retrieval tools are registered in the public application.

## `vector_search`

Scores local catalog metadata against a query and returns ranked candidate
records.

```json
{"query": "coffee commercial", "top_k": 10, "filters": {}}
```

## `bm25_search`

Performs lexical BM25-style matching over the same catalog.

```json
{"query": "coffee commercial", "top_k": 10}
```

## `rrf_fusion`

Combines multiple ranked lists using reciprocal rank fusion.

```json
{"result_sets": [[], []], "k": 60}
```

## Extension contract

Every tool derives from the documented base contract, declares a name,
description, and input schema, and returns serializable data. Additional vision,
audio, policy, output, or database tools are not included in the public
registry and must not be claimed as operative.

