"""
Chat logic with intent detection, memory management, and tool routing.
"""
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
import app.config as config
from app.booking_flow import BookingFlow
from app.tools import RAGTool, BookingPersistenceTool, EmailTool, WebSearchTool
from app.rag_pipeline import RAGPipeline


class ChatLogic:
    """Manages chat logic, memory, and tool routing."""
    
    def __init__(self, rag_pipeline: RAGPipeline, database):
        """Initialize chat logic."""
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.7
        )
        self.rag_pipeline = rag_pipeline
        self.database = database
        self.booking_flow = BookingFlow()
        
        # Initialize tools
        self.rag_tool = RAGTool(rag_pipeline)
        self.booking_tool = BookingPersistenceTool(database)
        self.email_tool = EmailTool()
        self.web_search_tool = WebSearchTool()
        
        # Memory (last 20-25 messages)
        self.memory: List[Dict[str, str]] = []
        self.max_memory = config.MAX_MEMORY_MESSAGES
    
    def add_to_memory(self, role: str, content: str):
        """Add message to memory."""
        self.memory.append({"role": role, "content": content})
        # Keep only last max_memory messages
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def get_memory_context(self) -> str:
        """Get formatted memory context."""
        if not self.memory:
            return ""
        context_parts = []
        for msg in self.memory[-10:]:  # Last 10 for context
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        return "\n".join(context_parts)
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and generate response."""
        # Add user message to memory
        self.add_to_memory("user", user_message)
        
        # Detect intent
        intent = self.booking_flow.detect_intent(user_message)
        
        # Handle booking intent
        if intent == "booking" or self.booking_flow.state != "idle":
            return self._handle_booking_flow(user_message)
        
        # Handle general queries (RAG or web search)
        return self._handle_general_query(user_message)
    
    def _handle_booking_flow(self, user_message: str) -> Dict[str, Any]:
        """Handle booking conversation flow for Gates Of Argonath gaming convention."""
        # Check for confirmation
        if self.booking_flow.state == "confirming":
            if any(word in user_message.lower() for word in ["yes", "confirm", "correct", "proceed"]):
                return self._confirm_booking()
            elif any(word in user_message.lower() for word in ["no", "cancel", "wrong", "change"]):
                self.booking_flow.reset()
                return {
                    "response": "I understand. Let's start over. How can I help you with Gates Of Argonath gaming convention?",
                    "tool_used": None,
                    "status": "info"
                }
        
        # Handle beta tester question response
        if "beta_tester" not in self.booking_flow.current_booking and self.booking_flow.is_ready_for_confirmation():
            user_lower = user_message.lower()
            if any(word in user_lower for word in ["yes", "yeah", "yep", "sure", "ok", "okay"]):
                self.booking_flow.current_booking["beta_tester"] = "yes"
                response = "Great! Please upload your government ID (PDF) in the 'Upload PDFs' section. Once uploaded, we'll process your beta tester application. Now, let me confirm your ticket booking details."
            elif any(word in user_lower for word in ["no", "nope", "nah", "not interested"]):
                self.booking_flow.current_booking["beta_tester"] = "no"
                response = "No problem! You can still enjoy all the convention activities. Now, let me confirm your ticket booking details."
            else:
                # Still asking about beta tester
                next_question = self.booking_flow.get_next_question()
                self.add_to_memory("assistant", next_question)
                return {
                    "response": next_question,
                    "tool_used": None,
                    "status": "info"
                }
            
            # After beta tester question, show confirmation
            if self.booking_flow.is_ready_for_confirmation():
                self.booking_flow.state = "confirming"
                summary = self.booking_flow.get_booking_summary()
                response = f"{response}\n\nI have the following details:\n\n{summary}\n\nIs this correct? Please reply 'yes' to confirm or 'no' to start over."
                self.add_to_memory("assistant", response)
                return {
                    "response": response,
                    "tool_used": None,
                    "status": "info"
                }
        
        # Start booking flow if needed
        if self.booking_flow.state == "idle":
            self.booking_flow.state = "collecting"
            self.booking_flow.current_booking = {}
            welcome_msg = "Welcome to Gates Of Argonath gaming convention! I'll help you book your tickets. This is a 3-day event where you can enjoy new games, LAN games, and learn about gaming technology."
            next_question = self.booking_flow.get_next_question()
            response = f"{welcome_msg}\n\n{next_question}"
            self.add_to_memory("assistant", response)
            return {
                "response": response,
                "tool_used": None,
                "status": "info"
            }
        
        # Extract information from message
        extracted = self.booking_flow.extract_info(user_message)
        self.booking_flow.update_booking(extracted)
        
        # Check if ready for confirmation
        if self.booking_flow.is_ready_for_confirmation() and "beta_tester" in self.booking_flow.current_booking:
            self.booking_flow.state = "confirming"
            summary = self.booking_flow.get_booking_summary()
            response = f"I have the following details:\n\n{summary}\n\nIs this correct? Please reply 'yes' to confirm or 'no' to start over."
            self.add_to_memory("assistant", response)
            return {
                "response": response,
                "tool_used": None,
                "status": "info"
            }
        
        # Ask for missing fields
        next_question = self.booking_flow.get_next_question()
        self.add_to_memory("assistant", next_question)
        return {
            "response": next_question,
            "tool_used": None,
            "status": "info"
        }
    
    def _confirm_booking(self) -> Dict[str, Any]:
        """Confirm and save booking."""
        booking_data = self.booking_flow.current_booking.copy()
        
        # Save to database
        booking_result = self.booking_tool.execute(booking_data)
        
        if not booking_result["success"]:
            error_msg = f"I encountered an error: {booking_result.get('error', 'Unknown error')}. Please try again."
            self.add_to_memory("assistant", error_msg)
            return {
                "response": error_msg,
                "tool_used": "booking",
                "status": "error"
            }
        
        booking_id = booking_result["booking_id"]
        
        # Send email
        email_body = self._generate_email_body(booking_data, booking_id)
        email_result = self.email_tool.execute(
            to_email=booking_data["email"],
            subject=f"Gates Of Argonath - Ticket Confirmation (ID: {booking_id})",
            body=email_body
        )
        
        # Prepare response
        beta_note = ""
        if booking_data.get("beta_tester") == "yes":
            beta_note = " Don't forget to upload your government ID (PDF) in the 'Upload PDFs' section to complete your beta tester registration!"
        
        if email_result["success"]:
            response = f"✅ Ticket booking confirmed! Your Ticket ID is {booking_id}. A confirmation email has been sent to {booking_data['email']}.{beta_note}"
            status = "success"
        else:
            response = f"✅ Ticket booking confirmed! Your Ticket ID is {booking_id}. However, I couldn't send the confirmation email ({email_result.get('error', 'Unknown error')}). Your booking has been saved.{beta_note}"
            status = "warning"
        
        self.add_to_memory("assistant", response)
        self.booking_flow.reset()
        
        return {
            "response": response,
            "tool_used": "booking",
            "booking_id": booking_id,
            "email_sent": email_result["success"],
            "status": status
        }
    
    def _generate_email_body(self, booking_data: Dict, booking_id: int) -> str:
        """Generate email body for Gates Of Argonath gaming convention ticket confirmation."""
        beta_tester_info = ""
        if booking_data.get("beta_tester") == "yes":
            beta_tester_info = "\nBeta Tester: Yes - Please ensure your government ID (PDF) is uploaded in the system."
        
        return f"""
