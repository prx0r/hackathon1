"""MCP tool definitions for Research CI.

Register these as MCP tools so AI agents can verify their
conclusions through the Alien/OpenAIRE MCP connector.
"""

MCP_TOOLS = [
    {
        "name": "patala_verify_analysis",
        "description": (
            "Verify whether conclusions derived from OpenAIRE data are "
            "still current. Returns impact report and proof obligations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis_id": {
                    "type": "string",
                    "description": "The tracked analysis ID to verify",
                },
            },
            "required": ["analysis_id"],
        },
    },
    {
        "name": "patala_track_query",
        "description": (
            "Register an OpenAIRE query for continuous tracking. "
            "Returns tracked analysis ID."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "OpenAIRE search query",
                },
                "entity_type": {
                    "type": "string",
                    "default": "research-products",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "patala_add_claim",
        "description": (
            "Add a research conclusion with dependencies to a tracked analysis."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis_id": {"type": "string"},
                "claim_text": {"type": "string"},
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dependencies like 'entity:openaire:xxx' or 'relation:src:predicate:tgt'",
                },
            },
            "required": ["analysis_id", "claim_text"],
        },
    },
    {
        "name": "patala_check_obligations",
        "description": (
            "List open proof obligations for a tracked analysis."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis_id": {"type": "string"},
            },
            "required": ["analysis_id"],
        },
    },
]
