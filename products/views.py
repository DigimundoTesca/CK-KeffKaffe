# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from products.forms import SupplyForm, SuppliesCategoryForm, CartridgeForm, SuppliersForm, RecipeForm
from products.models import Cartridge, Supply, SuppliesCategory, CartridgeRecipe
from kitchen.models import Warehouse
from sales.models import TicketDetail
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView

import math


# -------------------------------------  Class based Views -------------------------------------
class CreateSupply(CreateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/supplies/')


class UpdateSupply(UpdateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

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

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/cartridges/')


class UpdateCartridge(UpdateView):
    model = Cartridge
    fields = ['name', 'price', 'category', 'image']
    template_name = 'cartridges/new_cartridge.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('/cartridges/')


class DeleteCartridge(DeleteView):
    model = Cartridge
    template_name = 'cartridges/delete_cartridge.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect('/cartridges/')


class CreateSupplier(CreateView):
    model = Supplier
    fields = ['name', 'image']
    template_name = 'supplies/new_category.html'

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


def test(request):
    # template = 'base/base_nav_footer.html'
    template = 'base/nav.html'
    return render(request, template, {})


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


# -------------------------------------  Suppliers and  -------------------------------------

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

class CateringHelper(object):
    """Catering Helpers """

    def __init__(self):
        super(CateringHelper, self).__init__()

    def get_start_week_day(self, day):
        format = "%w"
        number_day = int(self.naive_to_datetime(day).strftime(format))
        if number_day == 0:
            number_day = 7
        else:
            day = self.naive_to_datetime(day) - timedelta(days=number_day - 1)

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

                        cont = 0;

                        required_suppply_object = {
                            'name': name,
                            'cost': cost,
                            'measurement': measurement,
                            'measurement_quantity': measurement_quantity,
                            'quantity': quantity,
                        }

                        if (len(required_supplies_list) == 0):
                            count = 1;
                        else:
                            for required_supplies in required_supplies_list:
                                if required_supplies['name'] == name:
                                    required_supplies['quantity'] += quantity
                                    count = 0
                                    break
                                else:
                                    count = 1
                        if (count == 1):
                            required_supplies_list.append(required_suppply_object)

        return required_supplies_list

    def get_supplies_on_stock(self):

        stock_list = []
        elements = Warehouse.objects.all()
        for element in elements:
            stock_object = {
                'name': element.supply.name,
                'quantity': element.quantity,
            }

            stock_list.append(stock_object)

        return stock_list

    def get_prediction_supplies(self):
        prediction = []

        TicketsDetails = TicketDetail.objects.all()

        for TicketsDetail in TicketsDetails:
            cartridge_object = {
                'name': TicketsDetail.cartridge.name,
                'cantidad': 1,
            }

            prediction.append(cartridge_object)

        return prediction


@login_required(login_url='users:login')
def catering(request):
    helper = CateringHelper()

    total_cost = 0

    required_supplies = helper.get_required_supplies()

    supplies_on_stock = helper.get_supplies_on_stock()
    for required in required_supplies:

        for supplies in supplies_on_stock:
            if (supplies['name'] == required['name']):
                required['stock'] = supplies['quantity']
            else:
                required['stock'] = 0

        required['required'] = max(0, required['quantity'] - required['stock'])
        required['full_cost'] = required['cost'] * (math.ceil(required['required'] / required['measurement_quantity']))
        total_cost = total_cost + required['full_cost']

    template = 'catering/catering.html'
    title = 'Abastecimiento'
    context = {
        'title': title,
        'required_supplies': required_supplies,
        'total_cost': total_cost,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


''' 
    TODO: Media para predicción.
    TODO: Filtros por día.
    TODO: Ordenar por prioridad.

'''
