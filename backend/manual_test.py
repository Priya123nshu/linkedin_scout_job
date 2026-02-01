
import urllib.request
import json

def test():
    url = "http://localhost:8001/search"
    data = {"keywords": ["react"], "limit": 1}
    payload = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(
        url, 
        data=payload, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.status}")
            body = response.read()
            parsed = json.loads(body)
            print("Response structure:")
            print(json.dumps(parsed, indent=2))
    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
