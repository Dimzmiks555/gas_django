from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, View, TemplateView
from .models import Object, Client, Phone, Passport, ObjectDevice, DeviceModel, DeviceType, Contract
from .forms import LoginUserForm, ObjectCreateForm, PassportCreateForm, ClientCreateForm, PhoneCreateForm, ContractCreateForm, ObjectDeviceFormSet
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import datetime
from .utils import generate_docx, transform_date_month, get_full_address
from django.utils.translation import get_language, activate
from num2words import num2words






class Login(LoginView):
    form_class = LoginUserForm
    template_name = "login.html"

def Index(request):
    return redirect('/objects')

class ObjectListView(LoginRequiredMixin, ListView):
    template_name = "app/object/list.html"
    model = Object
    extra_context = {
        'total': Object.objects.count(),
    }

    def get_queryset(self):
        return Object.objects.filter().order_by('-pk')


class ObjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = "app/object/create.html"
    extra_context = {
        'object_form': ObjectCreateForm,
        'passport_form': PassportCreateForm,
        'phone_form': PhoneCreateForm,
        'client_form' : ClientCreateForm,
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_formset'] = ObjectDeviceFormSet(queryset=ObjectDevice.objects.none())
        return context

    def post(self, request):
        print(request.POST)

        data = request.POST.dict()

        new_object = Object.objects.create(
            type_of_building = data['type_of_building'],
            region = data['region'],
            area = data['area'],
            type_of_city = data['type_of_city'],
            city = data['city'],
            street_type = data['street_type'],
            street = data['street'],
            house = data['house'],
            room = data['room'],
            postcode = data['postcode'],
            show_part = None,
            comment = data['comment']
        )

        new_client = Client.objects.create(
            firstname = data['firstname'],
            lastname = data['lastname'],
            middlename = data['middlename'],
            is_main = True if data['is_main'] == 'on' else False,
            role = data['role'],
            sex = data['sex'],
            object = new_object,
        )

        new_phone = Phone.objects.create(
            phone_number = data['phone_number'],
            client = new_client,
        )

        
        new_passport = Passport.objects.create(
            serial = data['serial'],
            passport_number = data['passport_number'],
            getted_by = data['getted_by'],
            getted_date = f'{data['getted_date_year']}-{data['getted_date_month']}-{data['getted_date_day']}',
            birthday_date = f'{data['birthday_date_year']}-{data['birthday_date_month']}-{data['birthday_date_day']}',
            birthday_place = data['birthday_place'],
            registration_adress = data['registration_adress'],
            object = new_object,
        )

        devices = {}


        for key in data.keys():
            if key.startswith('form') and key[5].isdigit():
                if key[5] in devices:
                    devices[key[5]][key[7:]] = data[key]
                else:
                    devices[key[5]] = {
                        key[7:]: data[key]
                    }
        print(devices)
        for device in devices:

            device_type = DeviceType.objects.filter(pk=devices[device]['type'])[0]
            device_model = DeviceModel.objects.filter(pk=devices[device]['model'])[0]

            new_device = ObjectDevice.objects.create(
                type = device_type,
                model = device_model,
                object = new_object,
            )

                
        pass
        


class ObjectIdView(LoginRequiredMixin, DetailView):
    model = Object
    pk_url_kwarg = 'id'
    template_name = "app/object/id.html"

class ContractCreateView(LoginRequiredMixin, TemplateView):

    @property
    def id(self):
       return self.kwargs['id']

    template_name = "app/contract/create.html"
    extra_context = {
        'contract_form': ContractCreateForm,
    }

    def post(self, request, id):

        current_object = Object.objects.filter(pk=id)

        client = Client.objects.filter(object=id, role="Собственник")


        contract_data = request.POST.dict()

        contract_full_date_str = '%02d.%02d.%d' % (int(contract_data['date_day']), int(contract_data['date_month']), int(contract_data['date_year']))
        contract_full_date_str_for_db = '%02d-%02d-%d' % (int(contract_data['date_year']), int(contract_data['date_month']), int(contract_data['date_day']))
        contract_full_date_month = transform_date_month(contract_full_date_str)

        number_month = contract_data['date_month']
        if (len(number_month) < 2):
            number_month = '0' + number_month

            
        getted_date_str = '%02d.%02d.%d' % (int(current_object[0].passport.getted_date.day), int(current_object[0].passport.getted_date.month), int(current_object[0].passport.getted_date.year))

        summ_words = num2words(3104, lang='ru')

        data = {
            **contract_data,
            'full_month': contract_full_date_month,
            'number_month': number_month,
            'object_id': id,
            'f': client[0].lastname,
            'i': client[0].firstname,
            'o': client[0].middlename,
            'full_address': get_full_address(data=current_object[0]),
            'initials': f'{client[0].lastname} {client[0].firstname[:1]}. {client[0].middlename[:1]}.',
            'phone_number': client[0].phone_set.all()[0].phone_number,
            'passport': current_object[0].passport,
            'getted_date': getted_date_str,
            'summ': 3104,
            'summ_words': summ_words

        }

        print(data)

        generate_docx(data)

        Contract.objects.create(contract_number=data['contract_number'], date=contract_full_date_str_for_db, summ=0.00, object=current_object[0], status="active")


        # return redirect(f'/objects/{id}')
