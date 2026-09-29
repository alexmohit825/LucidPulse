#!/usr/bin/env python3
"""
Lucid Motors Telemetry Extractor
Direct AWS Cognito & Mobile Gateway Telemetry Client for Lucid Air GT
"""

import sys
import json
import getpass
import urllib.request
import urllib.error

# Lucid Motors Mobile App Cognito Constants
COGNITO_ENDPOINT = "https://cognito-idp.us-east-1.amazonaws.com/"
CLIENT_ID = "2k74s1e56m7uv1f3n1b2723t4m"
API_BASE_URL = "https://api.lucidmotors.com/v1"

def authenticate_lucid(username, password):
    """Authenticate with Lucid AWS Cognito User Pool to obtain ID & Access Tokens."""
    payload = {
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": CLIENT_ID,
        "AuthParameters": {
            "USERNAME": username,
            "PASSWORD": password
        }
    }
    
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }

    req = urllib.request.Request(
        COGNITO_ENDPOINT, 
        data=json.dumps(payload).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            auth_res = data.get("AuthenticationResult", {})
            return {
                "id_token": auth_res.get("IdToken"),
                "access_token": auth_res.get("AccessToken"),
                "refresh_token": auth_res.get("RefreshToken"),
                "expires_in": auth_res.get("ExpiresIn")
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"\n❌ Lucid Authentication Failed (HTTP {e.code}): {error_body}")
        return None
    except Exception as e:
        print(f"\n❌ Network or Connection Error: {e}")
        return None

def fetch_vehicles(id_token):
    """Query user vehicle list from Lucid Cloud Gateway."""
    url = f"{API_BASE_URL}/users/me/vehicles"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Accept": "application/json",
        "User-Agent": "LucidApp/2.24.0 (iPhone; iOS 18.0; Scale/3.00)"
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"❌ Failed to fetch vehicle list (HTTP {e.code}): {e.read().decode('utf-8')}")
        return None

def fetch_vehicle_telemetry(vin, id_token):
    """Fetch real-time BMS and vehicle state for a specific VIN."""
    url = f"{API_BASE_URL}/vehicles/{vin}/state"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Accept": "application/json",
        "User-Agent": "LucidApp/2.24.0 (iPhone; iOS 18.0; Scale/3.00)"
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"❌ Failed to fetch telemetry for VIN {vin} (HTTP {e.code}): {e.read().decode('utf-8')}")
        return None

def main():
    print("==========================================================")
    print("   LUCID MOTORS LIVE VEHICLE TELEMETRY & BMS EXTRACTOR    ")
    print("==========================================================")
    
    email = input("\nEnter Lucid Account Email (e.g. alex.mohit@icloud.com): ").strip()
    if not email:
        print("Email is required.")
        return
        
    password = getpass.getpass("Enter Lucid Account Password: ").strip()
    if not password:
        print("Password is required.")
        return

    print("\n⏳ Authenticating with Lucid AWS Cognito...")
    tokens = authenticate_lucid(email, password)
    
    if not tokens or not tokens.get("id_token"):
        print("\nCould not retrieve access tokens. Please verify your credentials.")
        return

    print("✅ Authentication successful! Session token acquired.")
    print("⏳ Querying your Lucid vehicle portfolio...")
    
    vehicles = fetch_vehicles(tokens["id_token"])
    if not vehicles:
        print("No vehicles found on this account.")
        return

    print(f"✅ Found {len(vehicles)} vehicle(s) linked to your account.")
    
    # Process primary vehicle
    first_vehicle = vehicles[0] if isinstance(vehicles, list) else vehicles.get("vehicles", [{}])[0]
    vin = first_vehicle.get("vin") or first_vehicle.get("id")
    
    print(f"\n🚗 Targeting Vehicle VIN: {vin}")
    print("⏳ Extracting High-Voltage Battery BMS Telemetry...")
    
    telemetry = fetch_vehicle_telemetry(vin, tokens["id_token"])
    
    # Bundle output
    output_data = {
        "account_email": email,
        "vin": vin,
        "tokens": tokens,
        "vehicle_spec": first_vehicle,
        "telemetry": telemetry
    }
    
    output_file = "live_telemetry.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\n🎉 SUCCESS! Live vehicle telemetry saved to: {output_file}")
    print(f"👉 Refresh http://localhost:4200 to view your live Air GT battery health!")

if __name__ == "__main__":
    main()
