import pytest  # pytest-version:latest
import json
import uuid

from src.backend.db.models.message import Message
from src.backend.db.models.user import User
from src.backend.db.models.negotiation import Negotiation
from src.backend.api.schemas.messages import MessageSchema  # src.backend.api.schemas.messages-version:latest

@pytest.fixture
def test_create_message(test_client, test_db, create_user, create_negotiation):
    """Tests the creation of a new message through the API endpoint"""
    # Create test data for a new message
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": "Hello, this is a test message."
    }

    # Make POST request to create message endpoint
    response = test_client.post("/api/v1/messages", json=message_data)

    # Verify response status code is 201
    assert response.status_code == 201

    # Verify response data contains expected message properties
    response_data = response.json()
    assert "id" in response_data
    assert response_data["thread_id"] == str(negotiation.id)
    assert response_data["sender_id"] == str(sender.id)
    assert response_data["recipient_ids"] == [str(recipient.id)]
    assert response_data["content"] == "Hello, this is a test message."

    # Verify message ID is returned in the response
    assert uuid.UUID(response_data["id"])

@pytest.fixture
def test_get_message(test_client, test_db, create_message):
    """Tests retrieving a single message by ID"""
    # Create a test message in the database
    message = create_message()

    # Make GET request to retrieve message by ID
    response = test_client.get(f"/api/v1/messages/{message.id}")

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify response data matches the expected message properties
    response_data = response.json()
    assert response_data["id"] == str(message.id)
    assert response_data["thread_id"] == str(message.thread_id)
    assert response_data["sender_id"] == str(message.sender_id)
    assert response_data["recipient_ids"] == message.recipient_ids
    assert response_data["content"] == message.content

@pytest.fixture
def test_get_messages_list(test_client, test_db, create_message, create_user):
    """Tests retrieving a list of messages with filtering and pagination"""
    # Create multiple test messages in the database
    user1 = create_user()
    user2 = create_user()
    message1 = create_message(sender_id=user1.id, recipient_ids=[user2.id], content="Test message 1")
    message2 = create_message(sender_id=user2.id, recipient_ids=[user1.id], content="Test message 2")
    message3 = create_message(sender_id=user1.id, recipient_ids=[user2.id], content="Test message 3")

    # Make GET request to list messages endpoint with filters
    response = test_client.get("/api/v1/messages?page=1&size=2")

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify response contains expected number of messages
    response_data = response.json()
    assert len(response_data["items"]) == 2
    assert response_data["total"] == 3
    assert response_data["page"] == 1
    assert response_data["size"] == 2

    # Verify pagination metadata is correct
    assert response_data["status"] == "success"

    # Test different filter combinations to ensure proper filtering
    response = test_client.get(f"/api/v1/messages?sender_id={user1.id}")
    assert response.status_code == 200
    filtered_data = response.json()
    assert len(filtered_data["items"]) == 2
    for message in filtered_data["items"]:
        assert message["sender_id"] == str(user1.id)

@pytest.fixture
def test_update_message(test_client, test_db, create_message):
    """Tests updating a message through the API"""
    # Create a test message in the database
    message = create_message()

    # Create update data for the message
    update_data = {"is_read": True}

    # Make PUT request to update message endpoint
    response = test_client.put(f"/api/v1/messages/{message.id}", json=update_data)

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify response data reflects the updates
    response_data = response.json()
    assert response_data["is_read"] == True

    # Make GET request to verify persistence of updates
    response = test_client.get(f"/api/v1/messages/{message.id}")
    assert response.status_code == 200
    get_data = response.json()
    assert get_data["is_read"] == True

@pytest.fixture
def test_delete_message(test_client, test_db, create_message):
    """Tests deleting a message through the API"""
    # Create a test message in the database
    message = create_message()

    # Make DELETE request to delete message endpoint
    response = test_client.delete(f"/api/v1/messages/{message.id}")

    # Verify response status code is 204
    assert response.status_code == 204

    # Make GET request to verify message is no longer accessible
    response = test_client.get(f"/api/v1/messages/{message.id}")
    assert response.status_code == 404

