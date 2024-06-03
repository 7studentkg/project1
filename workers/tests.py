import requests
import datetime

# URL вашего эндпоинта
url = 'http://127.0.0.1:8000/workers/client/{client_id}/documents/upload_documents/'

# Замена на реальный client_id
client_id = 2
url = url.replace('{client_id}', str(client_id))

# Пути к файлам, которые вы хотите загрузить
files = [
    ('documents', ('APITEST-main.zip', open(r'C:\Users\Surface\Downloads\APITEST-main.zip', 'rb')))
    # ('documents', ('python38.zip', open(r'C:\Users\Surface\Downloads\python-3.8.10-embed-amd64\python38.zip', 'rb'))),
]

# Дополнительные данные
data = {
    'title': 'zip.file',
    'uploaded_at': datetime.datetime.now().isoformat()
}

try:
    # Отправка запроса
    response = requests.post(url, files=files, data=data)

    # Закрытие файлов после использования
    for _, file in files:
        file[1].close()

    # Проверка статуса ответа
    if response.status_code == 201:
        try:
            print(response.json())
            print('TEST GOOD')
        except ValueError:
            print("Ответ не является допустимым JSON.")
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)
except requests.RequestException as e:
    print(f"Произошла ошибка при выполнении запроса: {e}")

# import requests
# import json

# # Задаем URL вашего API
# url = 'http://127.0.0.1:8000/workers/client/2/documents/111/edit_documents'  # Замените на ваш фактический URL

# # Тестовые данные для обновления группы документов
# # data_update_title = {
# #     "title": "Updated Group Title"
# # }

# data_delete_documents = {
#     "delete_ids": [111]  # Указывайте реальные ID документов для удаления
# }

# # data_update_documents = {
# #     "updated_documents": [
# #         {
# #             "id": 21,  # Указывайте реальный ID документа
# #             "file": ""
# #         }
# #     ]
# # }


# # Функция для отправки POST-запроса
# def send_post_request(data):
#     headers = {'Content-Type': 'application/json'}  # Заголовки запроса
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#     print(f'Status Code: {response.status_code}')
#     print(f'Response: {response.json()}')

# # # Выполнение тестов
# # print("Testing Update Title:")
# # send_post_request(data_update_title)

# print("\nTesting Delete Documents:")
# send_post_request(data_delete_documents)

# # print("\nTesting Update Documents:")
# # send_post_request(data_update_documents)

# # print("\nTesting Add New Documents:")
# # send_post_request(data_add_documents)
