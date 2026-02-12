import requests

# Splunk server details
splunk_url = "https://splunk-server:8089/services/search/jobs"
api_token = "YOUR_SPLUNK_API_TOKEN"

# Define available environments
environments = ["ENV1", "ENV2", "ENV3", "ENV4", "PROD"]

# Get user input for environment
print(f"Available environments: {', '.join(environments)}")
selected_env = input("Enter the environment you want to search logs for (ENV1, ENV2, ENV3, ENV4, PROD): ").strip().upper()

# Validate input
if selected_env not in environments:
    print("Invalid environment! Please restart and enter a valid environment.")
    exit()

# Get user input for Splunk query
user_query = input("Enter your Splunk search query: ")

# Construct the search query
search_query = f"search index={selected_env}_logs {user_query}"

# Define headers with API token
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/x-www-form-urlencoded"
}

# API request data
data = {
    "search": search_query,
    "output_mode": "json"
}

# Send the request
response = requests.post(splunk_url, headers=headers, data=data, verify=False)

# Process response
if response.status_code == 200:
    logs = response.json()
    print(f"Results for {selected_env} environment:\n", logs)
else:
    print(f"Error {response.status_code}: {response.text}")