from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
import os
import smtplib
import pandas as pd

# path of the directories
source = "file to be moved's original location directory (ex. downloads)"
destination = "target location of moved file"

#reference csv file to check if book already exists
checkdir = "directory of reference csv file"

# interacting with directory 
list1 = os.listdir(source)
check = pd.read_csv(checkdir)

# Get a list of all the files in the directory
files = os.listdir(destination)

# check if a downloads contains file and to transfer to Books
# Comparing the returned list to empty list
if os.listdir(source) == []:
    print("no files")

else:
    # gather all files
    allfiles = os.listdir(source)
    
    # iterate on all files to move them to destination folder
    for f in allfiles:
        src_path = os.path.join(source, f)
        dst_path = os.path.join(destination, f)
        os.rename(src_path, dst_path)

# function to send emails
def send_email(attachment_path):
    MAX_SIZE = 25 * 1024 * 1024 # 25 MB
    file_size = os.path.getsize(attachment_path)
    if file_size > MAX_SIZE:
        print("File too large to send by email")
        return
    else:
        # Gmail account details
        gmail_user = "gmail that's sending the email"
        gmail_password = "found in google settings > privacy > turn on 2 step verification > app passwords below 2 step verification will appear"
        to = "email recieving"
        subject = "whatever subject you want"
        body = "whatever body you want"

        # Create the message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body))

        # Attach the PDF file
        with open(attachment_path, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="pdf")
        attach.add_header('content-disposition', 'attachment', filename=file)
        msg.attach(attach)

        # Send the email
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, gmail_password)
        smtp.sendmail(gmail_user, to, msg.as_string())
        smtp.quit()

# function to upload to drive
def upload_basic():
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # Specify the API credentials for the desired Google Drive account
    creds = Credentials.from_authorized_user_info(info={
    "client_id": "look up how to get client id from google",
    "client_secret": "look up how to get client secret from google",
    "refresh_token": "look up how to get refresh token"})

    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    # name of the file and location on drive to be uploaded to i.e. which file on drive
    # if just upload to drive with no specific file remove parents.
    file_metadata = {'name': file, 'parents':['file id returned when running the below code']}
    media = MediaFileUpload(ref, mimetype='application/pdf')

    '''
    # Code to find folder ID so I can throw files into file in drive
    # Define the name of the folder you want to find
    folder_name = 'your folders name on drive (be careful to not mistype it)'
    service = build('drive', 'v3', credentials=creds)
    # Perform a search for the folder using the folder's name
    query = "mimeType='application/vnd.google-apps.folder' and trashed = false and name='" + folder_name + "'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])

    # If the search found a folder, return its ID
    if items:
        folder_id = items[0].get('id')
        print(F'Folder ID: {folder_id}')
    else:
        print(F'Folder not found')
    '''

    try:
        file1 = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(F'File ID: {file1.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file1 = None

    return file1.get('id')

# Loop through the list of files
for file in files:
    # directory of file is ref
    ref = destination + "\\" + file
    if file not in check.values:
        # Print the file name
        #print(file)
        #print(ref)

        if __name__ == '__main__':
            upload_basic()
            send_email(ref)
        
        data = {'Name': [file]} 

        # Make data frame of above data
        df = pd.DataFrame(data)
        print(df)

        # append data frame to CSV file
        df.to_csv(checkdir, mode='a', index=False, header=False)
        