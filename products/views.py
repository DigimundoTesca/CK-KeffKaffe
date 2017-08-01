# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
import random
import json
from datetime import timedelta, date, datetime
from datetime import timedelta, datetime, date
from decimal import Decimal

from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper, LeastSquares, SalesHelper, ProductsHelper
from products.forms import SuppliesCategoryForm, SuppliersForm, RecipeForm, PresentationForm, ShopListDetailForm
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
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'optimal_duration', 'optimal_duration_unit', 'location',
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
    fields = ['name', 'category', 'barcode', 'supplier', 'storage_required', 'optimal_duration', 'optimal_duration_unit', 'location',
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



# -------------------------------------- Warehouse ---------------------------------------------
@login_required(login_url='users:login')
def warehouse(request):

    products_helper = ProductsHelper()
    warehouse_list = products_helper.get_all_elements_in_warehouse()

    if request.method == 'POST':
        
        if request.POST['type'] == 'save_to_assembly':

            quantity = json.loads(request.POST.get('quantity_available'))
            warehouse_id = json.loads(request.POST.get('warehouse_id'))

            # Retirar del almacen
            selected_warehouse = Warehouse.objects.get(id=warehouse_id)
            selected_warehouse.quantity -= quantity
            selected_warehouse.save()

            # Agregar al almacen
            try:
                itemstock = Warehouse.objects.get(supply=selected_warehouse.supply, status="AS")
                itemstock.quantity += quantity
                itemstock.save()
            except Warehouse.DoesNotExist:
                itemstock = Warehouse(supply=selected_warehouse.supply, status="AS",
                                      quantity=quantity,
                                      measurement_unit=selected_warehouse.measurement_unit)
                itemstock.save()

    template = 'catering/warehouse.html'
    title = 'Movimientos de Almacen'
    context = {
        'warehouse_list': warehouse_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def shop_list(request):

    shop_list = ShopList.objects.all()

    if request.method == 'POST':

        if request.POST['type'] == 'load_list':
            element = json.loads(request.POST.get('load_list'))
            list_sl = ShopListDetail.objects.filter(shop_list_id=element)

            shop_list_array = []

            for ele_shoplist in list_sl:
                list_object = {
                    'id': ele_shoplist.id,
                    'nombre': ele_shoplist.presentation.supply.name,
                    'cantidad': ele_shoplist.quantity,
                    'medida': ele_shoplist.presentation.measurement_quantity,
                    'unidad': ele_shoplist.presentation.measurement_unit,
                    'costo': ele_shoplist.presentation.presentation_cost * ele_shoplist.quantity,
                    'status': ele_shoplist.status
                }

                shop_list_array.append(list_object)

            list_naive_array = {
                'shop_list': shop_list_array
            }
            return JsonResponse(list_naive_array)

        if request.POST['type'] == 'load_list_detail':
            element = json.loads(request.POST.get('load_list_detail'))
            list_sl = ShopListDetail.objects.get(id=element)
            list_sl.status = "DE"
            list_sl.deliver_day = datetime.now()
            list_sl.save()

            try:
                itemstock = Warehouse.objects.get(supply=list_sl.presentation.supply, status="ST")
                itemstock.quantity += list_sl.quantity * list_sl.presentation.measurement_quantity
                itemstock.save()
            except Warehouse.DoesNotExist:
                itemstock = Warehouse(supply=list_sl.presentation.supply, status="ST",
                                      quantity=list_sl.quantity * list_sl.presentation.measurement_quantity,
                                      measurement_unit=list_sl.presentation.measurement_unit)
                itemstock.save()

        if request.POST['type'] == 'load_date':
            element = json.loads(request.POST.get('detail_list_id'))
            list_sl = ShopListDetail.objects.get(id=element)
            date = list_sl.deliver_day

            return HttpResponse(date)


    template = 'catering/shoplist.html'
    title = 'Lista de Compras'
    context = {
        'shop_list': shop_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_shoplist(request):

    products_helper = ProductsHelper()
    supps = products_helper.get_all_supplies()
    all_presentations = Presentation.objects.all()

    shop_list = ShopList.objects.all()

    supply_list = []

    if request.method == 'POST':
        form = PresentationForm(request.POST, request.FILES)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.save()
            return redirect('/warehouse/new_shoplist')

        if request.POST['type'] == 'shop_list':
            shop_l = json.loads(request.POST.get('shop_list'))

            new_shop_list = ShopList.objects.create()
            new_shop_list.save()

            for item in shop_l:
                sel_pre = Presentation.objects.get(pk=item['pre_pk'])
                ShopListDetail.objects.create(shop_list=new_shop_list, presentation=sel_pre, quantity=item['Cantidad'])

            return redirect('/warehouse/shoplist')

    else:
        form = PresentationForm()

    for sup in supps:
        element_object = {
            'pk': sup.pk,
            'name': sup.name,
            'imagen': sup.image.url,
        }
        supp_presentations = all_presentations.filter(supply=sup)
        supp_pres = []

        for supp_pre in supp_presentations:
            supp_pres.append(supp_pre)

        element_object['presentations'] = supp_pres
        supply_list.append(element_object)

    template = 'catering/new_shoplist.html'
    title = 'Lista de Compras'
    context = {
        'shop_list': shop_list,
        'form': form,
        'title': title,
        'supply_list': supply_list,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def products_analytics_b(request):
    products_helper = ProductsHelper()

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
                'category': cartridge_item.category,
            }
            cartridges_list.append(cartridge_object)

        for ticket_detail_item in filtered_ticket_details:
            if ticket_detail_item.cartridge:
                for cartridge_item in cartridges_list:
                    if cartridge_item['id'] == ticket_detail_item.cartridge.id:
                        cartridge_item['frequency'] += ticket_detail_item.quantity
                        break

        return cartridges_list

    def get_sold_category():
        drinks_sold = []
        food_sold = []
        for element in get_products_sold():
            category_object = {
                'id': element['id'],
                'name': element['name'],
                'category': element['category'],
                'quantity': element['frequency']
            }
            if element['frequency'] > 0:
                if element['category'] == 'CO':

                    drinks_sold.append(category_object)
                else:
                    food_sold.append(category_object)
        return {'drinks_sold': drinks_sold, 'food_sold': food_sold}

    if request.method == 'POST':
        if request.POST['type'] == 'category':
            sold_categories = get_sold_category()
            return JsonResponse(sold_categories)
        else:
            return JsonResponse('Hola')

    template = 'analytics/analytics.html'
    title = 'Products - Analytics'

    categories_sold = get_sold_category()
    sold_product = get_products_sold()
    print(categories_sold)
    all_categories = products_helper.get_all_cartridges_categories()
    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'today_sold_product_json': json.dumps(sold_product),
        'today_sold_product': sold_product,
        'category_sold': json.dumps(categories_sold),
        'all_categories': json.dumps(all_categories),
    }

    return render(request, template, context)


@login_required(login_url='users:login')
def products_analytics(request):

    template = 'analytics/analytics_r.html'
    title = 'Analytics'

    products_helper = ProductsHelper()    
    sales = json.dumps(products_helper.get_sales_by_date(initial_date,final_date))

    if request.method == 'POST':
        if request.POST['type'] == 'sales_week':
            initial_date = request.POST['dt_week'].split(',')[0]
            final_date = request.POST['dt_week'].split(',')[1]
            initial_date = helper.parse_to_datetime(initial_date)
            final_date = helper.parse_to_datetime(final_date) + timedelta(days=1)

            sales = json.dumps(products_helper.get_sales_by_date(initial_date,final_date))

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'sales': sales,
        'page_title': title
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
    if request.method == 'POST':
        initial_date = 'Fecha inicial ' + request.POST['initial_date']
        final_date = 'Fecha Final ' + request.POST['final_date']

        result_date = initial_date + '/' + final_date

        return JsonResponse({'resultado': result_date})
    return HttpResponse('No soy un metodo POST')
