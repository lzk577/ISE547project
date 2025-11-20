# GitHub Upload Guide

This guide will help you upload your project to GitHub.

## Prerequisites

1. A GitHub account (create one at https://github.com if you don't have one)
2. Git installed on your system (should already be installed)

## Step 1: Configure Git (First Time Only)

Open PowerShell or Command Prompt in your project directory and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace "Your Name" and "your.email@example.com" with your actual name and email.

## Step 2: Create a GitHub Repository

1. Go to https://github.com and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Enter a repository name (e.g., "ISE547project" or "chat-with-your-data")
5. Choose Public or Private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 3: Commit Your Files

In your project directory, run:

```bash
# Add all files (respecting .gitignore)
git add .

# Commit with a message
git commit -m "Initial commit: Chat with Your Data project"
```

## Step 4: Connect to GitHub and Push

After creating the repository on GitHub, you'll see instructions. Run these commands:

```bash
# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note:** You may be prompted for your GitHub username and password. If you have two-factor authentication enabled, you'll need to use a Personal Access Token instead of your password.

### Creating a Personal Access Token (if needed)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name and select scopes: `repo` (full control of private repositories)
4. Click "Generate token"
5. Copy the token and use it as your password when pushing

## Step 5: Verify Upload

Go to your GitHub repository page and verify all files are uploaded correctly.

## Important Notes

- The `.env` file is excluded from Git (contains sensitive API keys)
- `chat_history/` and `uploads/` directories are excluded (user data)
- `__pycache__/` directories are excluded (Python cache files)

## Troubleshooting

### If you get "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### If you need to update files later
```bash
git add .
git commit -m "Your commit message"
git push
```

