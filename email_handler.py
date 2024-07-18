import os

import dotenv

from database import Session, engine
from models.email import Base
from services.data_service import EmailDataLayer
from services.email_service import EmailService
from strategies.email_provider_strategy import GoogleFetchEmails

dotenv.load_dotenv()

if __name__ == "__main__":
    # Create the tables for first time
    Base.metadata.create_all(engine)

    # Instantiate the GoogleEmailProvider with credentials path
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_FILE_LOCATION", None)

    if not credentials_path:
        raise ValueError(
            (
                "Credentials path not found. ",
                "Please set CREDENTIALS_PATH environment variable with the path to the google credentials file.",
            )
        )

    google_fetch_email_provider = GoogleFetchEmails(credentials_path)

    # Instantiate EmailService with GoogleEmailProvider
    email_service = EmailService(google_fetch_email_provider)

    email_message_list = email_service.fetch_emails()

    # Instantiate EmailDataLayer
    email_data_layer = EmailDataLayer(Session)
    email_data_layer.add_bulk_emails(email_message_list)
