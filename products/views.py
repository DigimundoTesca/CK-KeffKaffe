# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, datetime, date

from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper, LeastSquares, SalesHelper, ProductsHelper
from products.forms import SuppliesCategoryForm, SuppliersForm, RecipeForm
from products.models import Cartridge, Supply, SuppliesCategory, CartridgeRecipe
from kitchen.models import Warehouse, WarehouseDetails
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView



# -------------------------------------  Suppliers -------------------------------------
from sales.models import TicketDetail


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
class AddStock(CreateView):
    model = WarehouseDetails
    fields = ['warehouse','status','quantity']
    template_name = 'catering/add_stock.html'

    def __init__(self, **kwargs):
        super(AddStock).__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        print(form)
        self.object = form.save()
        return redirect('products:warehouse/catering')


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
                'Provedor': "proveedor",
                'Cantidad': required['name'],
                'Medida': required["measurement"],
                'Presentacion': required['measurement_quantity'],
                'Stock'
                'Requerdio': required['required'],
                'Costo': required['full_cost']                     
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
    supplies_on_stock = products_helper.get_all_warehouse_details()
    all_supplies = products_helper.get_all_supplies()

    if request.method == 'POST':
        number = request.POST['cantidad']
        mod_wh = WarehouseDetails.objects.get(pk=request.POST['element_pk'])
        mod_wh.quantity -= float(number)
        mod_wh.save()

        created_detail = WarehouseDetails.objects.create(warehouse=mod_wh.warehouse, quantity=number)

        if request.POST['type'] == 'Stock':
            created_detail.status = "ST"
        else:
            created_detail.status = "AS"

        start_date = str(created_detail.created_at)
        dt = datetime.strptime(start_date, "%Y-%m-%d")
        modified_date = dt + timedelta(days=created_detail.warehouse.supply.optimal_duration)
        created_detail.expiry_date = modified_date
        created_detail.save()

    for prediction in predictions:
        if prediction['required'] > 0:
            try:
                sup_on_stock = Warehouse.objects.get(supply=prediction['supply'])
                try:
                    detail = WarehouseDetails.objects.get(warehouse=sup_on_stock, status="PR")
                    detail.quantity = prediction['required']
                except WarehouseDetails.DoesNotExist:
                    WarehouseDetails.objects.create(
                        warehouse=sup_on_stock, status="PR", quantity=prediction['required'])
            except Warehouse.DoesNotExist:
                Warehouse.objects.create(supply=prediction['supply'], cost=prediction['cost'])

    template = 'catering/catering_movements.html'
    title = 'Movimientos de Almacen'
    context = {
        'supps': all_supplies,
        'supply_list': supplies_on_stock,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def products_analytics(request):
    def get_daily_period():
        helper = Helper()
        sales_helper = SalesHelper()

        initial_date = helper.naive_to_datetime(date.today())
        final_date = helper.naive_to_datetime(initial_date + timedelta(days=1))
        filtered_tickets = sales_helper.get_all_tickets().filter(created_at__range=[initial_date, final_date])
        tickets_details = sales_helper.get_all_tickets_details()
        tickets_list = []
        period_list = []
        for ticket in filtered_tickets:
            ticket_object = {
                'total': Decimal(0.00),
            }
            for ticket_details in tickets_details:
                if ticket_details.ticket == ticket:
                    ticket_object['total'] += ticket_details.price
            tickets_list.append(Decimal(ticket_object['total']))

        for _ in tickets_list:
            if ticket.created_at == ticket.created_at:
                print('No corresponde a la hora')

    def get_period(initial_dt, final_dt):
        helper = Helper()
        sales_helper = SalesHelper()
        initial_dt = initial_dt.split('-')
        initial_dt = helper.naive_to_datetime(date(int(initial_dt[2]), int(initial_dt[1]), int(initial_dt[0])))
        final_dt = final_dt.split('-')
        final_dt = helper.naive_to_datetime(date(int(final_dt[2]), int(final_dt[1]), int(final_dt[0])))

        filtered_tickets_details = sales_helper.get_all_tickets_details().filter(ticket__created_at__range=
                                                                                 [initial_dt, final_dt])
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
            # get_daily_period()
            get_period(initial_date, final_date)
<<<<<<< HEAD

            return JsonResponse({'resultado': 'algo xd'})

    def get_selled_products():
        helper = Helper()
        sales_helper = SalesHelper()
        all_products = sales_helper.get_all_tickets_details()
        all_products_dict = {}
        
        # for 
        # pass

    template = 'analytics/analytics.html'
    title = 'Products - Analytics'
    list_x = [1, 2, 3, 4, 5, 6]
    list_y = [10, 20, 30, 40, 50, 60]
    get_selled_products()
=======
            return JsonResponse({'resultado': 'algo xd'})

    template = 'analytics/analytics.html'
    title = 'Products - Analytics'
    list_x = [1, 2, 3, 4, 5, 6]
    list_y = [10, 20, 30, 40, 50, 60]

    latest_squares = LeastSquares(list_x, list_y)
    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'least_squares': latest_squares,
    }

    return render(request, template, context)


