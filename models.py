from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'tickets'  # Название таблицы

    id = Column(Integer, primary_key=True, index=True)  # Первичный ключ
    title = Column(String, index=True)  # Название тикета
    description = Column(String, nullable=True)  # Описание тикета
    status = Column(String, default='open')  # Статус тикета, по умолчанию 'open'