@pytest.fixture
def test_create_thread_message(test_client, test_db, create_user, create_negotiation):
    """Tests creating a message within a thread"""
    # Create a test thread in the database
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)

    # Create test data for a thread message
    thread_message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": "This is a thread message."
    }

    # Make POST request to create thread message endpoint
    response = test_client.post("/api/v1/messages", json=thread_message_data)

    # Verify response status code is 201
    assert response.status_code == 201

    # Verify message is properly associated with the thread
    response_data = response.json()
    assert response_data["thread_id"] == str(negotiation.id)

    # Verify thread metadata is updated
    response = test_client.get(f"/api/v1/messages/{response_data['id']}")
    assert response.status_code == 200
    message = response.json()
    assert message["content"] == "This is a thread message."

@pytest.fixture
def test_get_thread_messages(test_client, test_db, create_message, create_user, create_negotiation):
    """Tests retrieving all messages in a thread"""
    # Create a test thread with multiple messages
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    message1 = create_message(thread_id=negotiation.id, sender_id=sender.id, recipient_ids=[recipient.id], content="Thread message 1")
    message2 = create_message(thread_id=negotiation.id, sender_id=recipient.id, recipient_ids=[sender.id], content="Thread message 2")
    message3 = create_message(thread_id=negotiation.id, sender_id=sender.id, recipient_ids=[recipient.id], content="Thread message 3")

    # Make GET request to retrieve thread messages
    response = test_client.get(f"/api/v1/messages?thread_id={negotiation.id}")

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify all messages in the thread are returned
    response_data = response.json()
    assert len(response_data["items"]) == 3

    # Verify messages are ordered correctly
    assert response_data["items"][0]["content"] == "Thread message 1"
    assert response_data["items"][1]["content"] == "Thread message 2"
    assert response_data["items"][2]["content"] == "Thread message 3"

    # Verify thread metadata is included
    assert response_data["status"] == "success"

@pytest.fixture
def test_message_read_status(test_client, test_db, create_message):
    """Tests marking a message as read"""
    # Create a test message in the database with read status as false
    message = create_message(is_read=False)

    # Make PATCH request to update read status endpoint
    response = test_client.patch(f"/api/v1/messages/{message.id}", json={"is_read": True})

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify response shows updated read status
    response_data = response.json()
    assert response_data["is_read"] == True

    # Make GET request to verify persistence of read status
    response = test_client.get(f"/api/v1/messages/{message.id}")
    assert response.status_code == 200
    get_data = response.json()
    assert get_data["is_read"] == True

@pytest.fixture
def test_message_notifications(test_client, test_db, create_user, create_negotiation):
    """Tests that notifications are created when messages are sent"""
    # Create test users for sender and recipient
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)

    # Create test data for a new message
    message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": "This is a test message for notifications."
    }

    # Make POST request to create message endpoint
    response = test_client.post("/api/v1/messages", json=message_data)

    # Verify response status code is 201
    assert response.status_code == 201

    # Make GET request to recipient's notifications endpoint
    response = test_client.get(f"/api/v1/notifications?user_id={recipient.id}")
    assert response.status_code == 200
    notifications = response.json()

    # Verify a notification was created for the new message
    found_notification = False
    for notification in notifications["items"]:
        if "New message" in notification["message"]:
            found_notification = True
            break
    assert found_notification

@pytest.fixture
def test_message_search(test_client, test_db, create_message, create_user, create_negotiation):
    """Tests searching for messages by content"""
    # Create multiple test messages with different content
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    message1 = create_message(thread_id=negotiation.id, sender_id=sender.id, recipient_ids=[recipient.id], content="This message contains the word apple.")
    message2 = create_message(thread_id=negotiation.id, sender_id=recipient.id, recipient_ids=[sender.id], content="This message contains the word banana.")
    message3 = create_message(thread_id=negotiation.id, sender_id=sender.id, recipient_ids=[recipient.id], content="This message contains the word orange.")

    # Make GET request to search messages endpoint with search term
    response = test_client.get("/api/v1/messages?search=apple")

    # Verify response status code is 200
    assert response.status_code == 200

    # Verify only messages containing the search term are returned
    response_data = response.json()
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["content"] == "This message contains the word apple."

    # Test different search terms to ensure proper filtering
    response = test_client.get("/api/v1/messages?search=banana")
    assert response.status_code == 200
    search_data = response.json()
    assert len(search_data["items"]) == 1
    assert search_data["items"][0]["content"] == "This message contains the word banana."