def get_control_proporcional(day_to_predict: datetime, products_object: object):
    """
    Este metodo nos retornará un PROMEDIO, pero qué promedios???
    
    1. Por DÍA [Lunes, Martes, Miercoles...]
    2. Por Número de día de cada MES [1, 2, 3, 4... 30, 31] 
    3. Por día del AÑO [1, 2, 3, 4, 5, ... 363, 364, 365]
    
    La Suma de estos tres valores nos indicarán el Control Proporcional
    
    Ejemplo:
        Hoy estamos a Lunes 15 de Mayo de 2017
        Sp
        Espera... me surgió una duda ...
        no recuerdo si aquí debería ser el promedio de TODOS los días que hay registro o
        el promedio de ventas de TODOS los lunes de los que se tiene registro ...
    
        Mp
        Calcular el promedio de todos los días 15 de TODOS los meses, por ejemplo 15 de enero, 
        15 de febrero, 15 de marzo... etc
    
        Ap 
        Calcular el promedio de ventas de todos los días X de todos los años 
        enero tiene 31...
        febrero... 28 
        marzo 31...
        abril .. 30
        mayo ... -> 15
    
        por lo tanto, 31 + 28 + 31 + 30 +15 = 135 -> Mayo es el día 135 del año
        Ap sería el promedio de todos los días 135 de todos los años que se tenga registro
    """

    #  Primero debemos hacer las consultas pertinentes :3

    #  Todas las siguientes deberías ser funciones, pero por ahora nel

    #  ----------------------------- INCISO A ---------------------
    # Aquí debe estar la lógica para obtener la variable Sp
    # Hay que filtrar sólo los que tengan como fecha de creación un lunes :D


    """
    En esta parte nos auxiliaremos de isoweekday que nos proveé python... 
    https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday
    
    nos retornará un numero del 1 al 7 dependiendo de cada día
    siendo 1 lunes y 7 domingo
    así que una vez obtenidos todos los tickets, iteraremos su fecha de creacion
    y validaremos uno a uno los que cumplan a condicion requerida...
    
    Recordar: ya tenemos un método en helpers que nos retorna el numero de un día,
    pero nos retorna numero del 0 al 6, siendo lunes el 0 y 6 domingo
    """

    """  Le tenemos que enviar el día del cual queremos obtener el numero
    correspondiente para hacer las validaciones """
    helper = Helper()
    number_day = helper.get_number_day(day_to_predict) + 1  # Este metodo ya incorpora isoweekday
    #  Como day_to_predict es Lunes 22 de mayo, nos retornará un 0, así que le sumamos uno, para que tenga sentido

    all_tickets_details = TicketDetail.objects.select_related('ticket').all()
    tickets_details_list = []
    total_days_dict = {}
    #  Ahora sí, vamos a iterar los tickets y a cada uno igual hay que convertir su atributo a entero

    for ticket_detail in all_tickets_details:
        if ticket_detail.ticket.created_at.isoweekday() == number_day:
            'Por lo tanto, ese ticket detail es de un día lunes :D'
            tickets_details_list.append(ticket_detail)
            """ Aquí obtendremos el total de lunes """
            total_days_dict[ticket_detail.ticket.created_at.strftime('%d-%m-%Y')] = True
            # Es obvio que si ya existe un ticket detail con la misma fecha no importa, ya que
            # sólo indicaremos que si existen tickets en ese día ...

    """ ahora obtendremos el promedio de todos esos días, como son tickets details
    entonces ya incluye el producto vendido y obvio, el precio base y el total, pero necesitamos conocer el
    id de la gelatina, por lo tanto debemos pasarlo por argumento en la funcion
    en este caso pasaremos el objecto como tal...
    Una vez encontrado el ticket detail correspondiente podremos añadir las elementos que se 
    vendieron en ese movimiento
    """

    total_elements = 0

    for ticket_detail in tickets_details_list:
        if ticket_detail.cartridge.id == products_object.id:
            'significa que es un ticket detail que vendio una gelatina'
            total_elements += ticket_detail.quantity

    # Y listo, ahora total_elements nos indicará los elementos vendidos en todos los tiempos
    #  en los cuales haya sido una venta en un día lunes :3 -> Procedemos a promediar

    day_average = total_elements / len(
        total_days_dict)  # Promedio de dia = cantidad de elementos vendidos entre total de dias obtenidos

    """ Necesitamos calcular los días totales :D ¿Cómo los calcularias? 
    TIP: Te puedes guiar usando los tickets_details_list <- Contiene los datos que sí nos sirven
    
    TODO: Obtener la cantidad de lunes en TODOS los tiempos en los que se haya vendido la gelatina
    
    Solución:
        recordar que un diccionario tiene llaves irrepetibles, entonces podemos usar cada datetime como una llave
        por lo tanto iteramos todos los tickets details list ( que son los que ya están filtrados)
        y almacenamos cada llava y obviamente, cada que se encuentre otro ticket detail con la misma
        fecha (date, no confundir con datetime) entonces ya no será necesario crear otro espacio en el diccionario
        al final solo queda obtener el tamaño del diccionario y ya
        """

    # ----------------------------- INCISO B ---------------------
    # Aquí debe estar la lógica para obtener la variable Mp
    total_elements = 0
    month_to_predict = TicketDetail.object.select_related('ticket').all()
    date = month_to_predict.created_at.month()
    print(date)

    # ----------------------------- INCISO C ---------------------
    # Aquí debe estar la lógica para obtener la variable Ap


