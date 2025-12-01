"""
Database client for SQLite operations.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from db.models import Base, Customer, Booking
from typing import Optional, List, Dict


class Database:
    """SQLite database client."""
    
    def __init__(self, db_path: str = "bookings.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def create_customer(self, name: str, email: str, phone: str) -> Optional[Customer]:
        """Create a new customer."""
        session = self.get_session()
        try:
            # Check if customer already exists
            existing = session.query(Customer).filter_by(email=email).first()
            if existing:
                return existing
            
            customer = Customer(name=name, email=email, phone=phone)
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error creating customer: {str(e)}")
        finally:
            session.close()
    
    def create_booking(
        self,
        customer_id: int,
        booking_type: str,
        date: str,
        time: str,
        status: str = "confirmed",
        notes: Optional[str] = None
    ) -> Optional[Booking]:
        """Create a new booking."""
        session = self.get_session()
        try:
            booking = Booking(
                customer_id=customer_id,
                booking_type=booking_type,
                date=date,
                time=time,
                status=status,
                notes=notes
            )
            session.add(booking)
            session.commit()
            session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error creating booking: {str(e)}")
        finally:
            session.close()
    
    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings with customer information."""
        session = self.get_session()
        try:
            bookings = session.query(Booking).join(Customer).all()
            result = []
            for booking in bookings:
                result.append({
                    "id": booking.id,
                    "customer_name": booking.customer.name,
                    "customer_email": booking.customer.email,
                    "customer_phone": booking.customer.phone,
                    "booking_type": booking.booking_type,
                    "date": booking.date,
                    "time": booking.time,
                    "status": booking.status,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None,
                    "notes": booking.notes
                })
            return result
        except SQLAlchemyError as e:
            raise Exception(f"Database error fetching bookings: {str(e)}")
        finally:
            session.close()
    
    def search_bookings(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[Dict]:
        """Search bookings by name, email, or date."""
        session = self.get_session()
        try:
            query = session.query(Booking).join(Customer)
            
            if name:
                query = query.filter(Customer.name.ilike(f"%{name}%"))
            if email:
                query = query.filter(Customer.email.ilike(f"%{email}%"))
            if date:
                query = query.filter(Booking.date == date)
            
            bookings = query.all()
            result = []
            for booking in bookings:
                result.append({
                    "id": booking.id,
                    "customer_name": booking.customer.name,
                    "customer_email": booking.customer.email,
                    "customer_phone": booking.customer.phone,
                    "booking_type": booking.booking_type,
                    "date": booking.date,
                    "time": booking.time,
                    "status": booking.status,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None,
                    "notes": booking.notes
                })
            return result
        except SQLAlchemyError as e:
            raise Exception(f"Database error searching bookings: {str(e)}")
        finally:
            session.close()

