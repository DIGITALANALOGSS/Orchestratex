import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Helper functions
async def get_token(username: str, password: str) -> str:
    """Get authentication token."""
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

async def create_user(username: str, email: str, password: str) -> dict:
    """Create a new user."""
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    return response.json()

async def create_profile(token: str, user_id: int) -> dict:
    """Create a user profile."""
    headers = {"Authorization": f"Bearer {token}"}
    profile_data = {
        "user_id": user_id,
        "learning_style": "visual",
        "preferred_modality": "interactive",
        "current_level": "beginner",
        "strengths": json.dumps(["quantum mechanics", "linear algebra"]),
        "gaps": json.dumps(["quantum algorithms", "quantum error correction"])
    }
    response = requests.post(f"{BASE_URL}/profiles/", headers=headers, json=profile_data)
    return response.json()

async def create_session(token: str, user_id: int) -> dict:
    """Create a learning session."""
    headers = {"Authorization": f"Bearer {token}"}
    session_data = {
        "user_id": user_id,
        "topic": "quantum computing basics",
        "engagement_score": 0.85,
        "progress_score": 0.6,
        "quantum_simulation": True
    }
    response = requests.post(f"{BASE_URL}/sessions/", headers=headers, json=session_data)
    return response.json()

async def create_quantum_state(token: str, user_id: int) -> dict:
    """Create a quantum state."""
    headers = {"Authorization": f"Bearer {token}"}
    state_data = {
        "user_id": user_id,
        "state_vector": json.dumps([0.5, 0.5, 0.5])
    }
    response = requests.post(f"{BASE_URL}/quantum/states/", headers=headers, json=state_data)
    return response.json()

async def teleport_quantum_state(token: str, source_id: int, target_id: int) -> dict:
    """Teleport a quantum state."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/quantum/states/teleport/",
        headers=headers,
        json={"source_id": source_id, "target_id": target_id}
    )
    return response.json()

async def measure_quantum_state(token: str, state_id: int) -> dict:
    """Measure a quantum state."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/quantum/states/measure/",
        headers=headers,
        json={"state_id": state_id}
    )
    return response.json()

async def main():
    print("\nCreating test user...")
    user = await create_user("test_user", "test@example.com", "password123")
    print("User created:", user)
    
    print("\nGetting authentication token...")
    token = await get_token("test_user", "password123")
    print("Token received")
    
    print("\nCreating profile...")
    profile = await create_profile(token, user["id"])
    print("Profile created:", profile)
    
    print("\nCreating learning session...")
    session = await create_session(token, user["id"])
    print("Session created:", session)
    
    print("\nCreating quantum state...")
    state = await create_quantum_state(token, user["id"])
    print("Quantum state created:", state)
    
    print("\nMeasuring quantum state...")
    measurement = await measure_quantum_state(token, state["id"])
    print("Measurement result:", measurement)
    
    print("\nCreating second quantum state...")
    state2 = await create_quantum_state(token, user["id"])
    print("Second state created:", state2)
    
    print("\nTeleporting quantum state...")
    teleport_result = await teleport_quantum_state(token, state["id"], state2["id"])
    print("Teleport result:", teleport_result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
