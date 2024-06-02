# import requests
# import datetime

# # URL вашего эндпоинта
# url = 'http://127.0.0.1:8000/workers/client/{client_id}/documents/upload_documents/'

# # Замена на реальный client_id
# client_id = 9
# url = url.replace('{client_id}', str(client_id))

# # Пути к файлам, которые вы хотите загрузить
# files = [
#     ('documents', ('APITEST-main.zip', open(r'C:\Users\Surface\Downloads\APITEST-main.zip', 'rb'))),
#     ('documents', ('python38.zip', open(r'C:\Users\Surface\Downloads\python-3.8.10-embed-amd64\python38.zip', 'rb'))),
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


# import requests

# # URL API
# url = 'http://127.0.0.1:8000/workers/client/2/documents/18/edit_documents'

# # Данные для тестирования изменения группы документов
# data = {
#     "delete_ids": [20],  # Пример ID документов для удаления
#     "updated_documents": [  # Пример обновления документов
#         {
#             "id": 21,
#             "title": "Updated Title"
#         }
#     ],
#     "new_documents": [  # Пример добавления новых документов
#         {
#             "title": "New Document",
#             "file": "path/to/new/document.pdf"
#         }
#     ]
# }

# # Заголовки запроса
# headers = {
#     'Content-Type': 'application/json'
# }

# # Отправка POST запроса
# response = requests.post(url, json=data, headers=headers)

# # Вывод ответа от сервера
# print('Status Code:', response.status_code)
# print('Response Body:', response.json())
