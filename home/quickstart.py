import os.path
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    creds = None
    if os.path.exists("../static/token.json"):
        creds = Credentials.from_authorized_user_file("../static/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
          "../static/credentials.json", SCOPES
      )
            creds = flow.run_local_server(port=3000)
            print(creds)
        # Save the credentials for the next run
        with open("../static/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        TOPIC_NAME = "projects/reform-crm-1715524659999/topics/ReformTopic"

        # Create the Gmail API client
        gmail = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

        # Create the watch request
        request = {
        'labelIds': ['UNREAD'],
        'topicName': TOPIC_NAME,
        'labelFilterAction': 'INCLUDE'
    }

        # Execute the watch request
        response = gmail.users().watch(userId='me', body=request).execute()

        # Print a success message
        print(response)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