def get_control_integral():
    """
    Este método retornará la suma del total de ventas de un producto en un
    día 'n' de la semana menos el promedio de ventas en una semana del producto,
    dividido entre la diferencia de los días de la semana menos la cantidad
    de días evaluados.

    Ejemplo:
    en el día miercoles se han vendido 20 gelatinas, y sabemos que en promedio
    hasta la fecha de hoy, en una semana cualquiera el promedio es que se vendan 
    50 gelatinas, por lo tanto
    Ts = 20
    Tp = 50
    Dr = 7 - 3 = 4

    """


def get_control_derivativo():
    """
    Este método nos retornará la derivada del día anterior con respecto a su día anterior
    aquí es donde utilizaremos los mínimos cuadrados...
    hipoteticamente, imaginando que la semana pasada se vendieron en el siguiente 
    orden de días la cantidad de gelatinas:
        {'Lunes': 15, 
        'Martes': 5, 
        'Miércoles': 9: 
        'Jueves': 14, 
        'Viernes': 12, 
        'Sabado': 0, 
        'Domingo': 15
        }
    y al realizar las operaciones de los mínimos cuadrados obtuvimos las siguientes "Predicciones":
    (Hipoteticamente)
        {'Lunes': 13,
        'Martes': 7, 
        'Miércoles': 8: 
        'Jueves': 10, 
        'Viernes': 12, 
        'Sabado': 0, 
        'Domingo': 12
        }
    por lo tanto si hoy es lunes y queremos conocer las ventas de mañana martes utilizaríamos
    el valor correspondiente al martes: 7
    
    """


def test(request):
    """
    TODO: Importar helpers
    """

    """
    Controlador PID

    TODO: Obtener el Control Proporcional, Integral y Derivativo

    La fórmula está dada por:
        ( (K1 * (Sp + Mp + Ap) ) + (K2 * ( Sum(Ts) - Sum(Tp) ) / Dr) + Dp ) / 3 

    En donde
        K1 = Constante Proporcional
        K2 =  Constante Integral
        K3 = Constante Derivativa
        Sp = Promedio por día de la Semana
        Mp = Promedio por dia del Mes
        Ap = Promedio por día del Año
        Ts = Suma del total de elementos en los días de la semana
        Tp = Suma del total de elementos promedios en todas las semanas registradas
        Dr = Días restantes -> 7 - Ts
        Dp = Promedio derivativo ( Mínimos cuadrados )

        *** K1, K2, K3 Son constantes que se van ajustando manualmente al final de la
        predicción inicial, de acuerdo a los valores reales obtenidos ***
        """

    """
    Esta funcion su unico proposito será generar los cálculos pertinentes, además
    de que aquí configuraremos las constantes de control
    
    Inicialmente, K1 = k2 = k3 = 1
    
    Mientras se vayan obteniendo los resultados y se comparen con los valores reales, entonces
    se hacen los ajustes pertinentes a las constantes.
    
    Ejemplo:
        obtuvimos los siguientes valores para cada control:
        get_control_proporcional() = 5
        get_control_integral() =  7
        get_control_derivativo() = 13
    
    
        Pero el valor real para el día siguiente de la gelatina fue de 7
        por lo tanto se hace un ajuste a la primer constante k1, para que 
        5 * k1 nos de un valor aproximado a 7
        los mismo para las siguientes constantes
        de manera que:
    
            k1 * 5  = 7;    k1 > 1
            k2 * 7  = 1;    k2 = 1 ... aquí se mantuvo :D
            k3 * 13 = 13;   k3 < 1 
    
            Ejemplo:
            De k3 ...
            si k3 > 1 entonces:
                k3 > 13 ... por lo tanto k3 * 13 > 7... y eso no nos sirve, ya que
                la venta real fue de 7, entonces nos estaríamos alejando más...
                la idea es realizarle ajustes a la constante para que el valor se acerque a 7 :D
    """
    k1 = 1
    k2 = 1
    k3 = 1
>>>>>>> 4bbc70805e08189eb33b27fe071f44f79d81dc3c

    # Debemos enviarle un dato, el cual es el día que queremos calcular la predicción ...
    # Imaginando que hoy es DOMINGO 21 de mayo, por lo tanto enviamos el día a predecir
    # Es decir el Lunes 22 de mayo


    day_to_predict = datetime.today() + timedelta(days=1)
    control_p = get_control_proporcional(day_to_predict)

    return HttpResponse('Hola!!!')
