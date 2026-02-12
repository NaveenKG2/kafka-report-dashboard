import requests

# List of endpoints to check
endpoints = [
    "http://swiftservicesenv4:9014/metastormorderpackageservice",
    "http://swiftservicesenv4:9014/orderpackageservice",
    "http://swiftservicesenv4:9014/customervuservice",
    "http://Swiftenv4/",
    "http://swiftservicesenv4:9000/",
    "http://swiftservicesenv4:9000/AdminSupportService.svc",
    "http://swiftservicesenv4:9000/swagger/ui/index",
    "http://swiftservicesenv4:9001/swagger/",
    "http://swiftservicesenv4:9002/swagger/index.html",
    "http://swiftservicesenv4:9003/swagger/index.html"
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