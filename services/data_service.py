from sqlalchemy.orm import Session
from models.email import Email
from typing import List
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

class EmailDataLayer:
    def __init__(self, session: Session):
        self.session = session()
    
    def add_bulk_emails(self, emails: List[dict]):
        insert_stmt = pg_insert(Email).values(emails)
        update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['email_provider_id'],
            set_={
                'subject': insert_stmt.excluded.subject,
                'body': insert_stmt.excluded.body,
                'sender_email': insert_stmt.excluded.sender_email,
                'recipient_emails': insert_stmt.excluded.recipient_emails,
                'status': insert_stmt.excluded.status,
                'labels': insert_stmt.excluded.labels,
                'received_at': insert_stmt.excluded.received_at,
                'updated_at': func.now()
            }
        )
        self.session.execute(update_stmt)
        self.session.commit()

    def get_emails(self):
        return self.session.query(Email).all()