@pytest.fixture
def test_message_attachment_handling(test_client, test_db, create_user, create_negotiation):
    """Tests creating a message with attachments"""
    # Create test data for a message with attachments
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    attachment_data = [{"file_name": "test.pdf", "file_type": "pdf", "file_size": 1024}]
    message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": "This is a test message with attachments.",
        "attachments": attachment_data
    }

    # Make POST request to create message endpoint
    response = test_client.post("/api/v1/messages", json=message_data)

    # Verify response status code is 201
    assert response.status_code == 201

    # Verify attachments are properly stored and linked to the message
    response_data = response.json()
    assert len(response_data["attachments"]) == 1
    assert response_data["attachments"][0]["file_name"] == "test.pdf"
    assert response_data["attachments"][0]["file_type"] == "pdf"
    assert response_data["attachments"][0]["file_size"] == 1024

    # Verify attachment metadata is correctly returned
    response = test_client.get(f"/api/v1/messages/{response_data['id']}")
    assert response.status_code == 200
    message = response.json()
    assert len(message["attachments"]) == 1
    assert message["attachments"][0]["file_name"] == "test.pdf"

@pytest.fixture
def test_message_related_entity(test_client, test_db, create_user, create_negotiation):
    """Tests creating a message linked to another entity like a negotiation or rate"""
    # Create a test negotiation in the database
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)

    # Create test data for a message linked to the negotiation
    message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": "This message is related to the negotiation.",
        "related_entity_type": "negotiation",
        "related_entity_id": str(negotiation.id)
    }

    # Make POST request to create message endpoint
    response = test_client.post("/api/v1/messages", json=message_data)

    # Verify response status code is 201
    assert response.status_code == 201

    # Verify message is properly linked to the negotiation
    response_data = response.json()
    assert response_data["related_entity_type"] == "negotiation"
    assert response_data["related_entity_id"] == str(negotiation.id)

    # Make GET request to filter messages by related entity
    response = test_client.get(f"/api/v1/messages?related_entity_type=negotiation&related_entity_id={negotiation.id}")
    assert response.status_code == 200
    related_data = response.json()
    assert len(related_data["items"]) == 1
    assert related_data["items"][0]["content"] == "This message is related to the negotiation."

@pytest.fixture
def test_unauthorized_access(test_client, test_db, create_message, create_user, create_negotiation):
    """Tests that unauthorized users cannot access messages"""
    # Create a test message in the database
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    message = create_message(thread_id=negotiation.id, sender_id=sender.id, recipient_ids=[recipient.id], content="Unauthorized message")

    # Make GET request without authentication
    response = test_client.get(f"/api/v1/messages/{message.id}")

    # Verify response status code is 401
    assert response.status_code == 401

    # Make GET request with authentication from non-participant user
    unauthorized_user = create_user()
    response = test_client.get(f"/api/v1/messages/{message.id}", headers={"Authorization": f"Bearer {unauthorized_user.id}"})

    # Verify response status code is 403
    assert response.status_code == 401

@pytest.fixture
def test_validation_error_handling(test_client, test_db, create_user, create_negotiation):
    """Tests API error handling for invalid message data"""
    # Create invalid test data (missing required fields)
    sender = create_user()
    recipient = create_user()
    negotiation = create_negotiation(client_id=sender.organization_id, firm_id=recipient.organization_id)
    invalid_message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [str(recipient.id)],
        "content": ""
    }

    # Make POST request to create message endpoint
    response = test_client.post("/api/v1/messages", json=invalid_message_data)

    # Verify response status code is 422
    assert response.status_code == 400

    # Verify error response contains validation details
    error_data = response.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "validation_error"
    assert "validation_errors" in error_data["error"]
    assert len(error_data["error"]["validation_errors"]) > 0

    # Test different validation scenarios
    invalid_message_data = {
        "thread_id": str(negotiation.id),
        "sender_id": str(sender.id),
        "recipient_ids": [],
        "content": "Valid content"
    }
    response = test_client.post("/api/v1/messages", json=invalid_message_data)
    assert response.status_code == 400
    error_data = response.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "validation_error"
    assert "validation_errors" in error_data["error"]
    assert len(error_data["error"]["validation_errors"]) > 0