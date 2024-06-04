# import requests
# import datetime

# # URL вашего эндпоинта
# url = 'http://127.0.0.1:8000/workers/client/{client_id}/documents/upload_documents/'

# # Замена на реальный client_id
# client_id = 2
# url = url.replace('{client_id}', str(client_id))

# # Пути к файлам, которые вы хотите загрузить
# files = [
#     ('documents', ('APITEST-main.zip', open(r'C:\Users\Surface\Downloads\APITEST-main.zip', 'rb')))
#     # ('documents', ('python38.zip', open(r'C:\Users\Surface\Downloads\python-3.8.10-embed-amd64\python38.zip', 'rb'))),
# ]

# # Дополнительные данные
# data = {
#     'title': 'zip.file',
#     'uploaded_at': datetime.datetime.now().isoformat()
# }

# try:
#     # Отправка запроса
#     response = requests.post(url, files=files, data=data)

#     # Закрытие файлов после использования
#     for _, file in files:
#         file[1].close()

#     # Проверка статуса ответа
#     if response.status_code == 201:
#         try:
#             print(response.json())
#             print('TEST GOOD')
#         except ValueError:
#             print("Ответ не является допустимым JSON.")
#     else:
#         print(f"Ошибка: {response.status_code}")
#         print(response.text)
# except requests.RequestException as e:
#     print(f"Произошла ошибка при выполнении запроса: {e}")
import requests
import json

# Задаем URL вашего API
url = 'http://127.0.0.1:8000/workers/client/10/documents/130/edit_documents'

# Тестовые данные для обновления, удаления и добавления документов
data = {
    "title": "Updated Group Title",
    "delete_ids": ["132"],  # Предполагается использование UUID
    "updated_documents": [
        {
            "uuid": "131",  # Предполагается использование UUID для идентификации
            "file": open(r'C:\Users\Surface\Downloads\APITEST-main.zip', 'rb')
        }
    ],
    "new_documents": [
        {
            "file": open(r'C:\Users\Surface\Downloads\APITEST-main.zip', 'rb')
        }
    ]
}

# Функция для отправки POST-запроса
def send_post_request(data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f'Status Code: {response.status_code}')
        try:
            print(f'Response: {response.json()}')
        except json.JSONDecodeError:
            print(f'Response content: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')

# Выполнение теста
print("\nTesting Edit Documents:")
send_post_request(data)


# # Выполнение тестов
# print("Testing Update Title:")
# send_post_request(data_update_title)

# print("\nTesting Delete Documents:")
# send_post_request(data_delete_documents)

# print("\nTesting Update Documents:")
# send_post_request(data_update_documents)

# print("\nTesting Add New Documents:")
# send_post_request(data_add_documents)
