import requests
import json
from typing import List, Dict, Optional, Any
from agents import function_tool

@function_tool
def search_doctors(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Search for doctors in the NPPES NPI Registry.
    
    Args:
        first_name: The doctor's first name.
        last_name: The doctor's last name.
        city: The city where the doctor practices.
        state: The 2-letter state code (e.g., 'CA', 'NY').
        specialty: The taxonomy description (e.g., 'Cardiology', 'Dentist').
        limit: Number of results to return (default 10).
        
    Returns:
        A JSON string containing a list of matching doctors with their details.
    """
    base_url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "limit": limit,
        "pretty": "True"
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

    # Ensure at least one search criterion is provided to avoid generic broad searches if the API restricts them
    # Though NPPES allows NPI lookup, for this specific tool we are focusing on search by attributes.
    if not any([first_name, last_name, city, state, specialty]):
         return json.dumps({"error": "Please provide at least one search criterion (name, location, or specialty)."})

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
                
                # Find primary practice location
                practice_address = next((addr for addr in addresses if addr.get("address_purpose") == "LOCATION"), {})
                
                # Get primary taxonomy (specialty)
                primary_taxonomy = next((tax for tax in taxonomies if tax.get("primary") == True), {})
                
                doctor_info = {
                    "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                    "npi": item.get("number"),
                    "credential": basic.get("credential"),
                    "gender": basic.get("gender"),
                    "specialty": primary_taxonomy.get("desc"),
                    "address": {
                        "address_1": practice_address.get("address_1"),
                        "city": practice_address.get("city"),
                        "state": practice_address.get("state"),
                        "postal_code": practice_address.get("postal_code"),
                        "phone": practice_address.get("telephone_number")
                    }
                }
                results.append(doctor_info)
                
        return json.dumps(results, indent=2)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API request failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
