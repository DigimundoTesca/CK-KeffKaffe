# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
from datetime import timedelta, date

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper, LeastSquares, SalesHelper, ProductsHelper
from products.forms import SuppliesCategoryForm, SuppliersForm, RecipeForm, PresentationForm
from products.models import Cartridge, Supply, SuppliesCategory, CartridgeRecipe, Presentation
from kitchen.models import Warehouse, ShopList, ShopListDetail
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView


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


# -------------------------------------  Catering -----~--------------------------------
@login_required(login_url='users:login')
def catering(request):
    """"
    TODO: Media para predicción. 
    TODO: Ordenar por prioridad.
    """

    products_helper = ProductsHelper()
    required_supplies = products_helper.get_required_supplies()

    estimated_total_cost = 0

    if request.method == 'POST':
        buy_objects_list = []
        for required in required_supplies:
            diner_object = {    
                'Nombre': required['name'], 
                'Requeridos': required['quantity'],
                'Stock': required['stock'],
                'Por Comprar': required['required'],
                'Comprar en': str(required['supplier']),
                'Cantidad x Unidad' : required['measurement_quantity'],
                'Costo x Unidad': required['cost'],
                'Costo Total': required['full_cost'],                    
            }
            buy_objects_list.append(diner_object)
        return JsonResponse({'buy_list': buy_objects_list})

    for required in required_supplies:
        estimated_total_cost += required["full_cost"]

    template = 'catering/catering.html'
    title = 'Abastecimiento'

    context = {
        'title': title,
        'required_supplies': required_supplies,
        'estimated_total_cost': estimated_total_cost,
        'page_title': PAGE_TITLE,
        'supply_list': products_helper.get_all_supplies(),
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
    supplies_list = products_helper.get_all_supplies()

    if request.method == 'POST':
        number = request.POST['cantidad']
        mod_wh = Warehouse.objects.get(pk=request.POST['element_pk'])
        mod_wh.quantity -= float(number)
        mod_wh.save()

        if request.POST['type'] == 'Stock':
            try:
                on_stock = Warehouse.objects.get(supply=mod_wh.supply, status="ST")
                on_stock.quantity += float(number)
                on_stock.save()
            except Warehouse.DoesNotExist:
                Warehouse.objects.create(supply=mod_wh.supply, quantity=number, cost=mod_wh.cost, status="ST")
        else:
            try:
                on_stock = Warehouse.objects.get(supply=mod_wh.supply, status="AS")
                on_stock.quantity += float(number)
                on_stock.save()
            except Warehouse.DoesNotExist:
                Warehouse.objects.create(supply=mod_wh.supply, quantity=number, cost=mod_wh.cost, status="AS")

    for supply in supplies_list:
        try:
            Warehouse.objects.get(supply=supply, status="PR")
        except Warehouse.DoesNotExist:

            Warehouse.objects.create(supply=supply, cost=supply.presentation_cost, status="PR")

    for prediction in predictions:
        if prediction['required'] > 0:
            try:
                Warehouse.objects.get(supply=prediction['supply'], status="PR")
            except Warehouse.DoesNotExist:
                Warehouse.objects.create(supply=prediction['supply'], cost=prediction['cost'],
                                         quantity=prediction['required'], status="PR")

    template = 'catering/catering_movements.html'
    title = 'Movimientos de Almacen'
    context = {
        'supply_list': products_helper.get_all_elements_in_warehouse(),
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title
    }
    return render(request, template, context)

@login_required(login_url='users:login')
def shop_list(request):

    products_helper = ProductsHelper()
    supps = products_helper.get_all_supplies()
    supply_list = []

    if request.method == 'POST':
        form = PresentationForm(request.POST, request.FILES)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.save()
            return redirect('/warehouse/shoplist')

        if request.POST['shop_list']:
            shop_l = json.loads(request.POST.get('shop_list'))

            new_shop_list = ShopList.objects.create()
            new_shop_list.save()

            for item in shop_l:
                ShopListDetail.objects.create(shop_list=new_shop_list, supply=item['sup_pk'], presentation=item['pre_pk'], quantity=item['Cantidad'])


    else:
        form = PresentationForm()



    all_presentations = Presentation.objects.all()

    for sup in supps:
        element_object = {
            'pk': sup.pk,
            'name': sup.name,
            'imagen': sup.image.url,
            'unidad': sup.self_measurement_conversion,
            'medida': sup.self_unit_conversion,
            'costo': sup.presentation_cost,
        }
        supp_presentations = all_presentations.filter(supply=sup)
        supp_pres = []

        for supp_pre in supp_presentations:
            supp_pres.append(supp_pre)

        element_object['presentations'] = supp_pres
        supply_list.append(element_object)

    template = 'catering/shoplist.html'
    title = 'Lista de Compras'
    context = {
        'form': form,
        'required_supplies': products_helper.get_required_supplies(),
        'title': title,
        'supply_list': supply_list,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)

@login_required(login_url='users:login')
def products_analytics(request):
    def get_period(initial_dt, final_dt):
        helper = Helper()
        sales_helper = SalesHelper()
        initial_dt = initial_dt.split('-')
        initial_dt = helper.naive_to_datetime(date(int(initial_dt[2]), int(initial_dt[1]), int(initial_dt[0])))
        final_dt = final_dt.split('-')
        final_dt = helper.naive_to_datetime(date(int(final_dt[2]), int(final_dt[1]), int(final_dt[0])))
        filtered_tickets_details = sales_helper.get_all_tickets_details().\
            filter(ticket__created_at__range=[initial_dt, final_dt])
        all_cartridge_recipes = CartridgeRecipe.objects.select_related('cartridge').all()
        supplies_list = []
        date_dict = {}
        aux_initial = initial_dt
        aux_final = final_dt

        while aux_initial < aux_final:
            date_dict[aux_initial.strftime('%d-%m-%Y')] = []
            aux_initial = aux_initial + timedelta(days=1)

        for ticket_detail in filtered_tickets_details:
            filtered_cartridge_recipes = all_cartridge_recipes.filter(cartridge=ticket_detail.cartridge)
            filtered_cartridge_recipes_list = []

            for item in filtered_cartridge_recipes:
                filtered_cartridge_recipes_list.append(item.supply.name)

            cartridge_object = {
                'name': ticket_detail.cartridge.name,
                'quantity': ticket_detail.quantity,
                'recipe': filtered_cartridge_recipes_list
            }
            supplies_list.append(cartridge_object)

        if request.method == 'POST':
            initial_date = request.POST['initial_date']
            final_date = request.POST['final_date']
            get_period(initial_date, final_date)
            return JsonResponse({'resultado': 'algo xd'})

    def get_products_sold():
        sales_helper = SalesHelper()
        products_helper = ProductsHelper()
        initial_date = date.today()
        final_date = initial_date + timedelta(days=1)
        cartridges_list = []
        filtered_ticket_details = sales_helper.get_tickets_details(initial_date, final_date)
        all_cartridges = products_helper.get_all_cartridges()

        for cartridge_item in all_cartridges:
            cartridge_object = {
                'id': cartridge_item.id,
                'name': cartridge_item.name,
                'frequency': 0,
            }
            cartridges_list.append(cartridge_object)

        for ticket_detail_item in filtered_ticket_details:
            if ticket_detail_item.cartridge:
                for cartridge_item in cartridges_list:
                    if cartridge_item['id'] == ticket_detail_item.cartridge.id:
                        cartridge_item['frequency'] += ticket_detail_item.quantity
                        break

        return cartridges_list

    template = 'analytics/analytics.html'
    title = 'Products - Analytics'

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
    }

    return render(request, template, context)


@login_required(login_url='users:login')
def products_predictions(request):
    template = 'analytics/predictions.html'
    title = 'Predicciones'

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title
    }
    return render(request, template, context)


def test(request):
    return HttpResponse('Hola!!!')
