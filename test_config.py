"""Test that API key configuration works correctly."""
import sys
import os

# Test without streamlit first
print("Testing API key configuration...")

# Check .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"1. .env file exists: {os.path.exists(env_path)}")

# Check secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
print(f"2. .streamlit/secrets.toml exists: {os.path.exists(secrets_path)}")

# Try to load from .env directly
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY=' in content:
            print("3. .env contains GOOGLE_API_KEY: Yes")
        else:
            print("3. .env contains GOOGLE_API_KEY: No")

# Now test the config module
from config import API_KEY, get_api_key

print(f"\n4. API_KEY loaded: {'Yes' if API_KEY and API_KEY != 'PASTE_YOUR_API_KEY_HERE' else 'No'}")
if API_KEY and len(API_KEY) > 10:
    print(f"5. API_KEY starts with: {API_KEY[:10]}...")
else:
    print(f"5. API_KEY value: {API_KEY}")

print("\n✅ Configuration test complete!")
