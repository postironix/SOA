from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import tasks_pb2
from datetime import datetime, timezone

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    
    title = Column(String(128), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    deadline = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    author_id = Column(Integer)

    def to_proto(self):
        return tasks_pb2.Task(
            id=self.id,
            title=self.title,
            description=self.description if self.description else "",
            deadline=self.deadline.strftime('%Y-%m-%d %H:%M:%S') if self.deadline else "",
            is_completed=self.is_completed,
            author_id=self.author_id
        )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_completed': self.is_completed,
            'author_id': self.author_id
        }