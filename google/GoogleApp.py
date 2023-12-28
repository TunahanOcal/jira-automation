import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


class GoogleApp:

    CLIENT_SECRET_FILE: str
    def __init__(self) -> None:
        self.CLIENT_SECRET_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") 
        #To connect Gspread API you need a service account credentials.
        pass

    def getGoogleSpreadSheet(self,sheet_id:str,document_key:str) -> gspread.Worksheet:
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.CLIENT_SECRET_FILE, scope)
        gs_client = gspread.authorize(creds)
        sheet = gs_client.open_by_key(key=document_key).get_worksheet_by_id(id=sheet_id)
        return sheet
