# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, datetime, date

import pytz
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper
from products.forms import SupplyForm, SuppliesCategoryForm, CartridgeForm, SuppliersForm, RecipeForm
from products.models import Cartridge, Supply, SuppliesCategory, CartridgeRecipe
from kitchen.models import Warehouse
from sales.models import TicketDetail, Ticket
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView

import math


# -------------------------------------  Class based Views -------------------------------------

class ProductsHelper(object):
    def __init__(self):
        self.__required_supplies_list = None
        self.__predictions = None
        self.__all_cartridges = None
        self.__today_popular_cartridge = None
        self.__always_popular_cartridge = None
        self.__all_tickets_details = None
        super(ProductsHelper, self).__init__()

    def get_required_supplies(self):
        self.__required_supplies_list = []
        self.__predictions = self.get_prediction_supplies()
        self.__all_cartridges = Cartridge.objects.all()
        for prediction in self.__predictions:
            for cartridge in self.__all_cartridges:
                if prediction['name'] == cartridge.name:
                    ingredients = CartridgeRecipe.objects.filter(cartridge=cartridge)

                    for ingredient in ingredients:
                        name = ingredient.supply.name
                        cost = ingredient.supply.presentation_cost
                        measurement = ingredient.supply.measurement_unit
                        measurement_quantity = ingredient.supply.measurement_quantity
                        quantity = ingredient.quantity

                        count = 0

                        required_supply_object = {
                            'name': name,
                            'cost': cost,
                            'measurement': measurement,
                            'measurement_quantity': measurement_quantity,
                            'quantity': quantity,
                        }

                        if len(self.__required_supplies_list) == 0:
                            count = 1
                        else:
                            for required_supplies in self.__required_supplies_list:
                                if required_supplies['name'] == name:
                                    required_supplies['quantity'] += quantity
                                    count = 0
                                    break
                                else:
                                    count = 1
                        if count == 1:
                            self.__required_supplies_list.append(required_supply_object)

        return self.__required_supplies_list

    def set_all_tickets_details(self, initial_date=None, final_date=None):
        if initial_date is None and final_date is None:
            self.__all_tickets_details = TicketDetail.objects.prefetch_related(
                'ticket').prefetch_related('cartridge').prefetch_related('package_cartridge').all()
        else:
            self.__all_tickets_details = TicketDetail.objects.prefetch_related(
                'ticket').prefetch_related('cartridge').prefetch_related('package_cartridge').filter(
                ticket__created_at__range=[initial_date, final_date])

    def set_all_cartridges(self):
        self.__all_cartridges = Cartridge.objects.all()

    def set_always_popular_cartridge(self):
        cartridges_frequency_dict = {}
        for cartridge in self.__all_cartridges:
            cartridges_frequency_dict[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }
        for ticket_detail in self.__all_tickets_details:
            if ticket_detail.cartridge:
                ticket_detail_id = ticket_detail.cartridge.id
                ticket_detail_frequency = ticket_detail.quantity
                cartridges_frequency_dict[ticket_detail_id]['frequency'] += ticket_detail_frequency

        for element in cartridges_frequency_dict:
            if self.__always_popular_cartridge is None:
                """ Base case """
                self.__always_popular_cartridge = {
                    'id': element,
                    'name': cartridges_frequency_dict[element]['name'],
                    'frequency': cartridges_frequency_dict[element]['frequency'],
                }
            else:
                if cartridges_frequency_dict[element]['frequency'] > self.__always_popular_cartridge['frequency']:
                    self.__always_popular_cartridge = {
                        'id': element,
                        'name': cartridges_frequency_dict[element]['name'],
                        'frequency': cartridges_frequency_dict[element]['frequency'],
                    }

    def set_today_popular_cartridge(self):
        cartridges_frequency_dict = {}
        helper = Helper()
        start_date = helper.naive_to_datetime(date.today())
        limit_day = helper.naive_to_datetime(start_date + timedelta(days=1))
        self.set_all_tickets_details(start_date, limit_day)

        for cartridge in self.__all_cartridges:
            cartridges_frequency_dict[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }

        for ticket_detail in self.__all_tickets_details:
            if ticket_detail.cartridge:
                ticket_detail_id = ticket_detail.cartridge.id
                ticket_detail_frequency = ticket_detail.quantity
                cartridges_frequency_dict[ticket_detail_id]['frequency'] += ticket_detail_frequency

        for element in cartridges_frequency_dict:
            if self.__today_popular_cartridge is None:
                """ Base case """
                self.__today_popular_cartridge = {
                    'id': element,
                    'name': cartridges_frequency_dict[element]['name'],
                    'frequency': cartridges_frequency_dict[element]['frequency'],
                }
            else:
                if cartridges_frequency_dict[element]['frequency'] > self.__today_popular_cartridge['frequency']:
                    self.__today_popular_cartridge = {
                        'id': element,
                        'name': cartridges_frequency_dict[element]['name'],
                        'frequency': cartridges_frequency_dict[element]['frequency'],
                    }

    @staticmethod
    def get_supplies_on_stock():
        stock_list = []
        elements = Warehouse.objects.all()
        if elements.count() > 0:
            for element in elements:
                stock_object = {
                    'name': element.supply.name,
                    'quantity': element.quantity,
                }

                stock_list.append(stock_object)

        return stock_list

    @staticmethod
    def get_prediction_supplies():
        prediction = []

        TicketsDetails = TicketDetail.objects.all()
        for TicketsDetail in TicketsDetails:
            cartridge_object = {
                'name': TicketsDetail.cartridge.name,
                'cantidad': 1,
            }

            prediction.append(cartridge_object)

        return prediction

    def get_all_tickets_details(self):
        return self.__all_tickets_details

    def get_all_cartridges(self):
        return self.__all_cartridges

    def get_always_popular_cartridge(self):
        self.set_always_popular_cartridge()
        return self.__always_popular_cartridge

    def get_today_popular_cartridge(self):
        return self.__always_popular_cartridge


