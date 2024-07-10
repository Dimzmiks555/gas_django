from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, View, TemplateView
from .models import Object, Client, Passport, ObjectDevice, DeviceModel, DeviceType, Contract, DeviceKind, DeviceManufacter, DeviceModification, ActPosition, Act, Master
from .forms import LoginUserForm, ObjectCreateForm, PassportCreateForm, ClientFormSet, ContractCreateForm, ObjectDeviceFormSet, ActCreateForm, PositionFormSet
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import datetime
from .utils import generate_docx, get_pricelist_array, transform_date_month, get_full_address, generate_act
from num2words import num2words
from django.db.models import Q







class Login(LoginView):
    form_class = LoginUserForm
    template_name = "login.html"

def Index(request):
    return redirect('/objects')

class ObjectListView(LoginRequiredMixin, ListView):
    template_name = "app/object/list.html"
    model = Object

    def get_queryset(self):
        last_name = self.request.GET.get('last_name')
        first_name = self.request.GET.get('first_name')
        middle_name = self.request.GET.get('middle_name')
        phone_number = self.request.GET.get('phone_number')

        region = self.request.GET.get('region')
        city = self.request.GET.get('city')
        area = self.request.GET.get('area')
        street = self.request.GET.get('street')
        house = self.request.GET.get('house')
        room = self.request.GET.get('room')

        clients_filter = {}

        if last_name:
            clients_filter["lastname__contains"] = last_name
        if first_name:
            clients_filter["firstname__contains"] = first_name
        if middle_name:
            clients_filter["middlename__contains"] = middle_name

        clients_query = Q(**clients_filter)
        
        if phone_number:
            local_query = Q(phone_number_1__contains=phone_number)
            local_query.add(Q(phone_number_2__contains=phone_number), Q.OR)
            local_query.add(Q(phone_number_3__contains=phone_number), Q.OR)
            clients_query.add(local_query, Q.AND)


        clients = Client.objects.filter(clients_query)

        filter_object = {
            "client__in": clients
        }


        if region:
            filter_object["region__contains"] = region
        if area:
            filter_object["area__contains"] = area
        if city:
            filter_object["city__contains"] = city
        if street:
            filter_object["street__contains"] = street
        if house:
            filter_object["house__contains"] = house
        if room:
            filter_object["room__contains"] = room


        # print(last_name)

        return Object.objects.filter(Q(**filter_object)).order_by('-pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_formset'] = ObjectDeviceFormSet(queryset=ObjectDevice.objects.none())
        if self.queryset:
            context['total'] = self.queryset.count()
        else:
            context['total'] = 0
        return context


class ObjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = "app/object/create.html"
    extra_context = {
        'object_form': ObjectCreateForm,
        'passport_form': PassportCreateForm,
        # 'phone_form': PhoneCreateForm,
        # 'client_form' : ClientCreateForm,
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_formset'] = ObjectDeviceFormSet(queryset=ObjectDevice.objects.none())
        context['client_formset'] = ClientFormSet(queryset=Client.objects.none(), prefix='client')
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


        # new_phone = Phone.objects.create(
        #     phone_number = data['phone_number'],
        #     client = new_client,
        # )

        
        new_passport = Passport.objects.create(
            serial = data['serial'],
            passport_number = data['passport_number'],
            getted_by = data['getted_by'],
            division = data['division'],
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
        for device in devices:

            device_type = DeviceType.objects.filter(pk=int(devices[device]['type']))[0]
            device_model = DeviceModel.objects.filter(pk=int(devices[device]['model']))[0] if devices[device]['model'] else  None
            device_kind = DeviceKind.objects.filter(pk=int(devices[device]['kind']))[0] if devices[device]['kind'] else  None
            device_manufacter = DeviceManufacter.objects.filter(pk=int(devices[device]['manufacter']))[0] if devices[device]['manufacter'] else  None
            device_modification = DeviceModification.objects.filter(pk=int(devices[device]['modification']))[0] if devices[device]['modification'] else  None

            ObjectDevice.objects.create(
                type = device_type,
                model = device_model,
                modification = device_modification,
                kind = device_kind,
                manufacter = device_manufacter,
                object = new_object,
            )

        
        clients = {}


        for key in data.keys():
            if key.startswith('client') and key[7].isdigit():
                if key[7] in clients:
                    clients[key[7]][key[9:]] = data[key]
                else:
                    clients[key[7]] = {
                        key[9:]: data[key]
                    }
        for client in clients:
            print(clients[client])
            Client.objects.create(
                firstname = clients[client]['firstname'],
                lastname = clients[client]['lastname'],
                middlename = clients[client]['middlename'],
                # is_main = True,
                is_main = True if clients[client]['is_main'] == 'on' else False,
                role = clients[client]['role'],
                sex = clients[client]['sex'],
                phone_number_1 = clients[client]['phone_number_1'],
                phone_number_2 = clients[client]['phone_number_2'],
                phone_number_3 = clients[client]['phone_number_3'],
                object = new_object,
            )
                
        pass
        


class ObjectIdView(LoginRequiredMixin, DetailView):
    model = Object
    pk_url_kwarg = 'id'
    template_name = "app/object/id.html"


    


class ActCreateFromContractView(LoginRequiredMixin, TemplateView):
    @property
    def id(self):
       return self.kwargs['id']
    
    template_name = "app/act/create_from_contract.html"
    extra_context = {
        'act_form': ActCreateForm,
    }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['position_formset'] = PositionFormSet()

        current_object = Object.objects.filter(pk=self.kwargs['id'])[0]
        
        prices = get_pricelist_array(current_object)

        total_summ = 0
        for p in prices:
            total_summ += prices[p]['total']

        positions = []
        for p in prices:
            if prices[p]['amount'] > 0:
                positions.append(prices[p])

        
        # actual_contract = Contract.objects.filter(object=current_object, status="active")[0]
        
        # context['actual_contract'] = actual_contract
        context['total_summ'] = total_summ
        context['positions'] = positions

        return context
    
    def post(self, request, id):

        current_object = Object.objects.filter(pk=id)
        client = Client.objects.filter(object=id, role="Собственник")
        actual_contract = Contract.objects.filter(object=current_object[0], status="active")[0]

        act_data = request.POST.dict()

        contract_full_date_month = transform_date_month(actual_contract.date_of_contract.strftime('%Y-%m-%d'), '-')
        act_full_date_str = '%02d.%02d.%d' % (int(act_data['date_day']), int(act_data['date_month']), int(act_data['date_year']))
        act_full_date_str_for_db = '%02d-%02d-%d' % (int(act_data['date_year']), int(act_data['date_month']), int(act_data['date_day']))
        act_full_date_month = transform_date_month(act_full_date_str, '.')


        number_month = str(actual_contract.date_of_contract.month)
        if (len(number_month) < 2):
            number_month = '0' + number_month

            
        getted_date_str = '%02d.%02d.%d' % (int(current_object[0].passport.getted_date.day), int(current_object[0].passport.getted_date.month), int(current_object[0].passport.getted_date.year))

        prices = get_pricelist_array(current_object[0])

        total_summ = 0

        for p in prices:
            total_summ += prices[p]['total']

        master = Master.objects.filter(pk=act_data['master'])[0]

        data = {
            **act_data,
            'contract_number': actual_contract.contract_number,
            'contract_day': str(actual_contract.date_of_contract.day),
            'contract_full_month': contract_full_date_month,
            'full_month': act_full_date_month,
            'contract_year': str(actual_contract.date_of_contract.year),
            'number_month': number_month,
            'object_id': id,
            'f': client[0].lastname,
            'i': client[0].firstname,
            'o': client[0].middlename,
            'full_address': get_full_address(data=current_object[0]),
            'initials': f'{client[0].lastname} {client[0].firstname[:1]}. {client[0].middlename[:1]}.',
            'master_initials': f'{master.lastname} {master.firstname[:1]}. {master.middlename[:1]}.',
            'phone_number': client[0].phone_number_1,
            'passport': current_object[0].passport,
            'getted_date': getted_date_str,
            'summ': total_summ,
            'devices': current_object[0].objectdevice_set.all(),
            'prices': prices

        }

        print(act_data['master'])

        new_act = Act.objects.create(act_number=data['act_number'], date_of_act=act_full_date_str_for_db, total=total_summ, object=current_object[0], master = master)

        generate_act(data, new_act.uuid_number)

        

        return redirect(f'/objects/{id}')


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
        # client = Client.objects.filter(object=id)


        contract_data = request.POST.dict()

        contract_full_date_str = '%02d.%02d.%d' % (int(contract_data['date_day']), int(contract_data['date_month']), int(contract_data['date_year']))
        contract_full_date_str_for_db = '%02d-%02d-%d' % (int(contract_data['date_year']), int(contract_data['date_month']), int(contract_data['date_day']))
        contract_full_date_month = transform_date_month(contract_full_date_str, '.')

        number_month = contract_data['date_month']
        if (len(number_month) < 2):
            number_month = '0' + number_month

            
        getted_date_str = '%02d.%02d.%d' % (int(current_object[0].passport.getted_date.day), int(current_object[0].passport.getted_date.month), int(current_object[0].passport.getted_date.year))


        prices = get_pricelist_array(current_object[0])

        total_summ = 0

        for p in prices:
            total_summ += prices[p]['total']

        summ_words = num2words(int(total_summ), lang='ru')

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
            'phone_number': client[0].phone_number_1,
            'passport': current_object[0].passport,
            'getted_date': getted_date_str,
            'summ': total_summ,
            'summ_words': summ_words,
            'devices': current_object[0].objectdevice_set.all(),
            'prices': prices

        }

        print(data)

        actual_contract = Contract.objects.filter(status="active", object=id)

        if actual_contract.count() > 0:
            # actual_contract[0].status = 'idle'
            actual_contract.update(status="idle")

        # print(actual_contract[0].status)

        new_contract = Contract.objects.create(contract_number=data['contract_number'], date_of_contract=contract_full_date_str_for_db, summ=total_summ, object=current_object[0], status="active")

        generate_docx(data, new_contract.uuid_number)



        

        return redirect(f'/objects/{id}')
