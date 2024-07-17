import base64
import json
from typing import List

from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime

# Strategy interface or base class for email providers. We have to inherit the same class if we want to fetch email from outlook, yahoo, etc.
class EmailProviderStrategy:
    def fetch_emails(self) -> List[dict]:
        """
        Fetch emails from the email provider
        """
        pass

    def transform(self, message) -> dict:
        pass


# Concrete strategy for fetching emails from Google
class GoogleEmailProvider(EmailProviderStrategy):
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.service = self.create_service()

    def create_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/gmail.modify"],
        )
        credentials = flow.run_local_server(port=0)
        return discovery.build("gmail", "v1", credentials=credentials)

class GoogleFetchEmails(GoogleEmailProvider):
    def __init__(self, credentials_path):
        super().__init__(credentials_path)

    def fetch_emails(self) -> List[dict]:
        details = []
        messages = (
            self.service.users().messages().list(userId="me", maxResults=10).execute()
        )
        # print(messages)
        for message in messages.get("messages", []):
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message["id"])
                .execute()
            )

            details.append(self.transform(msg))

        return details

    def transform(self, message) -> dict:
        return {
            "subject": self.get_subject(message),
            "body": self.get_body(message),
            "sender_email": self.get_sender_email(message),
            "recipient_emails": self.get_recipient_emails(message),
            "received_at": self.get_received_at(message),
            "email_provider_id": message["id"],
            "labels": self.get_labels(message),
            "status": self.get_message_status(message),
        }

    def get_body(self, message):
        body= ""
        if "parts" in message["payload"]:
            # Iterate through the parts of the email
            for part in message["payload"]["parts"]:
                # Check for plain text or HTML parts
                if part["mimeType"] == "text/plain" or part["mimeType"] == "text/html":
                    # Decode the base64 encoded string
                    body += base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
                    break
        else:
            # For simple email messages, directly decode the body
            body = base64.urlsafe_b64decode(message["payload"]["body"]["data"]).decode(
                "utf-8"
            )
        
        return body

    def get_subject(self, message):
        for header in message["payload"]["headers"]:
            if header["name"] == "Subject":
                return header["value"]

        return None

    def get_sender_email(self, message):
        # Get sender email
        for header in message["payload"]["headers"]:
            if header["name"] == "From":
                return header["value"]

        return None

    def get_recipient_emails(self, message):
        # Get recipient emails
        for header in message["payload"]["headers"]:
            if header["name"] == "To":
                return header["value"]

        return None

    def get_received_at(self, message):
        # Get received time. We need to convert iso format to datetime object
        return datetime.fromtimestamp(int(message["internalDate"]) / 1000)

    def get_message_status(self, message):
        # Get message status
        if "UNREAD" in message["labelIds"]:
            return "unread"
        
        return "read"
    
    def get_labels(self, message):
        # Get labels
        return message["labelIds"]

class GoogleUpdateEmail(GoogleEmailProvider):
    def __init__(self, credentials_path):
        super().__init__(credentials_path)

    def update_email(self, id: str, modifications: dict):
        # Update email with labels
        self.service.users().messages().modify(
            userId="me", id=id, body=modifications
        ).execute()
    
    def mark_as_read(self, id: str):
        # Mark email as read
        self.update_email(id, {"removeLabelIds": ["UNREAD"]})
    
    def mark_as_unread(self, id: str):
        # Mark email as unread
        self.update_email(id, {"addLabelIds": ["UNREAD"]})
    
    def move_to_label(self, id: str, label: str):
        # Move email to a label and skip inbox
        self.update_email(id, {"addLabelIds": [label], "removeLabelIds": ["INBOX"]})