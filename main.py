import os
import json
import requests
from dotenv import load_dotenv
from utils.tables_list import tables as table_list

# --- Load environment variables ---
load_dotenv()

TABLEAU_SERVER = os.getenv("TABLEAU_SERVER", "").rstrip("/")
TABLEAU_SITE = os.getenv("TABLEAU_SITE")
PAT_NAME = os.getenv("TABLEAU_TOKEN_NAME")
PAT_SECRET = os.getenv("TABLEAU_TOKEN_PASS")

if not all([TABLEAU_SERVER, PAT_NAME, PAT_SECRET, TABLEAU_SITE is not None]):
    raise ValueError("❌ Missing one or more environment variables in .env")

print(f"📌 Querying tables: {table_list}")

# --- Authenticate with Tableau REST API ---
print("🔐 Signing in to Tableau Cloud...")

auth_url = f"{TABLEAU_SERVER}/api/3.21/auth/signin"
auth_payload = {
    "credentials": {
        "personalAccessTokenName": PAT_NAME,
        "personalAccessTokenSecret": PAT_SECRET,
        "site": {"contentUrl": TABLEAU_SITE or ""}
    }
}

auth_response = requests.post(auth_url, json=auth_payload, headers={"Accept": "application/json", "Content-Type": "application/json"})
if not auth_response.ok:
    print(f"Auth failed ({auth_response.status_code}): {auth_response.text}")
auth_response.raise_for_status()

# Parse JSON response to extract token and site ID
auth_data = auth_response.json()
token = auth_data['credentials']['token']
site_id = auth_data['credentials']['site']['id']

print(f"✅ Authenticated successfully (site ID: {site_id})")

# --- Prepare headers for GraphQL ---
graphql_url = f"{TABLEAU_SERVER}/api/metadata/graphql"
headers = {"X-Tableau-Auth": token, "Content-Type": "application/json"}

# --- Dictionary to store results ---
result_dict = {}

# --- Loop through each table and query dashboards ---
for table_name in table_list:
    query = f"""
    {{
      databaseTables (filter: {{name: "{table_name}"}}) {{
        name
        downstreamWorkbooks {{
          name
        }}
      }}
    }}
    """
    try:
        response = requests.post(graphql_url, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract dashboard names
        database_tables = data.get('data', {}).get('databaseTables', [])
        dashboard_names = []
        for table in database_tables:
            downstream = table.get('downstreamWorkbooks', [])
            for wb in downstream:
                dashboard_names.append(wb.get('name'))
        
        result_dict[table_name] = dashboard_names

    except Exception as e:
        print(f"❌ Error querying table {table_name}: {e}")
        result_dict[table_name] = []

# --- Print final dictionary ---
print("\n📊 Dashboards per table:")
print(json.dumps(result_dict, indent=2))

# --- Save result to JSON file in output/ directory ---
output_dir = "utils"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "dashboards_per_table.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result_dict, f, indent=2, ensure_ascii=False)

print(f"💾 Results saved to {output_file}")

# --- Sign out to revoke token ---
print("🚪 Signing out...")
try:
    requests.post(f"{TABLEAU_SERVER}/api/3.21/auth/signout", headers={"X-Tableau-Auth": token})
    print("👋 Signed out successfully.")
except Exception as e:
    print("⚠️ Error signing out:", e)
