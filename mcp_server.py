import requests
from typing import Optional, List, Dict, Any

from mcp.server.mcpserver import MCPServer
from mcp.server.sse import serve_sse

# -------------------------------------------------
# Create MCP server (THIS is the correct way)
# -------------------------------------------------
mcp = MCPServer(
    name="DoctorListing",
    version="1.0.0",
    description="Search doctors using the NPPES NPI Registry",
)

# -------------------------------------------------
# Non-UI resource (REQUIRED for Scan Tools)
# -------------------------------------------------
@mcp.resource("doctorlisting://metadata")
def metadata() -> Dict[str, Any]:
    return {
        "name": "DoctorListing MCP",
        "version": "1.0.0",
        "description": "Search doctors using the NPPES NPI Registry",
    }

# -------------------------------------------------
# UI resource (OPTIONAL – can keep it)
# -------------------------------------------------
@mcp.resource("ui://doctor_card")
def doctor_card_ui() -> str:
    try:
        with open("ui/doctor_card.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: UI Template not found</h1>"

# -------------------------------------------------
# Tool: search_doctors
# -------------------------------------------------
@mcp.tool(
    name="search_doctors",
    description="Search for doctors in the NPPES NPI Registry",
)
def search_doctors(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:

    base_url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "limit": limit,
        "pretty": "True",
    }

    if first_name:
        params["first_name"] = first_name
        params["use_first_name_alias"] = "True"
    if last_name:
        params["last_name"] = last_name
    if city:
        params["city"] = city
    if state:
        params["state"] = state
    if specialty:
        params["taxonomy_description"] = specialty

    if not any([first_name, last_name, city, state, specialty]):
        return [{"error": "Please provide at least one search criterion."}]

    response = requests.get(base_url, params=params)
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
        primary_taxonomy = next(
            (t for t in taxonomies if t.get("primary")), {}
        )

        results.append({
            "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
            "npi": item.get("number"),
            "credential": basic.get("credential"),
            "specialty": primary_taxonomy.get("desc"),
            "city": practice_address.get("city"),
            "state": practice_address.get("state"),
            "phone": practice_address.get("telephone_number"),
        })

    return results


# -------------------------------------------------
# Run via SSE (REQUIRED)
# -------------------------------------------------
if __name__ == "__main__":
    serve_sse(
        mcp,
        host="0.0.0.0",
        port=8000,
        path="/sse",
    )
