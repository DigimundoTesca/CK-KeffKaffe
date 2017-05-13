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
from products.forms import SupplyForm, SuppliesCategoryForm, CartridgeForm, SuppliersForm, RecipeForm, WarehouseForm
from products.models import Cartridge, Supply, SuppliesCategory, CartridgeRecipe
from kitchen.models import Warehouse, WarehouseDetails
from sales.models import TicketDetail, Ticket
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView

import math


# -------------------------------------  Class based Views -------------------------------------


class LeastSquares(object):
    """
    Object to obtain the least squares in a general way 
    :type x: period list
    :type y: 
    The formula to obtains A:
        Average(Y) - B(Average(X))

    The formula to obtains B:
        Sum(X * Y) - ((Sum(X)*Sum(Y))/n)/(Sum(X^2) - (Sum(X)^2)/n 

        * Where n = lenght of the list for period

    The formula to do de forecast it's gonna be:
        A + B(Period)
    """
    def __init__(self, x:list, y:list):

        super(LeastSquares, self).__init__()
        if len(x) != len(y):
            raise NameError('Las listas deben tener misma longitud.')

        self.__x = x
        self.__y = y
        self.__periodic_list = []
        self.__n = len(self.__x)
        self.set_periodic_list()
    
    def get_sum_x(self):
        """
        Obtains the sum of the elements in the list X
        """
        return sum(self.__x)
    
    def get_sum_y(self):
        """
        Obtains the sum of the elements in the list Y
        """
        return sum(self.__y)

    def get_x_average(self):
        """
        Obtains the average of the elements in the X list
        """
        return math.ceil(self.get_sum_x() / len(self.__x))

    def get_y_average(self):
        """
        Obtains the average of the elements in the Y list
        """
        return math.ceil(self.get_sum_y() / len(self.__y))

    def get_sum_x_pow(self):
        """
        Obtains the sum of the square pow from the elements of X
        """
        auxiliar_list = []
        count = 0

        for day in self.__x:
            auxiliar_list.append(self.__x[count]**2)
            count += 1
        return sum(auxiliar_list)

    def get_sum_y_pow(self):
        """
        Obtains the sum of the square pow from the elements of X
        """
        auxiliar_list = []
        count = 0

        for element in self.__y:
            auxiliar_list.append(self.__y[count]**2)
            count += 1
        return sum(auxiliar_list)

    def get_sum_x_y_prod(self):
        """
        Obtains the sum of the product between elements in the list of X and Y
        """
        count = 0
        auxiliar_list = [] 

        for item in self.__x:
            auxiliar_list.append(self.__x[count]*self.__y[count])
            count += 1
        return sum(auxiliar_list)

    def set_periodic_list(self):
        """
        This method gives the indicators to know if the given lists are or not periodic
        """
        difference_list = []
        count = 0
        is_periodic = True

        for _ in self.__x:
            if count != 0:
                difference_list.append(self.__x[count] - self.__x[count - 1])
            
            count += 1

        count = 0

        for item in difference_list:
            if count != 0:
                if difference_list[count] != difference_list[count-1]:
                    is_periodic = False
                    break
            count += 1

        if is_periodic:
            count = 0
            periodic_value = difference_list[0]

            for _ in self.__x:
                self.__periodic_list.append(self.__x[len(self.__x) - 1] + periodic_value * (count + 1))
                count += 1
        else:
            raise NameError('Tu lista de Periodo no es continua')

    def get_A(self):
        """
        This give us the valor of A for the mathematical method
        """
        return math.ceil(self.get_y_average() - self.get_B() * self.get_x_average())

    def get_B(self):
        """
        This give us the valor of B for the mathematical method
        """
        return math.ceil((self.get_sum_x_y_prod() - (self.get_sum_x() * self.get_sum_y() / self.__n) ) / (self.get_sum_x_pow() - (self.get_sum_x() ** 2) / self.__n ))

    def get_forecast(self):
        """
        This method give us the forecast for next week or case that we are gonna evaluate
        """
        forecast_list = []
        count = 0

        for item in self.__x:
            forecast_list.append(self.get_A() + self.get_B() * self.__periodic_list[count])
            count += 1

        return forecast_list


def main():
    lista_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    lista_y = [90, 106, 152, 244, 302, 274, 162, 194, 312, 359, 215, 126]

    xd = LeastSquares(lista_x, lista_y)
    print('Suma de x:\t\t', xd.get_sum_x())
    print('Suma de y:\t\t', xd.get_sum_y())
    print('Suma de x al cuadrado:\t', xd.get_sum_x_pow())
    print('Promedio de x:\t\t', xd.get_x_average())
    print('Promedio de y:\t\t', xd.get_y_average())
    print('Suma de y al cuadrado:\t', xd.get_sum_y_pow())
    print('Suma del producto del X y Y:\t', xd.get_sum_x_y_prod())
    print('*'*50)
    print('A:\t\t', xd.get_A())
    print('B:\t\t', xd.get_B())
    print('Pronostico:\t', xd.get_forecast())