class CreateSupply(CreateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('products:supplies')


class UpdateSupply(UpdateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('products:supplies')


class DeleteSupply(DeleteView):
    model = Supply
    template_name = 'supplies/delete_supply.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect('/supplies/')


class CreateCartridge(CreateView):
    model = Cartridge
    fields = ['name', 'price', 'category', 'image']
    template_name = 'cartridges/new_cartridge.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/cartridges/')


class UpdateCartridge(UpdateView):
    model = Cartridge
    fields = ['name', 'price', 'category', 'image']
    template_name = 'cartridges/new_cartridge.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/cartridges/')


class DeleteCartridge(DeleteView):
    model = Cartridge
    template_name = 'cartridges/delete_cartridge.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = self.get_object()

    def delete(self, request, *args, **kwargs):
        self.object.delete()
        return redirect('/cartridges/')


class CreateSupplier(CreateView):
    model = Supplier
    fields = ['name', 'image']
    template_name = 'supplies/new_category.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/supplies/')


class CreateCategory(CreateView):
    model = SuppliesCategory
    fields = ['name', 'image']
    template_name = 'supplies/new_supplier.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/supplies/')


# -------------------------------------  Profile -------------------------------------


# -------------------------------------  Providers -------------------------------------


@login_required(login_url='users:login')
def suppliers(request):
    suppliers_list = Supplier.objects.order_by('id')
    template = 'suppliers/suppliers.html'
    title = 'Proveedores'
    context = {
        'suppliers': suppliers_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)
# -------------------------------------  Supplies -------------------------------------


