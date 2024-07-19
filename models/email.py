from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    sender_email = Column(String(255), nullable=False)
    recipient_emails = Column(String(255), nullable=True)
    email_provider_id = Column(String(60), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    labels = Column(ARRAY(String), nullable=True)
    received_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Email(sender='{self.sender_email}', recipient='{self.recipient_emails}', subject='{self.subject}')>"

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
