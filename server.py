from __future__ import annotations
import os

os.environ["MCP_TRUSTED_HOSTS"] = "*"
from typing import Any, Dict, List

import httpx
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# os.environ.setdefault("MCP_TRUSTED_HOSTS", "*")

# -------------------------------------------------
# MCP server
# -------------------------------------------------
mcp = FastMCP(
    name="doctorlisting",
    # description="Search doctors in the NPPES NPI Registry",
    stateless_http=True,
)

# -------------------------------------------------
# Tool input schema
# -------------------------------------------------
SEARCH_DOCTORS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "specialty": {"type": "string"},
        "limit": {"type": "integer"},
    },
    "additionalProperties": False,
}


# -------------------------------------------------
# Tool discovery (OFFICIAL STYLE)
# -------------------------------------------------
@mcp._mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="search_doctors",
            title="Search Doctors",
            description="Search for doctors in the NPPES NPI Registry",
            inputSchema=SEARCH_DOCTORS_SCHEMA,
            annotations={
                "readOnlyHint": True,
                "destructiveHint": False,
                "openWorldHint": False,
            },
        )
    ]


# -------------------------------------------------
# Resources
# -------------------------------------------------
@mcp._mcp_server.list_resources()
async def list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name="Doctor Card UI",
            title="Doctor Card UI",
            uri="mcp://doctor_card",
            description="HTML UI for displaying doctor information",
            mimeType="text/html",
        )
    ]


@mcp._mcp_server.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name="Doctor Card UI",
            title="Doctor Card UI",
            uriTemplate="mcp://doctor_card",
            description="HTML UI for displaying doctor information",
            mimeType="text/html",
        )
    ]


# -------------------------------------------------
# Resource handler (OFFICIAL STYLE)
# -------------------------------------------------
@mcp._mcp_server.read_resource()
async def read_resource(
    req: types.ReadResourceRequest,
) -> types.ServerResult:
    if str(req.params.uri) != "mcp://doctor_card":
        return types.ServerResult(types.ReadResourceResult(contents=[]))

    try:
        with open("ui/doctor_card.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "<h1>Error: UI Template not found</h1>"

    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri="mcp://doctor_card",
                    mimeType="text/html",
                    text=html,
                )
            ]
        )
    )


# -------------------------------------------------
# Tool handler (OFFICIAL STYLE)
# -------------------------------------------------
@mcp._mcp_server.call_tool()
async def call_tool(
    req: types.CallToolRequest,
) -> types.ServerResult:
    if req.params.name != "search_doctors":
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    args = req.params.arguments or {}

    params = {
        "version": "2.1",
        "pretty": "true",
        "limit": args.get("limit", 10),
    }

    for key in ["first_name", "last_name", "city", "state"]:
        if args.get(key):
            params[key] = args[key]

    if args.get("specialty"):
        params["taxonomy_description"] = args["specialty"]

    if not any(
        params.get(k)
        for k in ["first_name", "last_name", "city", "state", "taxonomy_description"]
    ):
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="Please provide at least one search criterion.",
                    )
                ],
                isError=True,
            )
        )

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://npiregistry.cms.hhs.gov/api/",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("results", []):
        basic = item.get("basic", {})
        addresses = item.get("addresses", [])
        taxonomies = item.get("taxonomies", [])

        practice_address = next(
            (a for a in addresses if a.get("address_purpose") == "LOCATION"), {}
        )
        primary_taxonomy = next((t for t in taxonomies if t.get("primary")), {})

        results.append(
            {
                "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                "npi": item.get("number"),
                "credential": basic.get("credential"),
                "specialty": primary_taxonomy.get("desc"),
                "city": practice_address.get("city"),
                "state": practice_address.get("state"),
                "phone": practice_address.get("telephone_number"),
            }
        )

    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Found {len(results)} doctors.",
                )
            ],
            structuredContent={"results": results},
        )
    )


# -------------------------------------------------
# HTTP app exposed to ChatGPT Native Apps
# -------------------------------------------------
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
