# Google Drive Sync Script

This script backs up files from a local directory to a specific folder in your Google Drive using the Google Drive API v3.

## Setup

1.  **Google Cloud Console**:
    *   Create a project at [Google Cloud Console](https://console.cloud.google.com/).
    *   Enable the **Google Drive API**.
    *   Go to **OAuth consent screen**, set User Type to 'External', and add your email as a test user.
    *   Go to **Credentials**, click 'Create Credentials' -> 'OAuth client ID'.
    *   Select 'Desktop app', name it, and download the JSON file.
    *   Rename the downloaded file to `credentials.json` and place it in this project folder.

2.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Place files you want to back up inside a folder named `backup_files` (created automatically on first run).
2.  Run the script:
    ```bash
    python sync.py
    ```
3.  The first time you run it, a browser window will open for authentication. A `token.json` file will be created to store your session.

## Features
*   Automatically creates the destination folder on Drive.
*   Checks if files already exist: updates existing files or uploads new ones.