from django.db import models

# Create your models here.


class Passport(models.Model):
    serial = models.CharField(max_length=12, verbose_name="Серия")
    number = models.CharField(max_length=12, verbose_name="Номер")
    getted_by = models.CharField(max_length=255, verbose_name="Выдан")
    getted_date = models.DateField(verbose_name="Дата выдачи")
    birthday_date = models.DateField(verbose_name="День рождения")
    birthday_place = models.CharField(max_length=255, verbose_name="Место рождения")
    registration_adress = models.CharField(max_length=255, verbose_name="Адрес регистрации")



class Object(models.Model):
    comment = models.TextField(verbose_name="Примечание", blank=True)
    type_of_building = models.CharField(max_length=255, verbose_name="Тип домовладения")
    type_of_city = models.CharField(max_length=255, verbose_name="Тип населенного пункта")
    region = models.CharField(max_length=255, verbose_name="Область")
    street_type = models.CharField(max_length=255, verbose_name="Тип улицы")
    area = models.CharField(max_length=255, verbose_name="Район")
    city = models.CharField(max_length=255, verbose_name="Город")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house = models.CharField(max_length=255, verbose_name="Дом")
    room = models.CharField(max_length=255, verbose_name="Квартира или часть дома", blank=True)
    postcode = models.CharField(max_length=50, verbose_name="Индекс", blank=True)
    passport = models.OneToOneField(Passport, on_delete = models.CASCADE)
    show_part = models.BooleanField(verbose_name="Отображать часть дома/квартиру в документах", blank=True, null=True)
    gas_date = models.DateField(verbose_name="Дата пуска газа", blank=True, null=True)

    def get_full_address(self):
        address = f'{self.type_of_city} {self.city}, {self.street_type} {self.street}, д. {self.house} {self.room}'
        return address


class Client(models.Model):
    object = models.ForeignKey(Object, on_delete = models.CASCADE, blank=True, null=True)
    firstname = models.CharField(max_length=256, verbose_name="Имя")
    lastname = models.CharField(max_length=256, verbose_name="Фамилия")
    middlename = models.CharField(max_length=256, verbose_name="Отчество")
    is_main = models.BooleanField(verbose_name="Главный?")
    role = models.CharField(max_length=256, verbose_name="Роль")
    sex = models.CharField(max_length=20, verbose_name="Пол")
    
    
class Phone(models.Model):
    number = models.CharField(max_length=256, verbose_name="Номер телефона")
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    


class Master(models.Model):
    firstname = models.CharField(max_length=256, verbose_name="Имя")
    lastname = models.CharField(max_length=256, verbose_name="Фамилия")
    middlename = models.CharField(max_length=256, verbose_name="Отчество")
   

class Contract(models.Model):
    object = models.ForeignKey(Object, on_delete = models.CASCADE, blank=True, null=True)
    number = models.IntegerField(verbose_name="Номер")
    status = models.CharField(max_length=50, verbose_name="Статус")
    date = models.DateField(verbose_name="Дата")
    summ = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    
    # positions = models.CharField(max_length=255, verbose_name="Выдан")
    