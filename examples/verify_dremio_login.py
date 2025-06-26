import os
import requests
import asyncio
import datetime
import time
from dremioai.api.transport import DremioAsyncHttpClient

# Get credentials from environment variables
username = os.environ.get("username")
password = os.environ.get("password")
uri = os.environ.get("dremio_uri", "https://dremio.dev.serraict.me")

if not username or not password:
    raise ValueError("username and password environment variables must be set")

login_url = f"{uri}/apiv2/login"


def analyze_token_expiration(response_data):
    """Analyze token expiration from Dremio login response"""
    token = response_data["token"]
    expires_timestamp_ms = response_data.get("expires")

    print("\n🔑 Token Analysis:")
    print(f"   Token: {token}")
    user_info = (
        f"   User: {response_data.get('userName')} " f"({response_data.get('email')})"
    )
    print(user_info)
    print(f"   Admin: {response_data.get('admin')}")
    print(f"   Dremio Version: {response_data.get('version')}")

    if expires_timestamp_ms:
        # Convert from milliseconds to seconds
        expires_timestamp = expires_timestamp_ms / 1000
        current_timestamp = time.time()

        current_time = datetime.datetime.fromtimestamp(current_timestamp)
        expires_time = datetime.datetime.fromtimestamp(expires_timestamp)
        time_remaining = expires_time - current_time

        hours_remaining = (expires_timestamp - current_timestamp) / 3600
        days_remaining = hours_remaining / 24

        print("\n⏰ Token Expiration:")
        print(f"   Current time: {current_time}")
        print(f"   Expires at: {expires_time}")
        print(f"   Time remaining: {time_remaining}")
        print(f"   Hours remaining: {hours_remaining:.1f}")
        print(f"   Days remaining: {days_remaining:.1f}")

        # Warning if token expires soon
        if hours_remaining < 24:
            print("   ⚠️  WARNING: Token expires in less than 24 hours!")
        elif hours_remaining < 72:
            print("   ⚠️  NOTE: Token expires in less than 3 days")
        else:
            print("   ✅ Token has good validity period")
    else:
        print("   ❓ No expiration timestamp found in response")

    return token


def get_token():
    resp = requests.post(
        login_url, json={"userName": username, "password": password}, timeout=10
    )
    resp.raise_for_status()
    response_data = resp.json()
    print(f"Full login response: {response_data}")
    return analyze_token_expiration(response_data)


token = get_token()
print(f"Successfully retrieved token: {token}")


async def verify_token_with_mcp_client():
    client = DremioAsyncHttpClient(uri=uri, pat=token)
    # Try the actual endpoints that the MCP server uses for open source Dremio
    endpoints_to_try = [
        "/api/v3/catalog",  # Core catalog browsing
        "/api/v3/search",  # Semantic search
        "/apiv2/jobs",  # Jobs endpoint (that we know works)
    ]

    for endpoint in endpoints_to_try:
        try:
            result = await client.get(endpoint)
            print(f"✅ Success with {endpoint}:")
            print(f"Response type: {type(result)}")
            if isinstance(result, dict) and len(str(result)) > 500:
                print(f"Large response (truncated): {str(result)[:500]}...")
            else:
                print(result)
            print("-" * 50)
        except Exception as e:
            print(f"❌ Failed with {endpoint}: {e}")

    # Test SQL execution (this requires a POST request)
    try:
        print("Testing SQL execution...")
        # This would normally be done via the sql.py module, but let's test
        # the endpoint
        sql_payload = {"sql": "SELECT 1 as test_column"}
        result = await client.post("/api/v3/sql", body=sql_payload)
        print(f"✅ SQL execution successful: {result}")
    except Exception as e:
        print(f"❌ SQL execution failed: {e}")

    print(
        "\n🎯 Summary: These are the core endpoints the Dremio MCP server "
        "needs for your open source setup"
    )


if __name__ == "__main__":
    try:
        asyncio.run(verify_token_with_mcp_client())
    except Exception as e:
        print(f"Token test with DremioAsyncHttpClient failed: {e}")
