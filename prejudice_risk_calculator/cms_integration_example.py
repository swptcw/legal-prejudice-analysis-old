#!/usr/bin/env python3
"""
Example Client Integration for Legal Prejudice Risk Calculator API
This demonstrates how a case management system might integrate with the API
"""

import requests
import json
import time
import argparse
import sys

# Configuration
API_BASE_URL = "http://localhost:5000/api/v1"
API_KEY = "TEST_API_KEY_12345"  # This would be securely stored in a real implementation

class PrejudiceRiskCalculatorClient:
    """Client for interacting with the Legal Prejudice Risk Calculator API"""
    
    def __init__(self, base_url=API_BASE_URL, api_key=API_KEY):
        """Initialize the client with base URL and API key"""
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"ApiKey {api_key}",
            "Content-Type": "application/json"
        }
    
    def check_api_status(self):
        """Check if the API is operational"""
        try:
            response = requests.get(f"{self.base_url}/status", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error checking API status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception checking API status: {str(e)}")
            return None
    
    def create_assessment(self, case_name, judge_name, assessor_name, case_id=None, cms_id=None):
        """Create a new prejudice risk assessment"""
        try:
            data = {
                "case_name": case_name,
                "judge_name": judge_name,
                "assessor_name": assessor_name
            }
            
            if case_id:
                data["case_id"] = case_id
            
            if cms_id:
                data["case_management_system_id"] = cms_id
            
            response = requests.post(f"{self.base_url}/assessments", headers=self.headers, json=data)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error creating assessment: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Exception creating assessment: {str(e)}")
            return None
    
    def get_assessment(self, assessment_id):
        """Retrieve an existing assessment"""
        try:
            response = requests.get(f"{self.base_url}/assessments/{assessment_id}", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving assessment: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception retrieving assessment: {str(e)}")
            return None
    
    def update_assessment(self, assessment_id, data):
        """Update an existing assessment"""
        try:
            response = requests.put(f"{self.base_url}/assessments/{assessment_id}", headers=self.headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error updating assessment: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception updating assessment: {str(e)}")
            return None
    
    def delete_assessment(self, assessment_id):
        """Delete an assessment"""
        try:
            response = requests.delete(f"{self.base_url}/assessments/{assessment_id}", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error deleting assessment: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception deleting assessment: {str(e)}")
            return None
    
    def get_factor_definitions(self):
        """Get all factor definitions"""
        try:
            response = requests.get(f"{self.base_url}/factor_definitions", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving factor definitions: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception retrieving factor definitions: {str(e)}")
            return None
    
    def submit_factor_ratings(self, assessment_id, factors):
        """Submit ratings for multiple factors"""
        try:
            data = {"factors": factors}
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/factors", headers=self.headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error submitting factor ratings: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception submitting factor ratings: {str(e)}")
            return None
    
    def get_factor_ratings(self, assessment_id):
        """Retrieve all factor ratings for an assessment"""
        try:
            response = requests.get(f"{self.base_url}/assessments/{assessment_id}/factors", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving factor ratings: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception retrieving factor ratings: {str(e)}")
            return None
    
    def calculate_results(self, assessment_id):
        """Calculate risk scores based on current factor ratings"""
        try:
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/calculate", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error calculating results: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception calculating results: {str(e)}")
            return None
    
    def link_to_case(self, assessment_id, cms_type, case_id, matter_id=None, sync_data=True):
        """Link assessment to a case in external case management system"""
        try:
            data = {
                "cms_type": cms_type,
                "case_id": case_id,
                "sync_data": sync_data
            }
            
            if matter_id:
                data["matter_id"] = matter_id
            
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/link", headers=self.headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error linking to case: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception linking to case: {str(e)}")
            return None

def print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def run_demo():
    """Run a demonstration of the API client"""
    client = PrejudiceRiskCalculatorClient()
    
    # Check API status
    print("Checking API status...")
    status = client.check_api_status()
    if not status:
        print("API is not available. Please make sure the API server is running.")
        return
    
    print("API is operational:")
    print_json(status)
    print("\n" + "-" * 80 + "\n")
    
    # Create a new assessment
    print("Creating a new assessment...")
    case_name = "Smith v. Jones Corporation"
    judge_name = "Hon. Robert Williams"
    assessor_name = "Jane Attorney"
    case_id = "CASE-2025-0429"
    cms_id = "CMS-12345"
    
    assessment = client.create_assessment(case_name, judge_name, assessor_name, case_id, cms_id)
    if not assessment:
        print("Failed to create assessment. Exiting.")
        return
    
    assessment_id = assessment["assessment_id"]
    print(f"Assessment created with ID: {assessment_id}")
    print_json(assessment)
    print("\n" + "-" * 80 + "\n")
    
    # Get factor definitions
    print("Getting factor definitions...")
    definitions = client.get_factor_definitions()
    if not definitions:
        print("Failed to get factor definitions. Exiting.")
        return
    
    print("Factor definitions retrieved:")
    # Just print the categories to avoid too much output
    for category, data in definitions.items():
        print(f"Category: {data['name']}")
        print(f"  Factors: {len(data['factors'])}")
    print("\n" + "-" * 80 + "\n")
    
    # Submit factor ratings
    print("Submitting factor ratings...")
    factors = [
        {
            "id": "financial-direct",
            "likelihood": 4,
            "impact": 5,
            "notes": "Judge owns 1000 shares in defendant corporation"
        },
        {
            "id": "relationship-family",
            "likelihood": 3,
            "impact": 4,
            "notes": "Judge's cousin is married to plaintiff's sister"
        },
        {
            "id": "statements-disparaging",
            "likelihood": 5,
            "impact": 3,
            "notes": "Judge made negative comments about plaintiff's counsel in previous case"
        },
        {
            "id": "historical-consistent",
            "likelihood": 4,
            "impact": 4,
            "notes": "Judge has ruled against similar plaintiffs in 8 out of 10 previous cases"
        }
    ]
    
    result = client.submit_factor_ratings(assessment_id, factors)
    if not result:
        print("Failed to submit factor ratings. Exiting.")
        return
    
    print("Factor ratings submitted:")
    print_json(result)
    print("\n" + "-" * 80 + "\n")
    
    # Get factor ratings
    print("Getting factor ratings...")
    ratings = client.get_factor_ratings(assessment_id)
    if not ratings:
        print("Failed to get factor ratings. Exiting.")
        return
    
    print("Factor ratings retrieved:")
    print_json(ratings)
    print("\n" + "-" * 80 + "\n")
    
    # Calculate results
    print("Calculating results...")
    results = client.calculate_results(assessment_id)
    if not results:
        print("Failed to calculate results. Exiting.")
        return
    
    print("Results calculated:")
    print_json(results)
    print("\n" + "-" * 80 + "\n")
    
    # Link to case management system
    print("Linking to case management system...")
    link_result = client.link_to_case(assessment_id, "Clio", "CLIO-12345", "MATTER-6789")
    if not link_result:
        print("Failed to link to case. Exiting.")
        return
    
    print("Linked to case management system:")
    print_json(link_result)
    print("\n" + "-" * 80 + "\n")
    
    # Get updated assessment
    print("Getting updated assessment...")
    updated_assessment = client.get_assessment(assessment_id)
    if not updated_assessment:
        print("Failed to get updated assessment. Exiting.")
        return
    
    print("Updated assessment retrieved:")
    print_json(updated_assessment)
    print("\n" + "-" * 80 + "\n")
    
    print("Demo completed successfully!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Legal Prejudice Risk Calculator API Client")
    parser.add_argument("--demo", action="store_true", help="Run the demo")
    parser.add_argument("--url", help="API base URL", default=API_BASE_URL)
    parser.add_argument("--key", help="API key", default=API_KEY)
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()