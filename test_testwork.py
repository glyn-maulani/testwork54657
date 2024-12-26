from fastapi.testclient import TestClient
from testwork import app

client = TestClient(app)

def test_create_transaction():
    headers = {"api-key": "secure_api_key"}
    transaction_data = {
        "transaction_id": "test_1",
        "user_id": "user_1",
        "amount": 100.0,
        "currency": "USD",
        "timestamp": "2024-12-12T12:00:00"
    }
    response = client.post(
        "/transactions",
        headers=headers,
        json=transaction_data
    )
    print(response.json())
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Transaction received"
    assert "task_id" in response_data

def test_delete_transactions():
    headers = {"api-key": "secure_api_key"}
    response = client.delete(
        "/transactions",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "All transactions deleted"

def test_get_statistics():
    headers = {"api-key": "secure_api_key"}
    client.post(
        "/transactions",
        headers=headers,
        json={
            "transaction_id": "test_2",
            "user_id": "user_2",
            "amount": 200.0,
            "currency": "USD",
            "timestamp": "2024-12-14T17:25:00"
        }
    )
    client.post(
        "/transactions",
        headers=headers,
        json={
            "transaction_id": "test_3",
            "user_id": "user_3",
            "amount": 300.0,
            "currency": "USD",
            "timestamp": "2024-12-12T12:00:00"
        }
    )

    # Get statistics
    response = client.get(
        "/statistics",
        headers=headers
    )
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_transactions"] == 2
    assert stats["average_transaction_amount"] == 250.0
    assert len(stats["top_transactions"]) == 2
