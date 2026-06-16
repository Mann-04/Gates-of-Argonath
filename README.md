# AI Booking Assistant

An AI-driven booking assistant chatbot that supports RAG (Retrieval-Augmented Generation) using user-uploaded PDFs, conversational booking flow, and email confirmations.

*Use it now: https://gates-of-argonath-j7jlwclgkb5bk5cznqh9gu.streamlit.app/*

## Features

- 🤖 **RAG Chatbot**: Upload PDFs and ask questions based on their content
- 📅 **Conversational Booking**: Natural language booking with intent detection and slot filling
- 📧 **Email Confirmations**: Automatic email confirmations after booking
- 🔍 **Web Search**: Optional web search tool for current information
- 📊 **Admin Dashboard**: View and search all bookings
- 💾 **SQLite Database**: Persistent storage for customers and bookings
- 🧠 **Short-term Memory**: Maintains conversation context (last 20-25 messages)

## Project Structure

```
pillar_of_men/
├── app/
│   ├── main.py              # Streamlit entry point
│   ├── chat_logic.py        # Intent detection + memory management
│   ├── booking_flow.py      # Slot filling + confirmation
│   ├── rag_pipeline.py      # PDF ingest + embeddings
│   ├── tools.py            # RAG/DB/email/search tools
│   ├── admin_dashboard.py   # Admin UI
│   └── config.py            # Configuration
├── db/
│   ├── database.py          # SQLite client
│   └── models.py            # Database models
├── docs/                    # Sample PDFs
├── streamlit/
│   └── secrets.toml         # Secrets configuration
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pillar_of_men
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables or secrets:

Create `streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-openai-api-key"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
EMAIL_FROM = "your-email@gmail.com"
```

Or set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export EMAIL_FROM="your-email@gmail.com"
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app/main.py
```

2. Navigate to the app in your browser (usually `http://localhost:8501`)

3. **Upload PDFs**: Go to "Upload PDFs" page and upload one or more PDF files

4. **Chat**: Use the "Chat" page to:
   - Ask questions about uploaded PDFs (RAG)
   - Make bookings by saying things like "I want to book 3 tickets for the convention"
   - Search the web for information

5. **Admin Dashboard**: View all bookings, search by name/email/date, and see statistics

## Booking Flow

1. User expresses booking intent (e.g., "I want to book a ticket")
2. Bot detects intent and starts collecting information:
   - Customer name
   - Email
   - Phone
   - Booking/service type
   - Preferred date (YYYY-MM-DD)
   - Preferred time (HH:MM, 24-hour format)
3. Bot extracts information from user messages automatically
4. Bot asks for missing fields
5. Bot summarizes all details and asks for confirmation
6. On confirmation:
   - Booking is saved to SQLite database
   - Confirmation email is sent
   - Booking ID is provided

## Database Schema

### customers
- `customer_id` (PK)
- `name`
- `email` (unique)
- `phone`
- `created_at`

### bookings
- `id` (PK)
- `customer_id` (FK)
- `booking_type`
- `date`
- `time`
- `status`
- `created_at`
- `notes`

## Tools Implemented

1. **RAG Tool**: Retrieves relevant information from uploaded PDFs
2. **Booking Persistence Tool**: Saves bookings to SQLite database
3. **Email Tool**: Sends confirmation emails via SMTP
4. **Web Search Tool**: Searches the web using DuckDuckGo API

## Configuration

Edit `app/config.py` to customize:
- Chunk size and overlap for RAG
- Embedding and LLM models
- Memory size
- Vector store path
- Database path

## Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Set secrets in Streamlit Cloud dashboard:
   - `OPENAI_API_KEY`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `EMAIL_FROM`
5. Deploy!

## Error Handling

The application handles:
- Invalid email/date/time formats
- Missing PDFs or extraction errors
- Database connection/insert errors
- Email delivery failures
- API errors

All errors are displayed with friendly messages to the user.

## Requirements

- Python 3.8+
- OpenAI API key
- SMTP credentials (for email functionality)
- Internet connection (for web search)

## License

This project is created for educational purposes.

## Author

AI Booking Assistant - AI Engineer Assignment

