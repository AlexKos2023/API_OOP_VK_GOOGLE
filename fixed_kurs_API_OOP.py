import requests
import pprint
import json
import os
import os.path
import google.auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from tqdm import tqdm
from time import sleep
from datetime import datetime as dt


VK_ID = str(input("Введите VK_ID:" ))
APP_ID = '51791067'
TOKEN = str(input("Введите TOKEN VK:" ))
authorization = str(input("Введите YANDEX:" ))


class VK:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token,
                       'v': self.version,
                       }

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def give_me_users_info(self):
        params = {'user_ids': self.id}
        response = requests.get(self._build_url('users.get'), params={**self.params, **params})
        return response.json()

    def give_me_folders_id(self):
        params = {'owner_id': self.id,
                  'extended': 1,
                  'need_system': 1,
                  'photo_sizes': 1,
                  }
        response = requests.get(self._build_url('photos.getAlbums'), params={**self.params, **params})
        folders_list_id = []
        for i in response.json()['response']['items']:
            folders_list_id.append(i['id'])
        return folders_list_id

    def give_me_photos(self):
        params = {'owner_id': self.id,
                  'extended': 1,
                  'rev': 0,
                  'photo_sizes': 1,
                  }
        information = []
        for i in self.give_me_folders_id():
            response = requests.get(self._build_url('photos.get'), params={**self.params, **params, 'album_id': f"{i}"})
            photos = response.json()['response']['items']
            for photo in photos:
                new_list = sorted(photo['sizes'], key=lambda i: int(i['height']) * int(i['width']))
                name = f"{photo['likes']['user_likes']}_{dt.strftime(dt.fromtimestamp(photo['date']),'%Y-%m-%d %H-%M-%S')}"
                new_list[-1]['file_name'] = name
                information.append(new_list[-1])
                # Использовать если необходимо записать на ЖМД
                #biggest = new_list[-1]['url']
                #content = requests.get(biggest).content
                #with open(f"{i}_{name}.jpg", 'wb') as f:
                    #f.write(content)
        inf_for_report = json.dumps(information, indent=2)
        with open("report.json", 'w') as f:
            f.write(inf_for_report)
        return information
        
               
class YANDEX:
    YA_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, authorization):
        self.token = authorization
        self.headers = {'Accept' : 'application/json',
                        'Authorization': self.token
                        } 
    
    def _build_url(self, api_method):
        return f'{self.YA_URL}/{api_method}'
    
    def send_photo_in_yandex(self, folder_name, information):
        self.folder_name = folder_name
        params = {'path': f'{folder_name}'}
        response = requests.put(self._build_url(''), params = {**params}, headers = {**self.headers})
        for photo in information:
            try:
                file_name = photo['file_name']
                path = f'{folder_name}/{file_name}'
                url = photo['url']
                params_ = {
                    'path': path,
                    'url': url,
                    'fields': 'file_name'
                }
                response = requests.post(self._build_url('upload'), params = {**params_}, headers = {**self.headers})
                for i in tqdm(response.json(), bar_format="{l_bar}{bar:20}{r_bar}", desc ="Installing Happiness"):
                    sleep(1)
                #print(response.json())
            except KeyError:
                pass
          
    
class GOOGLE:
    
    def __init__(self, user_id):
        self.user_id = user_id
                 
    def give_me_token_google(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly",
                  "https://www.googleapis.com/auth/drive",
                  "https://www.googleapis.com/auth/drive.photos.readonly",
                  "https://www.googleapis.com/auth/drive.readonly"]
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
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
                "Credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
          # Save the credentials for the next run
          with open("token.json", "w") as token:
            token.write(creds.to_json())

        try:
          service = build("drive", "v3", credentials=creds)

          # Call the Drive v3 API
          results = (
              service.files()
              .list(pageSize=1, fields="nextPageToken, files(id, name)")
              .execute()
          )
          items = results.get("files", [])

          if not items:
            print("No files found.")
            return
          print("Files:")
          for item in items:
            print(f"{item['name']} ({item['id']})")
        except HttpError as error:
          # TODO(developer) - Handle errors from drive API.
          print(f"An error occurred: {error}")
          
    def getFileList(self, N): 
        self.N = N
        existed_folders = {}
        # Аутентификация
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
        if not creds or not creds.valid:
           # Создаем новый flow для аутентификации
            flow = google.auth.flow.InstalledAppFlow.from_client_secrets_file(
                'token.json', ['https://www.googleapis.com/auth/drive']
            )
            creds = flow.run_local_server(port=0)
            # Сохраняем учетные данные для будущих использований
            with open('token.json', 'wb') as token:
                json.dump(creds, token)
        service = build('drive', 'v3', credentials=creds) 
        resource = service.files() 
        result = resource.list(pageSize=N, fields="files(id, name)").execute()
        
        result_dict = result.get('files')
        for file in result_dict: 
            #print(file['name'], file['id'])
            existed_folders[file['name']] = file['id']
        return existed_folders

    def give_me_folder_google(self,folder_name, existed_folders):
        self.folder_name = folder_name
        self.existed_folders = existed_folders
        # Аутентификация
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
        if not creds or not creds.valid:
           # Создаем новый flow для аутентификации
            flow = google.auth.flow.InstalledAppFlow.from_client_secrets_file(
                'token.json', ['https://www.googleapis.com/auth/drive']
            )
            creds = flow.run_local_server(port=0)
            # Сохраняем учетные данные для будущих использований
            with open('token.json', 'wb') as token:
                json.dump(creds, token)
        # Создание папки
        if existed_folders.get(f'{self.folder_name}') != None:
            res = str(existed_folders[f'{self.folder_name}'])
        else:
            drive_service = build('drive', 'v3', credentials=creds)
            folder_metadata = {
                'name': f'{self.folder_name}',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            print(f"Создана папка с ID: {folder.get('id')}")
            res = folder.get('id')
        return res


    def upload_file(self, information, folder_id=None):
        # Указываем путь к credentials.json
        creds = Credentials.from_authorized_user_file('token.json')
        # Создаем экземпляр объекта service с помощью build
        drive_service = build('drive', 'v3', credentials=creds)
        self.information = information
        for photo in information:
            try:
                file_metadata = {
                    'name': photo['file_name'],  # Имя загружаемого файла
                     }
                response = requests.get(photo['url'])
                media = MediaIoBaseUpload(BytesIO(response.content), mimetype='image/jpeg', resumable=True) 
                #media = MediaFileUpload(#Адрес файла в локальном, resumable=True)  # В случае необходимости загрузки с ЖМД
                if folder_id is not None:
                    file_metadata['parents'] = [folder_id]
                file = drive_service.files().create(
                    body = file_metadata,
                    media_body = media,
                    fields = 'id'
                ).execute()
            except KeyError:
                pass
        return file.get('id')
  
q = VK(TOKEN, VK_ID)
ya = YANDEX(authorization)
print(ya.send_photo_in_yandex('Animals', q.give_me_photos()))
#conda info --envs

f = GOOGLE(1)
f.give_me_token_google()
file_id = f.upload_file(q.give_me_photos(), (f.give_me_folder_google('Amimals', f.getFileList(10))))
print(f'Files uploaded successfully with last ID: {file_id}')
