"""Models module."""

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, DeclarativeBase

# стандартная залупа
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    transcriptions = relationship("Transcription", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, ip_address=\"{self.ip_address}\")>"


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    language = Column(String)
    status = Column(String, nullable=False)
    text_content = Column(Text)
    result_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transcriptions")

    def __repr__(self):
        return f"<Transcription(id={self.id}, status=\"{self.status}\")>"
