# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, datetime, date

import pytz
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
        super(ProductsHelper, self).__init__()

    def get_required_supplies(self):
        required_supplies_list = []
        predictions = self.get_prediction_supplies()
        cartridges = Cartridge.objects.all()

        for prediction in predictions:
            for cartridge in cartridges:
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

                        if len(required_supplies_list) == 0:
                            count = 1
                        else:
                            for required_supplies in required_supplies_list:
                                if required_supplies['name'] == name:
                                    required_supplies['quantity'] += quantity
                                    count = 0
                                    break
                                else:
                                    count = 1
                        if count == 1:
                            required_supplies_list.append(required_supply_object)

        return required_supplies_list

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


def test(request):
    # template = 'base/base_nav_footer.html'
    template = 'base/nav.html'
    return render(request, template, {})
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
    
    products_helper = ProductsHelper()

    def get_popular_cartridge():
        all_tickets_details = TicketDetail.objects.all()
        all_cartridges = Cartridge.objects.all()
        popular_cartridge = None
        cartridges_frequency_list = {}

        for cartridge in all_cartridges:
            cartridges_frequency_list[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }

        for ticket_detail in all_tickets_details:
            if ticket_detail.cartridge:
                id = ticket_detail.cartridge.id
                frecuency = ticket_detail.quantity
                cartridges_frequency_list[id]['frequency'] += frecuency

        for element in cartridges_frequency_list:
            if popular_cartridge is None:
                """ Base case """
                popular_cartridge = {
                    'id': element,
                    'name': cartridges_frequency_list[element]['name'],
                    'frequency': cartridges_frequency_list[element]['frequency'],
                }
            else:
                if cartridges_frequency_list[element]['frequency'] > popular_cartridge['frequency']:
                    popular_cartridge = {
                        'id': element,
                        'name': cartridges_frequency_list[element]['name'],
                        'frequency': cartridges_frequency_list[element]['frequency'],
                    }
        return popular_cartridge

    def get_popular_cartridge_today():
        start_date = date.today()
        limit_day = start_date + timedelta(days=1)
        all_tickets_details = TicketDetail.objects.prefetch_related('ticket').filter(
            ticket__created_at__range=[start_date, limit_day])
        all_cartridges = Cartridge.objects.all()
        popular_cartridge = None
        cartridges_frequency_list = {}

        for cartridge in all_cartridges:
            cartridges_frequency_list[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }

        for ticket_detail in all_tickets_details:
            if ticket_detail.cartridge:
                id = ticket_detail.cartridge.id
                frecuency = ticket_detail.quantity
                cartridges_frequency_list[id]['frequency'] += frecuency

        for element in cartridges_frequency_list:
            if popular_cartridge is None:
                """ Base case """
                popular_cartridge = {
                    'id': element,
                    'name': cartridges_frequency_list[element]['name'],
                    'frequency': cartridges_frequency_list[element]['frequency'],
                }
            else:
                if cartridges_frequency_list[element]['frequency'] > popular_cartridge['frequency']:
                    popular_cartridge = {
                        'id': element,
                        'name': cartridges_frequency_list[element]['name'],
                        'frequency': cartridges_frequency_list[element]['frequency'],
                    }
        return popular_cartridge

    popular_cartridge_today = get_popular_cartridge_today()

    popular_cartridge_always = get_popular_cartridge()

    estimated_total_cost = 0

    required_supplies = products_helper.get_required_supplies()

    supplies_on_stock = products_helper.get_supplies_on_stock()

    for required in required_supplies:

        for supplies in supplies_on_stock:
            if (supplies['name'] == required['name']):
                required['stock'] = supplies['quantity']
            else:
                required['stock'] = 0

        required['required'] = max(0, required['quantity'] - required['stock'])
        required['full_cost'] = required['cost'] * (math.ceil(required['required'] / required['measurement_quantity']))
        estimated_total_cost = estimated_total_cost + required['full_cost']

    template = 'catering/catering.html'
    title = 'Abastecimiento'
    context = {
        'title': title,
        'required_supplies': required_supplies,
        'estimated_total_cost': estimated_total_cost,
        'page_title': PAGE_TITLE, 
        'popular_cartridge_always': popular_cartridge_always,
        'popular_cartridge_today': popular_cartridge_today,
    }
    
    return render(request, template, context)


''' 
    TODO: Media para predicción.
    TODO: Ordenar por prioridad.
'''