@login_required(login_url='users:login')
def supplies(request):
    supplies_objects = Supply.objects.order_by('id')
    template = 'supplies/supplies.html'
    title = 'Insumos'
    context = {
        'supplies': supplies_objects,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_supply(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST, request.FILES)
        if form.is_valid():
            supply = form.save(commit=False)
            supply.save()
            return redirect('/supplies/')
    else:
        form = SupplyForm()

    template = 'supplies/new_supply.html'
    title = 'DabbaNet - Nuevo insumo'
    categories_list = SuppliesCategory.objects.order_by('name')
    suppliers_list = Supplier.objects.order_by('name')
    context = {
        'categories': categories_list,
        'suppliers': suppliers_list,
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def supply_detail(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    template = 'supplies/supply_detail.html'
    title = 'DabbaNet - Detalles del insumo'
    context = {
        'page_title': PAGE_TITLE,
        'supply': supply,
        'title': title
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def supply_modify(request, pk):
    supply = get_object_or_404(Supply, pk=pk)

    if request.method == 'POST':
        form = SupplyForm(request.POST, request.FILES)

        if form.is_valid():
            nuevo = form.save(commit=False)
            supply.name = nuevo.name
            supply.category = nuevo.category
            supply.barcode = nuevo.barcode
            supply.supplier = nuevo.suppliter
            supply.storage_required = nuevo.storage_required
            supply.presentation_unit = nuevo.presentation_unit
            supply.presentation_cost = nuevo.presentation_cost
            supply.measurement_quantity = nuevo.measurement_quantity
            supply.measurement_unit = nuevo.measurement_unit
            supply.optimal_duration = nuevo.optimal_duration
            supply.optimal_duration_unit = nuevo.optimal_duration_unit
            supply.location = nuevo.location
            supply.image = nuevo.image
            supply.save()

            return redirect('/supply')

    else:
        dic = {
            'name': supply.name,
            'category': supply.category,
            'barcode': supply.barcode,
            'supplier': supply.supplier,
            'storage_required': supply.storage_required,
            'presentation_unit': supply.presentation_unit,
            'presentation_cost': supply.presentation_cost,
            'quantity': supply.measurement_quantity,
            'measurement_unit': supply.measurement_unit,
            'optimal_duration': supply.optimal_duration,
            'optimal_duration_unit': supply.optimal_duration_unit,
            'location': supply.location,
            'image': supply.image,
        }
        form = SupplyForm(initial=dic)

    template = 'supplies/new_supply.html'
    title = 'Modificar Insumo'
    context = {
        'form': form,
        'supply': supply,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)
# ------------------------------------- Categories -------------------------------------


@login_required(login_url='users:login')
def categories(request):
    supplies_categories = SuppliesCategory.objects.order_by('id')
    template = 'categories/categories.html'
    title = 'Categorias'
    context = {
        'supplies_categories': supplies_categories,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_category(request):
    if request.method == 'POST':
        form = SuppliesCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('/categories')
    else:
        form = SuppliesCategoryForm()

    template = 'categories/new_category.html'
    title = 'Nueva Categoria'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def categories_supplies(request, categ):
    supplies_categories = SuppliesCategoryForm.objects.filter(name=categ)
    supply = Supply.objects.filter(category=supplies_categories)
    template = 'supplies/supplies.html'
    title = categ
    context = {
        'supply': supply,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)
# -------------------------------------  Cartridges -------------------------------------


@login_required(login_url='users:login')
def cartridges(request):
    cartridges_list = Cartridge.objects.order_by('id')
    template = 'cartridges/cartridges.html'
    title = 'Cartuchos'
    context = {
        'cartridges': cartridges_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_cartridge(request):
    if request.method == 'POST':
        form = CartridgeForm(request.POST, request.FILES)
        if form.is_valid():
            cartridge = form.save(commit=False)
            cartridge.save()
            return redirect('/cartridges')
    else:
        form = CartridgeForm()

    template = 'cartridges/new_cartridge.html'
    title = 'Nuevo Cartucho'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def cartridge_detail(request, pk):
    cartridge = get_object_or_404(Cartridge, pk=pk)
    template = 'cartridges/cartridge_detail.html'
    title = 'DabbaNet - Detalles del Producto'
    context = {
        'page_title': PAGE_TITLE,
        'cartridge': cartridge,
        'title': title
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def cartridge_recipe(request, pk):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.save()
            return redirect('/cartridges')
    else:
        form = RecipeForm()

    template = 'cartridges/cartridge_recipe.html'
    title = 'Nuevo Receta'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


# -------------------------------------  Suppliers and  -------------------------------------

def cartridge_modify(request, pk):
    cartridge = get_object_or_404(Cartridge, pk=pk)

    if request.method == 'POST':
        form = CartridgeForm(request.POST, request.FILES)

        if form.is_valid():
            nuevo = form.save(commit=False)
            cartridge.name = nuevo.name
            cartridge.price = nuevo.price
            cartridge.category = nuevo.category
            cartridge.save()
            return redirect('/cartridges')

    else:
        dic = {
            'name': cartridge.name,
            'price': cartridge.price,
            'category': cartridge.category,
            'image': cartridge.image
        }
        form = CartridgeForm(initial=dic)

    template = 'cartridges/new_cartridge.html'
    title = 'Modificar Cartucho'
    context = {
        'form': form,
        'cartridge': cartridge,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_supplier(request):
    if request.method == 'POST':
        form = SuppliersForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.save()
            return redirect('/suppliers')
    else:
        form = SuppliersForm()

    template = 'suppliers/new_supplier.html'
    title = 'Nuevo Proveedor'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


# -------------------------------------  Catering -------------------------------------
@login_required(login_url='users:login')
def catering(request):
    helper = Helper()
    products_helper = ProductsHelper()
    products_helper.set_all_tickets_details()
    products_helper.set_all_cartridges()

    def average_sales():
        start_date = helper.naive_to_datetime(date.today())
        limit_day = helper.naive_to_datetime(start_date + timedelta(days=1))
        products_helper.set_all_tickets_details(start_date, limit_day)
        all_cartridges_dict = {}

        for cartridge in products_helper.get_all_cartridges():
            all_cartridges_dict[cartridge.id] = {
                'name': cartridge.name,
                'quantity': 0,
                'average': 0,
                'total_tickets_appears': 0,
            }

        for ticket_detail in products_helper.get_all_tickets_details():
            pass
        return True

    def get_always_popular_cartridge():
        return products_helper.get_always_popular_cartridge()

    def get_today_popular_cartridge():
        products_helper.set_today_popular_cartridge()
        return products_helper.get_today_popular_cartridge()

    average_sales = average_sales()
    required_supplies = products_helper.get_required_supplies()
    supplies_on_stock = products_helper.get_supplies_on_stock()
    estimated_total_cost = 0

    for required_supply in required_supplies:
        required_supply['stock'] = 0
        for supply in supplies_on_stock:
            if supply['name'] == required_supply['name']:
                required_supply['stock'] = supply['quantity']
            else:
                required_supply['stock'] = 0

        required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
        required_supply['full_cost'] = required_supply['cost'] * (math.ceil(required_supply['required'] / required_supply['measurement_quantity']))
        estimated_total_cost = estimated_total_cost + required_supply['full_cost']

    template = 'catering/catering.html'
    title = 'Abastecimiento'
    context = {
        'title': title,
        'required_supplies': required_supplies,
        'estimated_total_cost': estimated_total_cost,
        'page_title': PAGE_TITLE,
        'always_popular_cartridge': get_always_popular_cartridge(),
        'today_popular_cartridge': get_today_popular_cartridge(),
    }

    return render(request, template, context)


''' 
    TODO: Media para predicción.
    TODO: Ordenar por prioridad.
'''


def test(request):
    variable_chida = '1'
    # template = 'base/base_nav_footer.html'

    def otra_funcion():
        variable_chida = '2'
        return variable_chida

    def mi_funcion():
        variable_chida = '3'
        print(variable_chida)
        variable_chida = otra_funcion()
        print(variable_chida)

    mi_funcion()

    print('FIN: ', variable_chida)
    return HttpResponse('jeje')