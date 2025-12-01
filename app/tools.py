"""
Tools for the AI Booking Assistant (RAG, Booking, Email, Web Search).
"""
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Any
from db.database import Database
from app.config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM,
    WEB_SEARCH_ENABLED
)


class RAGTool:
    """Tool for RAG-based question answering."""
    
    def __init__(self, rag_pipeline):
        """Initialize RAG tool."""
        self.rag_pipeline = rag_pipeline
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute RAG search and return results."""
        try:
            context = self.rag_pipeline.get_relevant_context(query, k=3)
            return {
                "success": True,
                "context": context,
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "context": ""
            }


class BookingPersistenceTool:
    """Tool for persisting bookings to database."""
    
    def __init__(self, database: Database):
        """Initialize booking persistence tool."""
        self.db = database
    
    def execute(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist booking to database for Gates Of Argonath gaming convention."""
        try:
            # Validate required fields for convention tickets
            required_fields = ["name", "email", "phone", "ticket_type", "days_attending"]
            missing_fields = [field for field in required_fields if field not in booking_data]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, booking_data["email"]):
                return {
                    "success": False,
                    "error": "Invalid email format"
                }
            
            # Validate name is not a ticket type
            customer_name = booking_data["name"]
            ticket_type_values = ["vip", "standard", "student", "group", "premium", "deluxe", "basic", "regular"]
            if customer_name.lower() in ticket_type_values:
                return {
                    "success": False,
                    "error": "Invalid name provided. Please provide your actual name, not a ticket type."
                }
            
            # Create or get customer
            customer = self.db.create_customer(
                name=customer_name,
                email=booking_data["email"],
                phone=booking_data["phone"]
            )
            
            # Build notes with convention-specific information
            notes_parts = [
                f"Ticket Type: {booking_data['ticket_type'].title()}",
                f"Days Attending: {booking_data['days_attending']} day(s)"
            ]
            if booking_data.get("beta_tester") == "yes":
                notes_parts.append("Beta Tester: Yes (Government ID uploaded)")
            else:
                notes_parts.append("Beta Tester: No")
            
            notes = "\n".join(notes_parts)
            
            # Create booking - using convention start date and time as placeholder
            # The actual convention dates would be set by the convention organizers
            from datetime import datetime, timedelta
            convention_start = datetime.now() + timedelta(days=30)  # Example: 30 days from now
            convention_date = convention_start.strftime("%Y-%m-%d")
            convention_time = "09:00"  # Convention starts at 9 AM
            
            booking = self.db.create_booking(
                customer_id=customer.customer_id,
                booking_type=f"Gates Of Argonath - {booking_data['ticket_type'].title()}",
                date=convention_date,
                time=convention_time,
                status="confirmed",
                notes=notes
            )
            
            return {
                "success": True,
                "booking_id": booking.id,
                "customer_id": customer.customer_id,
                "message": f"Booking {booking.id} created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class EmailTool:
    """Tool for sending confirmation emails."""
    
    def execute(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """Send email using SMTP."""
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            return {
                "success": False,
                "error": "Email configuration not set. Please configure SMTP settings."
            }
        
        try:
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, to_email):
                return {
                    "success": False,
                    "error": "Invalid recipient email format"
                }
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = EMAIL_FROM or SMTP_USERNAME
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}"
            }
        except smtplib.SMTPAuthenticationError as e:
            # Provide helpful error message for Gmail authentication issues
            error_msg = str(e)
            if "535" in error_msg or "BadCredentials" in error_msg or "Username and Password not accepted" in error_msg:
                return {
                    "success": False,
                    "error": f"SMTP Authentication failed. For Gmail, you need to use an App Password instead of your regular password. Please:\n1. Enable 2-Factor Authentication on your Google account\n2. Generate an App Password at: https://myaccount.google.com/apppasswords\n3. Use that App Password in your secrets.toml file (SMTP_PASSWORD)"
                }
            return {
                "success": False,
                "error": f"SMTP Authentication error: {str(e)}"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error sending email: {str(e)}"
            }


class WebSearchTool:
    """Tool for web search using DuckDuckGo API."""
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Search the web using DuckDuckGo."""
        if not WEB_SEARCH_ENABLED:
            return {
                "success": False,
                "error": "Web search is disabled"
            }
        
        try:
            # Using DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            abstract = data.get("Abstract", "")
            abstract_text = data.get("AbstractText", "")
            answer = data.get("Answer", "")
            definition = data.get("Definition", "")
            
            # Combine results
            result_text = ""
            if answer:
                result_text = answer
            elif abstract_text:
                result_text = abstract_text
            elif definition:
                result_text = definition
            elif abstract:
                result_text = abstract
            else:
                result_text = "No relevant information found."
            
            return {
                "success": True,
                "query": query,
                "result": result_text,
                "source": "DuckDuckGo"
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Web search error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error performing web search: {str(e)}"
            }

