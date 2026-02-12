import requests

# List of endpoints to check
endpoints = [
    "http://swiftservicesenv1:9014/metastormorderpackageservice",
    "http://swiftservicesenv1:9014/orderpackageservice",
    "http://swiftservicesenv1:9014/customervuservice",
     "http://Swiftenv1/",
    "http://swiftservicesenv1:9000/",
    "http://swiftservicesenv1:9000/AdminSupportService.svc",
    "http://swiftservicesenv1:9000/swagger/ui/index",
    "http://swiftservicesenv1:9001/swagger/ui/index",
    "http://swiftservicesenv1:9002/swagger/index.html",
    "http://swiftservicesenv1:9003/swagger/index.html"
]

def check_endpoints(endpoints):
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} is running!")
            else:
                print(f"⚠️ {url} returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to reach {url}: {e}")

# Run the check
check_endpoints(endpoints)