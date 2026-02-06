from fastmcp import FastMCP
import requests
import json
from typing import Optional

# Create an MCP server
mcp = FastMCP("DoctorListing")

from fastmcp import FastMCP
import requests
import json
from typing import Optional, List, Dict, Any

# Create an MCP server
mcp = FastMCP("DoctorListing")


@mcp.resource("ui://doctor_card")
def doctor_card_ui() -> str:
    """Returns the HTML UI for the doctor card."""
    try:
        with open("ui/doctor_card.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: UI Template not found</h1>"


@mcp.tool(description="Search for doctors in the NPPES NPI Registry.")
def search_doctors(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search for doctors in the NPPES NPI Registry.

    Args:
        first_name: The doctor's first name.
        last_name: The doctor's last name.
        city: The city where the doctor practices.
        state: The 2-letter state code (e.g., 'CA', 'NY').
        specialty: The taxonomy description (e.g., 'Cardiology', 'Dentist').
        limit: Number of results to return (default 10).
    """
    base_url = "https://npiregistry.cms.hhs.gov/api/"
    params = {"version": "2.1", "limit": limit, "pretty": "True"}

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

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        if "results" in data:
            for item in data["results"]:
                basic = item.get("basic", {})
                addresses = item.get("addresses", [])
                taxonomies = item.get("taxonomies", [])

                practice_address = next(
                    (
                        addr
                        for addr in addresses
                        if addr.get("address_purpose") == "LOCATION"
                    ),
                    {},
                )
                primary_taxonomy = next(
                    (tax for tax in taxonomies if tax.get("primary") == True), {}
                )

                doctor_info = {
                    "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                    "npi": item.get("number"),
                    "credential": basic.get("credential"),
                    "specialty": primary_taxonomy.get("desc"),
                    "city": practice_address.get("city"),
                    "state": practice_address.get("state"),
                    "phone": practice_address.get("telephone_number"),
                }
                results.append(doctor_info)

        return results
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    mcp.run()
