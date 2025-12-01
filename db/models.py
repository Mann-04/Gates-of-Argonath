"""
Database models for the AI Booking Assistant.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customer(Base):
    """Customer model."""
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with bookings
    bookings = relationship("Booking", back_populates="customer")


class Booking(Base):
    """Booking model."""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    booking_type = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False)  # Stored as string YYYY-MM-DD
    time = Column(String(10), nullable=False)  # Stored as string HH:MM
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationship with customer
    customer = relationship("Customer", back_populates="bookings")