if __name__ == '__main__':
    main()

class ProductsHelper(object):
    # --Getters --#

    def __init__(self):
        self.__all_cartridges = None
        self.__all_cartridges_recipes = None
        self.__all_tickets_details = None
        self.__all_supplies = None
        self.__always_popular_cartridge = None
        self.__elements_in_warehouse = None
        self.__all_warehouse_details = None
        self.__predictions = None
        self.__required_supplies_list = None
        self.__today_popular_cartridge = None
        super(ProductsHelper, self).__init__()

    def get_all_cartridges(self):
        return self.__all_cartridges

    def get_all_tickets_details(self):
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()
        return self.__all_tickets_details

    def get_all_warehouse_detaills(self):
        return self.__all_warehouse_details

    def get_all_supplies(self):
        if self.__all_supplies is None:
            self.set_all_supplies()
        return self.__all_supplies

    def get_always_popular_cartridge(self):
        self.set_always_popular_cartridge()
        return self.__always_popular_cartridge

    def get_prediction_supplies_list(self):
        return self.__predictions

    def get_required_supplies(self):
        if self.__elements_in_warehouse is None:
            self.set_elements_in_warehouse()

        if self.__all_cartridges is None:
            self.set_all_cartridges()

        if self.__all_cartridges_recipes is None:
            self.set_all_cartridges_recipes()

        if self.__all_warehouse_details is None:
            self.set_all_warehouse_details()

        if self.__predictions is None:
            self.set_predictions()

        required_supplies_list = []
        supplies_on_stock = self.__all_warehouse_details.filter(status="ST")

        for prediction in self.__predictions:
            for cartridge in self.__all_cartridges:
                if prediction['name'] == cartridge.name:
                    ingredients = self.__all_cartridges_recipes.filter(cartridge=cartridge)
                    for ingredient in ingredients:
                        supply = ingredient.supply
                        name = ingredient.supply.name
                        cost = ingredient.supply.presentation_cost
                        measurement = ingredient.supply.measurement_unit
                        measurement_quantity = ingredient.supply.measurement_quantity
                        quantity = ingredient.quantity

                        count = 0

                        required_supply_object = {
                            'supply': supply,
                            'name': name,
                            'cost': cost,
                            'measurement': measurement,
                            'measurement_quantity': measurement_quantity,
                            'quantity': quantity
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

        for required_supply in required_supplies_list:
            for supply_on_stock in supplies_on_stock:

                if supply_on_stock.warehouse.supply == required_supply['supply']:
                    required_supply['stock'] = supply_on_stock.quantity
                    required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
                    required_supply['full_cost'] = \
                        required_supply['cost'] * \
                        math.ceil(required_supply['required'] / required_supply['measurement_quantity'])
                    break
                else:
                    required_supply['stock'] = 0
                    required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
                    required_supply['full_cost'] = \
                        required_supply['cost'] * \
                        math.ceil(required_supply['required'] / required_supply['measurement_quantity'])

        return required_supplies_list

    def get_supplies_on_stock_list(self):
        stock_list = []
        all_elements = self.__elements_in_warehouse.filter(status='ST')
        if all_elements.count() > 0:
            for element in all_elements:
                stock_object = {
                    'name': element.supply.name,
                    'quantity': element.quantity,
                }
                stock_list.append(stock_object)

        return stock_list

    def get_today_popular_cartridge(self):
        return self.__always_popular_cartridge

    def get_all_warehouse_details(self):
        if self.__all_warehouse_details is None:
            self.set_all_warehouse_details()
        return self.__all_warehouse_details

    # --Setters --#

    def set_predictions(self):
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()

        prediction_list = []

        for ticket_details in self.__all_tickets_details:
            cartridge_object = {
                'name': ticket_details.cartridge.name,
                'cantidad': 1,
            }

            prediction_list.append(cartridge_object)

        self.__predictions = prediction_list

    def set_all_cartridges(self):
        self.__all_cartridges = Cartridge.objects.all()

    def set_all_tickets_details(self, initial_date=None, final_date=None):
        if initial_date is None and final_date is None:
            self.__all_tickets_details = TicketDetail.objects.select_related(
                'ticket').select_related('cartridge').select_related('package_cartridge').all()
        else:
            self.__all_tickets_details = TicketDetail.objects.select_related(
                'ticket').select_related('cartridge').select_related('package_cartridge').filter(
                ticket__created_at__range=[initial_date, final_date])

    def set_all_cartridges_recipes(self):
        self.__all_cartridges_recipes = \
            CartridgeRecipe.objects.select_related('cartridge').select_related('supply').all()

    def set_all_supplies(self):
        self.__all_supplies = \
            Supply.objects.select_related('category').select_related('supplier').select_related('location').all()

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

    def set_elements_in_warehouse(self):
        self.__elements_in_warehouse = Warehouse.objects.select_related('supply').all()

    def set_all_warehouse_details(self):
        self.__all_warehouse_details = WarehouseDetails.objects.all()

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


# -------------------------------------  Profile -------------------------------------


# -------------------------------------  Suppliers -------------------------------------
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


# -------------------------------------  Supplies -------------------------------------
@login_required(login_url='users:login')
def supplies(request):
    products_helper = ProductsHelper()
    template = 'supplies/supplies.html'
    title = 'Insumos'
    context = {
        'supplies': products_helper.get_all_supplies().order_by('id'),
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


class CreateSupply(CreateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

    def __init__(self, **kwargs):
        super(CreateSupply).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('products:supplies')


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


class UpdateSupply(UpdateView):
    model = Supply
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'presentation_unit', 'presentation_cost',
              'measurement_quantity', 'measurement_unit', 'optimal_duration', 'optimal_duration_unit', 'location',
              'image']
    template_name = 'supplies/new_supply.html'

    def __init__(self, **kwargs):
        super(UpdateSupply).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('products:supplies')

    class DeleteSupply(DeleteView):
        model = Supply
        template_name = 'supplies/delete_supply.html'

        def __init__(self, **kwargs):
            super(DeleteView).__init__(**kwargs)
            self.object = None

        def delete(self, request, *args, **kwargs):
            self.object = self.get_object()
            self.object.delete()
            return redirect('supplies:supplies')


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


class CreateCategory(CreateView):
    model = SuppliesCategory
    fields = ['name', 'image']
    template_name = 'supplies/new_supplier.html'

    def __init__(self, **kwargs):
        super(CreateCategory).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('supplies:supplies')


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


class CreateCartridge(CreateView):
    model = Cartridge
    fields = ['name', 'price', 'category', 'image']
    template_name = 'cartridges/new_cartridge.html'

    def __init__(self, **kwargs):
        super(CreateCartridge).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('supplies:cartridges')


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
def cartridge_recipe(request, pk=None):
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


class UpdateCartridge(UpdateView):
    model = Cartridge
    fields = ['name', 'price', 'category', 'image']
    template_name = 'cartridges/new_cartridge.html'

    def __init__(self, **kwargs):
        super(UpdateCartridge).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return redirect('supplies:cartridges')


class DeleteCartridge(DeleteView):
    model = Cartridge
    template_name = 'cartridges/delete_cartridge.html'

    def __init__(self, **kwargs):
        super(DeleteCartridge).__init__(**kwargs)
        self.object = self.get_object()

    def delete(self, request, *args, **kwargs):
        self.object.delete()
        return redirect('supplies:cartridges')


# -------------------------------------  Catering -------------------------------------
@login_required(login_url='users:login')
def catering(request):
    """"
    TODO: Media para predicción. 
    TODO: Ordenar por prioridad.
    """
    products_helper = ProductsHelper()
    required_supplies = products_helper.get_required_supplies()
    estimated_total_cost = 0

    template = 'catering/catering.html'
    title = 'Abastecimiento'

    context = {
        'title': title,
        'required_supplies': required_supplies,
        'estimated_total_cost': estimated_total_cost,
        'page_title': PAGE_TITLE,
        'always_popular_cartridge': products_helper.get_always_popular_cartridge(),
        'today_popular_cartridge': products_helper.get_today_popular_cartridge(),
    }

    return render(request, template, context)


# -------------------------------------- Warehouse ---------------------------------------------
@login_required(login_url='users:login')
def warehouse(request):
    template = 'catering/warehouse.html'
    title = 'Movimientos de Almacen'
    context = {
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def warehouse_movements(request):
    products_helper = ProductsHelper()
    predictions = products_helper.get_required_supplies()
    supplies_on_stock = WarehouseDetails.objects.order_by('warehouse')

    if request.method == 'POST':
        mod_wh = WarehouseDetails.objects.get(pk=request.POST['element_pk'])
        mod_wh.status = "ST"
        mod_wh.save()

    for prediction in predictions:
        if prediction['required'] > 0:
            try:
                sup_on_stock = Warehouse.objects.get(supply=prediction['supply'])
                try:
                    detail = WarehouseDetails.objects.get(warehouse=sup_on_stock, status="PR")
                    detail.quantity = prediction['quantity']
                except WarehouseDetails.DoesNotExist:
                    WarehouseDetails.objects.create(warehouse=sup_on_stock, status="PR",
                                                    quantity=prediction['required'])
            except Warehouse.DoesNotExist:
                Warehouse.objects.create(supply=prediction['supply'], cost=prediction['cost'])

    template = 'catering/catering_movements.html'
    title = 'Movimientos de Almacen'
    context = {
        'supply_list': supplies_on_stock,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


def products_analytics(request):

    template = 'analytics/analytics.html'
    title = 'Products - Analytics'
    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
    }

    return render(request, template, context)


def test(request):
    return HttpResponse('Write yours test here')
