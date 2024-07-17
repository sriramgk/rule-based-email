from strategies.email_provider_strategy import EmailProviderStrategy

class EmailService:
    def __init__(self, email_strategy: EmailProviderStrategy):
        self.email_strategy = email_strategy
    
    def fetch_emails(self):
        emails = self.email_strategy.fetch_emails()
        return emails
