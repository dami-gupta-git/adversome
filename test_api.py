#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_endpoint(endpoint, expected_keys=None, description=""):
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS")
            print(f"Response Preview: {json.dumps(data, indent=2)[:500]}...")
            
            if expected_keys:
                for key in expected_keys:
                    if key in data:
                        print(f"✅ Found expected key: {key}")
                    else:
                        print(f"❌ Missing expected key: {key}")
        else:
            print(f"❌ FAILED - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"❌ GENERAL ERROR: {e}")

def run_comprehensive_tests():
    print("🧪 Starting Drug Data API Comprehensive Tests")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Root endpoint
    test_endpoint("/", ["message", "version", "endpoints"], "Root API Information")
    
    # Test 2: Comprehensive drug data - Aspirin
    test_endpoint("/api/compound/aspirin", 
                 ["query", "chembl_data", "adverse_events"], 
                 "Comprehensive Data - Aspirin by Name")
    
    # Test 3: Comprehensive drug data - ChEMBL ID
    test_endpoint("/api/compound/CHEMBL25?type=chembl_id", 
                 ["query", "chembl_data", "adverse_events"], 
                 "Comprehensive Data - Aspirin by ChEMBL ID")
    
    # Test 4: ChEMBL specific endpoint
    test_endpoint("/api/chembl/CHEMBL25", 
                 ["chembl_id", "smiles"], 
                 "ChEMBL Specific Data - Aspirin")
    
    # Test 5: Adverse events
    test_endpoint("/api/adverse-events/ibuprofen", 
                 ["drug_name", "adverse_events"], 
                 "FAERS Adverse Events - Ibuprofen")
    
    # Test 6: Search functionality
    test_endpoint("/api/search?q=metformin", 
                 ["query", "results"], 
                 "Search Compounds - Metformin")
    
    # Test 7: Rate limiting test
    print(f"\n{'='*50}")
    print("Testing Rate Limiting")
    print(f"{'='*50}")
    
    for i in range(12):  # Should hit rate limit
        try:
            response = requests.get(f"{BASE_URL}/api/search?q=test{i}", timeout=5)
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("✅ Rate limiting working correctly")
                break
        except:
            pass
        time.sleep(0.1)
    
    print(f"\n{'='*50}")
    print("🎉 API Testing Complete!")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_comprehensive_tests()