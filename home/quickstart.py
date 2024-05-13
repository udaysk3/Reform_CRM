import os.path
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            # Modify the redirect URI to your hosted domain
            redirect_uri = 'https://web-production-e2474.up.railway.app'
            creds = flow.run_local_server(port=3000, host='0.0.0.0', redirect_uri=redirect_uri)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Create the Gmail API client
        gmail = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

        # Create the watch request
        request = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/sample-420901/topics/MyTopic',
            'labelFilterBehavior': 'INCLUDE'
        }

        # Execute the watch request
        response = gmail.users().watch(userId='me', body=request).execute()

        # Print a success message
        print(response)

        # Now, let's print the history of the user's Gmail
        list_history(gmail)

    except HttpError as error:
        # TODO(developer) - Handle errors from Gmail API.
        print(f"An error occurred: {error}")


def list_history(gmail):
    try:
        # Call the users.history.list endpoint
        response = gmail.users().history().list(userId='me').execute()
        history = response.get('history', [])
        if history:
            print("History:")
            for item in history:
                print(item)
        else:
            print("No history found.")

    except HttpError as error:
        # TODO(developer) - Handle errors from Gmail API.
        print(f"An error occurred while listing history: {error}")


if __name__ == "__main__":
    main()
