"""Agent prompts and templates."""

QUERY_PARSER_PROMPT = """You are a media content query parser. Parse the user query and extract:
1. Main intent (search, clip_generation, rights_check, brand_safety)
2. Entities (talent names, brands, actions)
3. Temporal requirements (duration, time range)
4. Rights requirements (territory, usage type)
5. Filters (content type, date range)

Return a structured JSON output.

Query: {query}
"""

QUERY_REWRITER_PROMPT = """Rewrite the following query to be more effective for semantic search.
Expand abbreviations, add relevant context, and reformulate for vector search.

Original: {query}
Rewritten: """

HYDE_PROMPT = """Generate a hypothetical ideal document that would perfectly answer this query.
This will be used for HYDE (Hypothetical Document Embeddings).

Query: {query}
Hypothetical document: """

RETRIEVAL_GRADER_PROMPT = """Grade the relevance of retrieved clips to the user query.
Return a score (0-1) and reason.

Query: {query}
Clip: {clip}
Score: """

BRAND_SAFETY_PROMPT = """Check if a clip passes brand safety requirements.

Clip: {clip_id}
Required brands: {required_brands}
Excluded brands: {excluded_brands}
Policy: {policy}

Result: """

RIGHTS_POLICY_PROMPT = """Check rights clearance for a clip.

Clip: {clip_id}
Territory: {territory}
Usage: {usage}
Duration: {duration}

Result: """

ANSWER_COMPOSER_PROMPT = """Compose a final answer from the validated evidence.

Query: {query}
Candidate clips: {clips}
Validation results: {validation}
Guardrail results: {guardrails}

Compose a response with:
1. Summary of findings
2. List of valid clips
3. Any human review flags
"""


def get_query_parser_prompt(query: str) -> str:
    return QUERY_PARSER_PROMPT.format(query=query)


def get_query_rewriter_prompt(query: str) -> str:
    return QUERY_REWRITER_PROMPT.format(query=query)


def get_hyde_prompt(query: str) -> str:
    return HYDE_PROMPT.format(query=query)


def get_retrieval_grader_prompt(query: str, clip: str) -> str:
    return RETRIEVAL_GRADER_PROMPT.format(query=query, clip=clip)


def get_brand_safety_prompt(clip_id: str, required_brands: list, excluded_brands: list, policy: str) -> str:
    return BRAND_SAFETY_PROMPT.format(
        clip_id=clip_id,
        required_brands=required_brands,
        excluded_brands=excluded_brands,
        policy=policy,
    )


def get_rights_policy_prompt(clip_id: str, territory: str, usage: str, duration: float) -> str:
    return RIGHTS_POLICY_PROMPT.format(
        clip_id=clip_id,
        territory=territory,
        usage=usage,
        duration=duration,
    )


def get_answer_composer_prompt(
    query: str, clips: list, validation: list, guardrails: dict
) -> str:
    return ANSWER_COMPOSER_PROMPT.format(
        query=query,
        clips=clips,
        validation=validation,
        guardrails=guardrails,
    )