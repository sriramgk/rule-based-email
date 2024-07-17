from strategies.email_provider_strategy import GoogleUpdateEmail
from services.email_service import EmailService
from services.data_service import EmailDataLayer
from database import Session
from services.email_rule_service import EmailRuleProcessor
import json
import os
import dotenv

dotenv.load_dotenv()

if __name__ == "__main__":

    # Get date from database
    email_obj = EmailDataLayer(Session)
    email_list = email_obj.get_emails()

    # Read the rule JSON file and convert into dictionary
    with open('./rules/email_rule.json') as file:
        rules_dict = json.load(file)

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_FILE_LOCATION", None)

    if not credentials_path:
        raise ValueError("Credentials path not found. Please set CREDENTIALS_PATH environment variable with the path to the google credentials file.")

    google_email_provider = GoogleUpdateEmail(credentials_path)

    rule_service = EmailRuleProcessor(rules_dict, google_email_provider)
    updated_email_list = rule_service.apply_rules_to_emails(email_list)