Dear {booking_data['name']},

Thank you for booking your tickets to Gates Of Argonath gaming convention!

Here are your booking details:

Ticket ID: {booking_id}
Name: {booking_data['name']}
Email: {booking_data['email']}
Phone: {booking_data['phone']}
Ticket Type: {booking_data['ticket_type'].title()}
Days Attending: {booking_data['days_attending']} day(s){beta_tester_info}

Gates Of Argonath is a 3-day gaming convention where you can:
- Enjoy new games and LAN gaming sessions
- Learn about the latest technology in the gaming industry
- Connect with fellow gamers and industry professionals

We look forward to seeing you at the convention!

Best regards,
Gates Of Argonath Team
"""
    
    def _handle_general_query(self, user_message: str) -> Dict[str, Any]:
        """Handle general queries using RAG or web search."""
        # Check if RAG has content
        rag_result = self.rag_tool.execute(user_message)
        
        # Determine if we should use RAG or web search
        use_rag = rag_result["success"] and rag_result.get("context", "").strip()
        use_web_search = not use_rag or "search" in user_message.lower() or "latest" in user_message.lower()
        
        # Build prompt
        memory_context = self.get_memory_context()
        system_prompt = """You are a helpful AI assistant for Gates Of Argonath gaming convention. 
Gates Of Argonath is a 3-day gaming convention where attendees can:
- Enjoy new games and LAN gaming sessions
- Learn about technology used in the gaming industry
- Upload government IDs (PDFs) to become beta testers for unreleased games

Answer questions based on the provided context. If context is not available or the question is about current events, use web search results.
Be friendly, concise, and helpful. Always mention the convention name when relevant."""
        
        # Build the full prompt with context
        prompt_parts = [system_prompt]
        
        # Add memory context
        if memory_context:
            prompt_parts.append(f"Recent conversation context:\n{memory_context}")
        
        # Add RAG context if available
        if use_rag and rag_result.get("context"):
            prompt_parts.append(f"Relevant information from uploaded documents:\n{rag_result['context']}")
        
        # Add web search if needed
        web_result = None
        if use_web_search:
            web_result = self.web_search_tool.execute(user_message)
            if web_result.get("success") and web_result.get("result"):
                prompt_parts.append(f"Web search results:\n{web_result['result']}")
        
        # Add user message
        prompt_parts.append(f"\nUser question: {user_message}")
        
        # Combine all parts into a single prompt
        full_prompt = "\n\n".join(prompt_parts)
        
        # Generate response
        try:
            response = self.llm.invoke(full_prompt)
            
            # Extract content from LangChain response
            assistant_response = response.content if hasattr(response, 'content') else str(response)
            self.add_to_memory("assistant", assistant_response)
            
            tool_used = []
            if use_rag:
                tool_used.append("rag")
            if use_web_search and web_result and web_result.get("success"):
                tool_used.append("web_search")
            
            return {
                "response": assistant_response,
                "tool_used": ", ".join(tool_used) if tool_used else None,
                "status": "info"
            }
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try again."
            self.add_to_memory("assistant", error_msg)
            return {
                "response": error_msg,
                "tool_used": None,
                "status": "error"
            }
    
    def reset_conversation(self):
        """Reset conversation and memory."""
        self.memory = []
        self.booking_flow.reset()

