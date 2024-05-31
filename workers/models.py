import enum
from django.db import models
from django.utils.translation import gettext_lazy as _



# class Country(models.Model):

#     name_country = models.CharField(max_length=200, unique=True)

#     def __str__(self):
#         return self.name_country

#     @staticmethod
#     def create_countries():
#         countries = [
#             "Великобритания", "Дания", "Германия", "Польша", "Литва", "Латвия", "Словакия", "Венгрия",
#             "Сербия", "Турция", "Болгария", "Финляндия", "Норвегия", "Нидерланды", "Чехия", "Южная Корея"
#         ]

#         for country in countries:
#             Country.objects.get_or_create(name_country=country)


# class StatusEnum(enum.Enum):
#     NEWCOMER = 'Новенький', _('Новенький')
#     INVITED = 'Приглашен(а)', _('Приглашен(а)')
#     VISA_QUEUE = 'В очереди на получение визы', _('В очереди на получение визы')
#     WAITING_FOR_VISA = 'Ждет визу', _('Ждет визу')
#     GET_A_VISA = 'Получил(а) виз', _('Получил(а) визу')
#     FLEW_AWAY = 'Улетел(а)', _('Улетел(а)')
#     REFUND = 'Возврат', _('Возврат')
#     REFUSED = 'Отказ', _('Отказ')


#     @classmethod
#     def choices(cls):
#         return [(key.value[0], key.value[1]) for key in cls]


# class Status(models.Model):
#     name = models.CharField(
#         max_length=50,
#         choices=StatusEnum.choices(),
#         unique=True
#     )



#     def __str__(self):
#         return self.get_name_display()



class Client(models.Model):
    image = models.ImageField(upload_to='client_image')
    birthLastName = models.CharField(max_length=200) # ФАМИЛИЯ ПРИ РОЖДЕНИЙ
    currentLastName = models.CharField(max_length=200) # ФАМИЛИЯ
    firstName = models.CharField(max_length=200) # ИМЯ
    birthDate = models.CharField(max_length=200) # ДАТА РОЖДЕНИЯ
    birthPlace = models.CharField(max_length=200) # МЕСТО РОЖДЕНИЯ
    residence = models.CharField(max_length=200) # ФАКТИЧЕСКИЙ АДРЕС ПРОЖИВАНИЕ
    passportNumber = models.CharField(max_length=200) # НОМЕР ЗАГРАН ПАСПОРТА
    passportIssueDate = models.CharField(max_length=200) # ДАТА ВЫДАЧИ ЗАГРАНПАСПОРТА
    passportExpirationDate = models.CharField(max_length=200) # ДАТА ОКОНЧАНИЕ ЗАГРАНПАСПОРТА
    passportIssuingAuthority = models.CharField(max_length=200) # ОРГАН ВЫДАЧИ ЗАГРАНПАСПОРТА
    email = models.CharField(max_length=300) # Email
    password = models.CharField(max_length=300) # Password
    height = models.CharField(max_length=200) # РОСТ
    weight = models.CharField(max_length=200) # ВЕС

    LEVEL_CHOICES = [('Новичок', 'Новичок'), ('Средний', 'Средний'), ('Отличный', 'Отличный')]
    englishLevel = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='Новичок') # УРОВЕНЬ АНГЛИЙСКОГО ЯЗЫКА

    FAMILY_STATUS = [('Холост/Не замужем', 'Холост/Не замужем'), ('Женат/Замужем', 'Женат/Замужем'), ('Разведен(а', 'Разведен(а)')]
    familyStatus = models.CharField(max_length=50, choices=FAMILY_STATUS, default='Холост/Не замужем') # СЕМЕЙНЫЙ СТАТУС

    country = models.TextField() # СТРАНЫ
    status = models.CharField(max_length=100)


    uploaded_at = models.DateTimeField(auto_now_add=True) # ДАТА ДОБАВЛЕНИЯ
    last_modified = models.DateTimeField(auto_now=True) # ДАТА ПОСЛЕДНЕГО ИЗМЕНЕНИЯ


class Child(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, blank=True)
    birthDate = models.CharField(max_length=100, blank=True)


class Mother(models.Model):
    client = models.OneToOneField(Client, related_name='mother', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True)
    birthDate = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=200, blank=True)


class Father(models.Model):
    client = models.OneToOneField(Client, related_name='father', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True)
    birthDate = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=200, blank=True)



class Contact(models.Model):
    client = models.OneToOneField(Client, related_name='contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    birthDate = models.CharField(max_length=200, blank=True)



class Document(models.Model):
    client = models.ForeignKey(Client, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='client_documents/%Y/%m/%d/', max_length=255, blank=True)
    title = models.TextField(verbose_name="Название", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", blank=True)
    title = models.TextField(verbose_name="Описание оплаты", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class Refund(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='refund')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", blank=True)
    title = models.TextField(verbose_name="Описание возврата", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
