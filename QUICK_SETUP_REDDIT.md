# Reddit Configuration: RSS Fallback

## Status: Using RSS Feeds (No App Required)

Since creating a Reddit App was restricted, the bot has been switched to use **Public RSS Feeds**.

### What This Means
- ❌ You **DO NOT** need to create a Reddit App.
- ❌ You **DO NOT** need to add any secrets to GitHub.
- ✅ The bot works "out of the box" using public data.
- ✅ It uses random User-Agents to avoid blocking.

### Troubleshooting
If you see 429 (Too Many Requests) or 403 errors in the future:
1. The bot automatically retries with `old.reddit.com`
2. It uses random User-Agents
3. If issues persist, we may need to try the App creation again in a few weeks (when your account is older).

### Testing
To verify it works:
1. Run `python src/monitor.py` locally
2. Or trigger the "WWM Bot Check" workflow in GitHub Actions
