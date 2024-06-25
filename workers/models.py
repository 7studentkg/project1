from django.utils.translation import gettext_lazy as _
from django.db import models
import enum



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
    image = models.ImageField(upload_to='client_image', verbose_name="Фотография")
    birthLastName = models.CharField(max_length=200, verbose_name="Фамилия при рождении")
    currentLastName = models.CharField(max_length=200, verbose_name="Нынешная фамилия")
    firstName = models.CharField(max_length=200, verbose_name="Имя")
    birthDate = models.CharField(max_length=200, verbose_name="Дата рождения")
    birthPlace = models.CharField(max_length=200, verbose_name="Место рождения")
    residence = models.CharField(max_length=200, verbose_name="Фактический адрес проживание")
    passportNumber = models.CharField(max_length=200, verbose_name="Норер загран паспорта")
    passportIssueDate = models.CharField(max_length=200, verbose_name="Дата выдачи загранпаспорта")
    passportExpirationDate = models.CharField(max_length=200, verbose_name="Дата оканчание загранпаспорта")
    passportIssuingAuthority = models.CharField(max_length=200, verbose_name="Оргна выдачи загранпаспорта")
    email = models.CharField(max_length=300)
    password = models.CharField(max_length=300)
    height = models.CharField(max_length=200, verbose_name="Рост")
    weight = models.CharField(max_length=200, verbose_name="Вес")

    LEVEL_CHOICES = [('Новичок', 'Новичок'), ('Средний', 'Средний'), ('Отличный', 'Отличный')]
    englishLevel = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='Новичок', verbose_name="Уровень английского языка")

    FAMILY_STATUS = [('Холост/Не замужем', 'Холост/Не замужем'), ('Женат/Замужем', 'Женат/Замужем'), ('Разведен(а)', 'Разведен(а)')]
    familyStatus = models.CharField(max_length=50, choices=FAMILY_STATUS, default='Холост/Не замужем', verbose_name="Семейный статус")

    country = models.TextField(verbose_name="Страны")
    education = models.TextField(verbose_name="Образование")
    driving_licence = models.CharField(max_length=100, blank=True, verbose_name="Водительские права")
    experience = models.TextField(blank=True, verbose_name="Опыт работы")

    status = models.CharField(max_length=100, verbose_name="Статус")
    referal = models.CharField(max_length=300, verbose_name="От кого")
    workers = models.CharField(max_length=300, verbose_name="Специалист")

    notes = models.TextField(blank=True, verbose_name="Заметки")
    related_clients = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='related_to')


    uploaded_at = models.DateTimeField(auto_now_add=True) # ДАТА ДОБАВЛЕНИЯ
    last_modified = models.DateTimeField(auto_now=True) # ДАТА ПОСЛЕДНЕГО ИЗМЕНЕНИЯ

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f'{self.birthLastName} {self.firstName}'


class PartnerClass(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Партнер")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"



class Partner(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, related_name='partners')
    name_partner = models.ForeignKey(PartnerClass, on_delete=models.CASCADE, blank=True, verbose_name="Название партнера")
    text = models.TextField(verbose_name="Текст")



class Child(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=300, blank=True, verbose_name="ФИО")
    birthDate = models.CharField(max_length=100, blank=True, verbose_name="Дата рождения")

    class Meta:
        verbose_name = "Дети"
        verbose_name_plural = "Дети"



class Mother(models.Model):
    client = models.OneToOneField(Client, related_name='mother', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, verbose_name="ФИО")
    birthDate = models.CharField(max_length=100, blank=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=200, blank=True, verbose_name="Телефон номера")

    class Meta:
        verbose_name = "Мать"
        verbose_name_plural = "Мать"



class Father(models.Model):
    client = models.OneToOneField(Client, related_name='father', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, verbose_name="ФИО")
    birthDate = models.CharField(max_length=100, blank=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=200, blank=True, verbose_name="Телефон номера")

    class Meta:
        verbose_name = "Отец"
        verbose_name_plural = "Отец"



class Contact(models.Model):
    client = models.OneToOneField(Client, related_name='contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, verbose_name="ФИО")
    birthDate = models.CharField(max_length=200, blank=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=200, blank=True, verbose_name="Телефон номера")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакт"



class DocumentFile(models.Model):
    file = models.FileField(upload_to='client_documents/%Y/%m/%d/', max_length=300, blank=True)

    def __str__(self):
        return self.file.name


class Document(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255, verbose_name="Название")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    files = models.ManyToManyField(DocumentFile, related_name='documents_files', verbose_name="Документы")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class PaymentFile(models.Model):
    file = models.FileField(upload_to='client_payment_files', max_length=300, blank=True)

    def __str__(self):
        return self.file.name

class RefundFile(models.Model):
    file = models.FileField(upload_to='client_refund_files', max_length=300, blank=True)

    def __str__(self):
        return self.file.name



class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payment')
    title = models.TextField(verbose_name="Описание оплаты", blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", blank=True)
    files = models.ManyToManyField(PaymentFile, related_name='payment_files', verbose_name="Файлы оплаты")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплата"



class Refund(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='refund')
    title = models.TextField(verbose_name="Описание возврата", blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", blank=True)
    files = models.ManyToManyField(RefundFile, related_name='refund_files', verbose_name="Файлы возврата")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Возврат"
        verbose_name_plural = "Возврат"
