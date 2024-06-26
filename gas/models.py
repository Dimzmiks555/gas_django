from django.db import models
import datetime

# Create your models here.

TYPE_OF_BUILDING__CHOICES = ({
    "Дом": "Дом",
    "Квартира": "Квартира",
})


TYPE_OF_MALE = ({
    "woman": "Женский",
    "man": "Мужской",
})

class Object(models.Model):
    type_of_building = models.CharField(max_length=255, verbose_name="Тип домовладения", choices=TYPE_OF_BUILDING__CHOICES)
    region = models.CharField(max_length=255, verbose_name="Область")
    area = models.CharField(max_length=255, verbose_name="Район")
    type_of_city = models.CharField(max_length=255, verbose_name="Тип населенного пункта")
    city = models.CharField(max_length=255, verbose_name="Город")
    street_type = models.CharField(max_length=255, verbose_name="Тип улицы")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house = models.CharField(max_length=255, verbose_name="Дом")
    room = models.CharField(max_length=255, verbose_name="Квартира", blank=True)
    postcode = models.CharField(max_length=50, verbose_name="Индекс", blank=True)
    show_part = models.BooleanField(verbose_name="Отображать часть дома/квартиру в документах", blank=True, null=True)
    gas_date = models.DateField(verbose_name="Дата пуска газа", blank=True, null=True)
    comment = models.TextField(verbose_name="Примечание", blank=True)

    def get_full_address(self):
        address = f'{self.type_of_city} {self.city}, {self.street_type} {self.street}, д. {self.house} {self.room}'
        return address
    
    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    
    def __str__(self): # new
        return f'Объект № {self.pk}'


class Client(models.Model):
    firstname = models.CharField(max_length=256, verbose_name="Имя")
    lastname = models.CharField(max_length=256, verbose_name="Фамилия")
    middlename = models.CharField(max_length=256, verbose_name="Отчество")
    is_main = models.BooleanField(verbose_name="Ответственное лицо?", default=True)
    role = models.CharField(max_length=256, verbose_name="Роль", default='Собственник')
    sex = models.CharField(max_length=20, verbose_name="Пол", choices=TYPE_OF_MALE)
    phone_number_1 = models.CharField(max_length=256, verbose_name="Номер телефона 1")
    phone_number_2 = models.CharField(max_length=256, verbose_name="Номер телефона 2", blank=True, null=True)
    phone_number_3 = models.CharField(max_length=256, verbose_name="Номер телефона 3", blank=True, null=True)
    object = models.ForeignKey(to=Object, verbose_name='Объект', on_delete=models.PROTECT)

    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Passport(models.Model):
    serial = models.CharField(max_length=12, verbose_name="Серия")
    passport_number = models.CharField(max_length=12, verbose_name="Номер")
    getted_by = models.CharField(max_length=255, verbose_name="Выдан")
    getted_date = models.DateField(verbose_name="Дата выдачи")
    division = models.CharField(max_length=255, verbose_name="Код подразделения")
    birthday_date = models.DateField(verbose_name="День рождения")
    birthday_place = models.CharField(max_length=255, verbose_name="Место рождения")
    registration_adress = models.CharField(max_length=255, verbose_name="Адрес регистрации")
    object = models.OneToOneField(to=Object, verbose_name='Объект', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Паспорт'
        verbose_name_plural = 'Паспорта'


class Master(models.Model):
    firstname = models.CharField(max_length=256, verbose_name="Имя")
    lastname = models.CharField(max_length=256, verbose_name="Фамилия")
    middlename = models.CharField(max_length=256, verbose_name="Отчество")
   
    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

class Contract(models.Model):
    object = models.ForeignKey(Object, on_delete = models.PROTECT, blank=True, null=True)
    contract_number = models.IntegerField(verbose_name="Номер", unique=True)
    status = models.CharField(max_length=50, verbose_name="Статус")
    date_of_contract = models.DateField(verbose_name="Дата", default=datetime.datetime.now())
    summ = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    
    # positions = models.CharField(max_length=255, verbose_name="Выдан")
    
    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договора'

    
class DeviceType(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")
    def __str__(self): # new
        return self.name
    
    class Meta:
        verbose_name = 'Категория оборудования'
        verbose_name_plural = 'Категории оборудования'

class DeviceKind(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")
    def __str__(self): # new
        return self.name
    
    class Meta:
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Типы оборудования'

class DeviceModel(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")

    def __str__(self): # new
        return self.name
    
    class Meta:
        verbose_name = 'Модель оборудования'
        verbose_name_plural = 'Модели оборудования'

class DeviceManufacter(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")

    def __str__(self): # new
        return self.name
    
    class Meta:
        verbose_name = 'Производитель оборудования'
        verbose_name_plural = 'Производители оборудования'

class DeviceModification(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")

    def __str__(self): # new
        return self.name

    class Meta:
        verbose_name = 'Модификация оборудования'
        verbose_name_plural = 'Модификации оборудования'

class ObjectDevice(models.Model):
    object = models.ForeignKey(Object, on_delete = models.PROTECT, blank=True, null=True)
    type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, verbose_name='Категория оборудования')
    kind = models.ForeignKey(DeviceKind, on_delete=models.PROTECT, verbose_name='Тип')
    modification = models.ForeignKey(DeviceModification, on_delete=models.PROTECT, verbose_name='Модификация')
    manufacter = models.ForeignKey(DeviceManufacter, on_delete=models.PROTECT, verbose_name='Производитель')
    model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT, verbose_name='Модель')
    sn = models.CharField(max_length=256, verbose_name="Серийный номер")
    date_of_manufacture = models.DateField(verbose_name="Дата изготовления",default=datetime.datetime.now())
    date_of_commissioning = models.DateField(verbose_name="Дата ввода в эксплуатацию", default=datetime.datetime.now())

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'


class Price(models.Model):
    type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, verbose_name='Тип оборудования')
    name = models.CharField(max_length=256, verbose_name="Название")
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Цена")
    
    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'