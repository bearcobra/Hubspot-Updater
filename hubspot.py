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
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the HubSpot client with an access token
        
        Args:
            access_token: Your HubSpot private app access token (defaults to HUBSPOT_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN")
        
        if not self.access_token:
            raise ValueError("HubSpot access token required. Set HUBSPOT_ACCESS_TOKEN environment variable.")
        
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
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
        endpoint = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        data = {
            "properties": {
                "custom_lead_score_marshall": str(score_value)
            }
        }
        
        try:
            response = requests.patch(
                endpoint,
                headers=self.headers,
                json=data
            )
            
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


if __name__ == "__main__":
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
    
    args = parser.parse_args()
    
    try:
        client = HubSpotContactUpdater()
        result = client.update_lead_score(args.contact_id, args.score)
        
        if result["success"]:
            print(f"✓ Successfully updated contact {args.contact_id}")
            print(f"  Lead score set to: {args.score}")
            exit(0)
        else:
            print(f"✗ Failed to update contact {args.contact_id}")
            print(f"  Error: {result.get('message', result.get('error'))}")
            exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
