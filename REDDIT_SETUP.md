# Reddit API Setup Guide

## Problem
Reddit's API returns HTTP 403 errors when using simple JSON endpoint requests without proper authentication.

## Solution Options

### Option 1: Quick Fix (Current Implementation)
I've updated the headers in `reddit.py` to be more specific. However, this may still be blocked by Reddit.

**Try running the test again:**
```bash
python scripts/test_reddit_service.py
```

### Option 2: Use Official Reddit API (PRAW) - RECOMMENDED

This is the most reliable solution for long-term use.

#### Step 1: Install PRAW
```bash
pip install praw
```

#### Step 2: Create a Reddit App
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click **"Create App"** or **"Create Another App"**
3. Fill in the form:
   - **Name**: `WhereWindsMeetBot`
   - **App type**: Select **"script"**
   - **Description**: `Bot to monitor Where Winds Meet subreddit`
   - **About URL**: (leave blank)
   - **Redirect URI**: `http://localhost:8080`
4. Click **"Create app"**
5. You'll see your app with:
   - **Client ID**: The string under "personal use script" (looks like: `abc123XYZ`)
   - **Client Secret**: The string labeled "secret" (looks like: `xyz789ABC-def456GHI`)

#### Step 3: Update reddit_praw.py with Your Credentials

Open `src/services/reddit_praw.py` and replace:
```python
client_id="YOUR_CLIENT_ID",          # Replace with your client ID
client_secret="YOUR_CLIENT_SECRET",  # Replace with your client secret
user_agent="WhereWindsMeetBot/1.0 (by /u/YourRedditUsername)",  # Replace with your Reddit username
```

#### Step 4: Update monitor.py to Use PRAW

Change the import in `src/monitor.py`:
```python
# Old:
from services.reddit import RedditService

# New:
from services.reddit_praw import RedditServicePRAW as RedditService
```

#### Step 5: Test
```bash
python scripts/test_reddit_service.py
```

## Alternative: Use Environment Variables (More Secure)

Instead of hardcoding credentials, use environment variables:

1. Create a `.env` file in the project root:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=WhereWindsMeetBot/1.0 (by /u/YourRedditUsername)
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. Update `reddit_praw.py` to load from environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()

self.reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)
```

## GitHub Actions Setup (REQUIRED)

To make this work in GitHub Actions, you need to add your Reddit credentials as GitHub Secrets:

### Step 1: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** (top navigation)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following three secrets:

   **Secret 1:**
   - Name: `REDDIT_CLIENT_ID`
   - Value: Your client ID from the Reddit app (the string under "personal use script")
   
   **Secret 2:**
   - Name: `REDDIT_CLIENT_SECRET`
   - Value: Your client secret from the Reddit app (the "secret" string)
   
   **Secret 3:**
   - Name: `REDDIT_USER_AGENT`
   - Value: `WhereWindsMeetBot/1.0 (by /u/YourRedditUsername)` (replace with your Reddit username)

### Step 2: Verify Workflow Configuration

The workflow file `.github/workflows/daily_check.yml` has already been updated to use these secrets:

```yaml
- name: Run Monitor Script
  env:
    WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
    REDDIT_USER_AGENT: ${{ secrets.REDDIT_USER_AGENT }}
  run: python src/monitor.py
```

### Step 3: Test GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click on **WWM Bot Check** workflow
3. Click **Run workflow** → **Run workflow** (to manually trigger)
4. Wait for the workflow to complete
5. Check the logs to verify Reddit posts are being fetched without 403 errors

## Local Testing with Environment Variables

To test locally before pushing to GitHub:

**Windows PowerShell:**
```powershell
$env:REDDIT_CLIENT_ID="your_client_id"
$env:REDDIT_CLIENT_SECRET="your_client_secret"
$env:REDDIT_USER_AGENT="WhereWindsMeetBot/1.0 (by /u/YourUsername)"
python src/monitor.py
```

**Windows Command Prompt:**
```cmd
set REDDIT_CLIENT_ID=your_client_id
set REDDIT_CLIENT_SECRET=your_client_secret
set REDDIT_USER_AGENT=WhereWindsMeetBot/1.0 (by /u/YourUsername)
python src/monitor.py
```

**Linux/Mac:**
```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="WhereWindsMeetBot/1.0 (by /u/YourUsername)"
python src/monitor.py
```

## Why This Happens

Reddit has tightened API access to:
- Prevent scraping and abuse
- Encourage use of official API
- Better rate limiting and monitoring
- Comply with data protection regulations

The official PRAW library handles authentication, rate limiting, and retries automatically.

## Current Implementation Status

✅ **Completed:**
- Added `praw` to `requirements.txt`
- Updated `reddit_praw.py` to use environment variables
- Switched `monitor.py` to use `RedditServicePRAW`
- Updated GitHub Actions workflow to pass credentials

⚠️ **Required by User:**
- Create Reddit app at https://www.reddit.com/prefs/apps
- Add three GitHub Secrets (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
- Install praw locally: `pip install -r requirements.txt`

