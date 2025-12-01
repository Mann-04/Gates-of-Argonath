"""
Booking flow management with intent detection and slot filling.
"""
import re
from typing import Dict, Optional, List, Any
from datetime import datetime


class BookingFlow:
    """Manages booking conversation flow and slot filling for Gates Of Argonath gaming convention."""
    
    REQUIRED_FIELDS = ["name", "email", "phone", "ticket_type", "days_attending"]
    
    def __init__(self):
        """Initialize booking flow."""
        self.current_booking: Dict[str, Any] = {}
        self.state: str = "idle"  # idle, collecting, confirming, completed
    
    def detect_intent(self, message: str) -> str:
        """Detect if user wants to book tickets for Gates Of Argonath gaming convention."""
        booking_keywords = [
            "book", "booking", "reserve", "reservation", "ticket", "tickets",
            "buy ticket", "purchase", "register", "sign up", "convention",
            "gates of argonath", "gaming convention", "attend", "join"
        ]
        message_lower = message.lower()
        
        for keyword in booking_keywords:
            if keyword in message_lower:
                return "booking"
        return "general"
    
    def extract_info(self, message: str) -> Dict[str, Optional[str]]:
        """Extract booking information from message."""
        extracted = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            extracted["email"] = emails[0]
        
        # Extract phone (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, message)
            if phones:
                extracted["phone"] = phones[0].replace("(", "").replace(")", "").replace("-", "").replace(".", "")
                break
        
        # Extract ticket type
        ticket_types = {
            "standard": ["standard", "regular", "basic", "general"],
            "vip": ["vip", "premium", "deluxe"],
            "student": ["student", "student discount"],
            "group": ["group", "group ticket", "bulk"]
        }
        message_lower = message.lower()
        for ticket_type, keywords in ticket_types.items():
            for keyword in keywords:
                if keyword in message_lower:
                    extracted["ticket_type"] = ticket_type
                    break
            if "ticket_type" in extracted:
                break
        
        # Extract days attending (1, 2, or 3 days)
        days_patterns = [
            r'\b(?:all|full|3|three)\s*(?:days?|day)\b',  # All 3 days
            r'\b(?:2|two|second)\s*(?:days?|day)\b',  # 2 days
            r'\b(?:1|one|first|single)\s*(?:days?|day)\b',  # 1 day
        ]
        for pattern in days_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                match = matches[0].lower()
                if "all" in match or "full" in match or "3" in match or "three" in match:
                    extracted["days_attending"] = "3"
                elif "2" in match or "two" in match or "second" in match:
                    extracted["days_attending"] = "2"
                else:
                    extracted["days_attending"] = "1"
                break
        
        # Extract beta tester interest
        beta_keywords = ["beta tester", "beta test", "unreleased games", "beta", "test games"]
        for keyword in beta_keywords:
            if keyword in message_lower:
                extracted["beta_tester"] = "yes"
                break
        
        # Extract name (look for "I'm", "my name is", etc.)
        # Exclude common ticket-related words to avoid false matches
        excluded_words = {"vip", "standard", "student", "group", "ticket", "tickets", "day", "days", "booking", "book"}
        
        name_patterns = [
            r'(?:my name is|i\'m|i am|call me|this is|name is|i\'m called)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'(?:name:)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'^([A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]+)*)(?:\s|$)',  # Name at start (at least 2 chars)
        ]
        for pattern in name_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                potential_name = matches[0].strip()
                # Validate it's not a ticket type or common word
                name_lower = potential_name.lower()
                name_words = name_lower.split()
                # Check if any word is in excluded list
                if not any(word in excluded_words for word in name_words) and len(potential_name) > 2:
                    extracted["name"] = potential_name
                    break
        
        return extracted
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        date_str_lower = date_str.lower().strip()
        
        # Handle relative dates
        today = datetime.now()
        if date_str_lower == "today":
            return today.strftime("%Y-%m-%d")
        elif date_str_lower == "tomorrow":
            from datetime import timedelta
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Handle MM/DD/YYYY or MM-DD-YYYY
        if "/" in date_str or "-" in date_str:
            parts = re.split(r'[/-]', date_str)
            if len(parts) == 3:
                if len(parts[2]) == 4:  # MM/DD/YYYY
                    month, day, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:  # DD/MM/YYYY (assuming)
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        return date_str  # Return as-is if can't parse
    
    def _normalize_time(self, time_str: str) -> str:
        """Normalize time to HH:MM format (24-hour)."""
        time_str = time_str.strip().upper()
        
        # Remove AM/PM and extract
        is_pm = "PM" in time_str
        is_am = "AM" in time_str
        time_str = re.sub(r'\s*(AM|PM)', '', time_str)
        
        if ":" in time_str:
            hour, minute = time_str.split(":")
            hour = int(hour)
            minute = int(minute)
        else:
            hour = int(time_str)
            minute = 0
        
        # Convert to 24-hour format
        if is_pm and hour != 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    
    def update_booking(self, extracted: Dict[str, Optional[str]]):
        """Update current booking with extracted information."""
        for key, value in extracted.items():
            if value:
                # Store required fields and optional fields like beta_tester
                if key in self.REQUIRED_FIELDS or key == "beta_tester":
                    # Additional validation: don't allow ticket_type values to be stored as name
                    if key == "name":
                        # Validate name is not a ticket type
                        ticket_type_values = ["vip", "standard", "student", "group", "premium", "deluxe", "basic", "regular"]
                        if value.lower() not in ticket_type_values:
                            self.current_booking[key] = value
                    else:
                        self.current_booking[key] = value
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        return [field for field in self.REQUIRED_FIELDS if field not in self.current_booking or not self.current_booking[field]]
    
    def get_booking_summary(self) -> str:
        """Get formatted summary of current booking."""
        summary_parts = []
        
        # Display fields in a logical order with proper labels
        field_labels = {
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "ticket_type": "Ticket Type",
            "days_attending": "Days Attending"
        }
        
        # Add required fields in order
        for field in self.REQUIRED_FIELDS:
            value = self.current_booking.get(field, "Not provided")
            
            # Special validation for name field - ensure it's not a ticket type
            if field == "name":
                ticket_type_values = ["vip", "standard", "student", "group", "premium", "deluxe", "basic", "regular"]
                if value.lower() in ticket_type_values or value == "Not provided":
                    value = "Not provided"
            
            field_name = field_labels.get(field, field.replace("_", " ").title())
            summary_parts.append(f"{field_name}: {value}")
        
        # Add beta tester info if available
        if "beta_tester" in self.current_booking:
            beta_status = "Yes" if self.current_booking["beta_tester"] == "yes" else "No"
            summary_parts.append(f"Beta Tester: {beta_status}")
        
        return "\n".join(summary_parts)
    
    def is_ready_for_confirmation(self) -> bool:
        """Check if all required fields are filled."""
        return len(self.get_missing_fields()) == 0
    
    def reset(self):
        """Reset booking flow."""
        self.current_booking = {}
        self.state = "idle"
    
    def get_next_question(self) -> str:
        """Get the next question to ask based on missing fields."""
        missing = self.get_missing_fields()
        if not missing:
            # Ask about beta tester if not asked yet
            if "beta_tester" not in self.current_booking:
                return "Would you like to be a beta tester for unreleased games? This requires uploading your government ID (PDF). Please answer 'yes' or 'no'."
            return ""
        
        field = missing[0]
        questions = {
            "name": "What is your full name? (Please provide your first and last name, e.g., 'John Doe' or 'My name is John Doe')",
            "email": "What is your email address?",
            "phone": "What is your phone number?",
            "ticket_type": "What type of ticket would you like? (Standard, VIP, Student, or Group)",
            "days_attending": "How many days would you like to attend? (1, 2, or all 3 days)"
        }
        return questions.get(field, f"Please provide {field.replace('_', ' ')}")

