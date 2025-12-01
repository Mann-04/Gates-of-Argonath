# Quick Start Guide

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up secrets:**
   - Copy `streamlit/secrets.toml.example` to `streamlit/secrets.toml`
   - Fill in your OpenAI API key and email credentials

3. **Run the app:**
   ```bash
   streamlit run app/main.py
   ```
   Or:
   ```bash
   streamlit run main.py
   ```

## Streamlit Cloud Deployment

1. **Push to GitHub:**
   - Create a GitHub repository
   - Push your code

2. **Deploy on Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Connect your repository
   - Set the main file path to: `app/main.py` or `main.py`
   - Add secrets in the Streamlit Cloud dashboard:
     - `OPENAI_API_KEY`
     - `SMTP_USERNAME`
     - `SMTP_PASSWORD`
     - `EMAIL_FROM`

3. **Deploy!**

## Testing the Application

1. **Upload PDFs:**
   - Go to "Upload PDFs" page
   - Upload one or more PDF files
   - Click "Process PDFs"

2. **Test RAG:**
   - Go to "Chat" page
   - Ask questions about the uploaded PDFs
   - Example: "What services do you offer?"

3. **Test Booking:**
   - Say: "I want to book a doctor appointment"
   - Provide details when asked:
     - Name: "John Doe"
     - Email: "john@example.com"
     - Phone: "123-456-7890"
     - Date: "2024-12-15"
     - Time: "14:30"
   - Confirm the booking

4. **Test Web Search:**
   - Ask: "What's the weather today?" or "Search for latest AI news"

5. **View Bookings:**
   - Go to "Admin Dashboard"
   - View all bookings
   - Search by name, email, or date

## Troubleshooting

- **OpenAI API Key Error:** Make sure you've set the `OPENAI_API_KEY` in secrets or environment variables
- **Email Not Sending:** Check your SMTP credentials. For Gmail, use an App Password, not your regular password
- **PDF Processing Error:** Ensure PDFs contain extractable text (not just images)
- **Database Errors:** The SQLite database will be created automatically. Make sure the app has write permissions

## Notes

- SQLite database resets on Streamlit Cloud restarts (this is expected behavior)
- Vector store persists across sessions
- Memory is maintained per session (last 20-25 messages)

