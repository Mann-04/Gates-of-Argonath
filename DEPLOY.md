# Deployment Guide - GitHub

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the repository details:
   - **Repository name**: `gates-of-argonath` (or your preferred name)
   - **Description**: "Gates Of Argonath Gaming Convention Booking System - AI-powered ticket booking chatbot"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 2: Push Your Code to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
cd "c:\mann\Study\Important\NeoStats AI Engineer Use Case\pillar_of_men"

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gates-of-argonath.git

# Rename the default branch to main (if needed)
git branch -M main

# Push your code
git push -u origin main
```

## Alternative: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/gates-of-argonath.git
git branch -M main
git push -u origin main
```

## Step 3: Verify Deployment

1. Go to your GitHub repository page
2. You should see all your files there
3. The `.streamlit/secrets.toml` file should NOT be visible (it's in .gitignore)

## Important Notes

- **Never commit secrets**: The `.streamlit/secrets.toml` file is already in `.gitignore` and won't be pushed
- **API Keys**: Make sure your `GEMINI_API_KEY` and email credentials are NOT in the repository
- **Database files**: The `*.db` files are also ignored and won't be pushed

## For Streamlit Cloud Deployment

After pushing to GitHub:

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository: `gates-of-argonath`
5. Set the main file path: `app/main.py`
6. Add secrets in the Streamlit Cloud dashboard:
   - `GEMINI_API_KEY`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `EMAIL_FROM`
7. Click "Deploy"

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
