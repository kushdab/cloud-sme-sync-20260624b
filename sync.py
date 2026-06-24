import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
LOCAL_BACKUP_PATH = './backup_files'

def authenticate_drive():
    """Handles authentication and returns the Drive API service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, folder_name):
    """Checks if a folder exists on Drive, otherwise creates it."""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    if items:
        return items[0]['id']
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def sync_file(service, file_path, folder_id):
    """Uploads a new file or updates an existing one on Google Drive."""
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)
    
    # Check if file already exists in the destination folder
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    try:
        if items:
            file_id = items[0]['id']
            print(f"Updating existing file: {file_name} (ID: {file_id})")
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            print(f"Uploading new file: {file_name}")
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    """Main logic to iterate through local directory and sync to Drive."""
    if not os.path.exists(LOCAL_BACKUP_PATH):
        os.makedirs(LOCAL_BACKUP_PATH)
        print(f"Created local directory '{LOCAL_BACKUP_PATH}'. Add files there to sync.")
        return

    service = authenticate_drive()
    drive_folder_id = find_or_create_folder(service, 'Python_Backup_Folder')

    files_to_sync = [f for f in os.listdir(LOCAL_BACKUP_PATH) if os.path.isfile(os.path.join(LOCAL_BACKUP_PATH, f))]
    
    if not files_to_sync:
        print("No local files found to sync.")
        return

    for file_name in files_to_sync:
        local_full_path = os.path.join(LOCAL_BACKUP_PATH, file_name)
        sync_file(service, local_full_path, drive_folder_id)

    print("Sync operation completed.")

if __name__ == '__main__':
    main()