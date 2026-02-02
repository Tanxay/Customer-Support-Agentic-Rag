import requests
import json

try:
    print("Sending request to http://localhost:8000/query...")
    response = requests.post("http://localhost:8000/query", json={"question": "What does a blinking amber light mean?"})
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
