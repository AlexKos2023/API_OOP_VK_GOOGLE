Код состоит из трех классов.
Класс VK предназначен для получения доступа к ресурсу VK с использованием API VK. Для этого необходимо сообщить ID своего приложения, получить ID пользователя от которого буду получать информацию и токен, посредством направления ссылки сформированной (https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit#heading=h.4cksbw8kq4a1):
APP_ID = '51791067'
OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
params = {'client_id' : APP_ID,
          'redirect_uri' : 'https://oauth.vk.com/blank.html',
          'display' : 'page',
          'scope' : 'photos,offline',
          'response_type' : 'token'
        }
oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
print(oauth_url)
В методе give_me_folders_id возвращаются номера всех папок пользователя. 
Метод give_me_photos собирает в словарь информацию для ее передачи в облако.
В метод send_photo_in_yandex передается словарь из give_me_photos и название папки для размещения фотографий в ней.
Для работы с Google_API необходимо создать проект и использовать тестовые коды (https://developers.google.com/drive/api/guides/manage-uploads?hl=ru#python), представленные в документации. Подробно о создании проекта https://azzrael.ru/google-cloud-platform-create-app?ysclid=lp9cmnk4g4571770407.