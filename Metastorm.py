import requests

# List of endpoints to check
endpoints = [
    "http://mbpm-env1.level3.com/metastormsso/",
"http://mbpm-env3.level3.com/metastormsso/",
"http://usodcwvjenk01/"
"https://api-test4.test.intranet:7443/",
"http://api.corp.intranet/"

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