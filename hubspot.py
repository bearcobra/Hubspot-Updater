"""
HubSpot Contact Custom Field Updater
Updates the 'custom_lead_score_marshall' field for a given contact ID
"""

import requests
import json
from typing import Optional, Dict, Any
import os
from datetime import datetime


class HubSpotContactUpdater:
    """
    A class to handle HubSpot contact updates via the API
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the HubSpot client with an access token
        
        Args:
            access_token: Your HubSpot private app access token or API key
        """
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def update_lead_score(self, contact_id: str, score_value: float) -> Dict[str, Any]:
        """
        Update the custom_lead_score_marshall field for a specific contact
        
        Args:
            contact_id: The HubSpot contact ID
            score_value: The numeric value to set for the lead score
            
        Returns:
            Dict containing the API response or error information
        """
        # Construct the API endpoint
        endpoint = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        # Prepare the data payload
        data = {
            "properties": {
                "custom_lead_score_marshall": str(score_value)
            }
        }
        
        try:
            # Make the PATCH request to update the contact
            response = requests.patch(
                endpoint,
                headers=self.headers,
                json=data
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": f"Successfully updated contact {contact_id}",
                    "contact_id": result.get("id"),
                    "updated_properties": result.get("properties", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update contact",
                    "status_code": response.status_code,
                    "error": response.text,
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_contact(self, contact_id: str, properties: Optional[list] = None) -> Dict[str, Any]:
        """
        Retrieve a contact's information from HubSpot
        
        Args:
            contact_id: The HubSpot contact ID
            properties: List of properties to retrieve (optional)
            
        Returns:
            Dict containing the contact information or error
        """
        endpoint = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        # Add properties to query if specified
        params = {}
        if properties:
            params["properties"] = ",".join(properties)
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_update_lead_scores(self, contact_scores: Dict[str, float]) -> list:
        """
        Update lead scores for multiple contacts
        
        Args:
            contact_scores: Dictionary mapping contact IDs to score values
            
        Returns:
            List of update results for each contact
        """
        results = []
        for contact_id, score in contact_scores.items():
            result = self.update_lead_score(contact_id, score)
            results.append({
                "contact_id": contact_id,
                "score": score,
                "result": result
            })
        return results


def main():
    """
    Example usage of the HubSpot Contact Updater
    """
    
    # Configuration
    # Option 1: Set your access token directly (not recommended for production)
    # ACCESS_TOKEN = "your-hubspot-access-token-here"
    
    # Option 2: Get from environment variable (recommended)
    ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
    
    if not ACCESS_TOKEN:
        print("Error: Please set your HubSpot access token")
        print("You can set it as an environment variable: export HUBSPOT_ACCESS_TOKEN='your-token'")
        return
    
    # Initialize the client
    client = HubSpotContactUpdater(ACCESS_TOKEN)
    
    # Example 1: Update a single contact's lead score
    print("=" * 50)
    print("Example 1: Updating single contact")
    print("=" * 50)
    
    contact_id = "12345"  # Replace with actual contact ID
    lead_score = 85.5
    
    result = client.update_lead_score(contact_id, lead_score)
    
    if result["success"]:
        print(f"✓ Successfully updated contact {contact_id}")
        print(f"  Lead score set to: {lead_score}")
    else:
        print(f"✗ Failed to update contact {contact_id}")
        print(f"  Error: {result.get('message', result.get('error'))}")
    
    print(json.dumps(result, indent=2))
    
    # Example 2: Get contact information to verify the update
    print("\n" + "=" * 50)
    print("Example 2: Retrieving contact to verify update")
    print("=" * 50)
    
    contact_info = client.get_contact(
        contact_id, 
        properties=["custom_lead_score_marshall", "email", "firstname", "lastname"]
    )
    
    if contact_info["success"]:
        print(f"✓ Retrieved contact information")
        properties = contact_info["data"].get("properties", {})
        print(f"  Lead Score: {properties.get('custom_lead_score_marshall', 'Not set')}")
        print(f"  Email: {properties.get('email', 'Not set')}")
        print(f"  Name: {properties.get('firstname', '')} {properties.get('lastname', '')}")
    else:
        print(f"✗ Failed to retrieve contact")
        print(f"  Error: {contact_info.get('error')}")
    
    # Example 3: Batch update multiple contacts
    print("\n" + "=" * 50)
    print("Example 3: Batch updating multiple contacts")
    print("=" * 50)
    
    contacts_to_update = {
        "12345": 85.5,
        "12346": 92.0,
        "12347": 73.25
    }
    
    batch_results = client.batch_update_lead_scores(contacts_to_update)
    
    for result in batch_results:
        status = "✓" if result["result"]["success"] else "✗"
        print(f"{status} Contact {result['contact_id']}: Score set to {result['score']}")


def cli_interface():
    """
    Command-line interface for updating a single contact
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update HubSpot contact's custom lead score"
    )
    parser.add_argument(
        "contact_id",
        help="The HubSpot contact ID to update"
    )
    parser.add_argument(
        "score",
        type=float,
        help="The lead score value to set"
    )
    parser.add_argument(
        "--token",
        help="HubSpot access token (or set HUBSPOT_ACCESS_TOKEN env variable)",
        default=os.getenv("HUBSPOT_ACCESS_TOKEN")
    )
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: HubSpot access token required")
        print("Provide via --token flag or HUBSPOT_ACCESS_TOKEN environment variable")
        return 1
    
    # Initialize client and update the contact
    client = HubSpotContactUpdater(args.token)
    result = client.update_lead_score(args.contact_id, args.score)
    
    if result["success"]:
        print(f"✓ Successfully updated contact {args.contact_id}")
        print(f"  Lead score set to: {args.score}")
        return 0
    else:
        print(f"✗ Failed to update contact {args.contact_id}")
        print(f"  Error: {result.get('message', result.get('error'))}")
        return 1


if __name__ == "__main__":
    # Uncomment the line below to use the CLI interface
    # exit(cli_interface())
    
    # Or run the examples
    main()
