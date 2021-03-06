import json
from datetime import datetime, date, timedelta

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Max, Min

from branchoffices.models import CashRegister
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper, SalesHelper
from kitchen.models import Warehouse
from products.models import Cartridge, PackageCartridge, PackageCartridgeRecipe, ExtraIngredient, CartridgeRecipe, \
    Supply
from sales.models import Ticket, TicketDetail, TicketExtraIngredient
from users.models import User as UserProfile


# -------------------------------------  Sales -------------------------------------
@login_required(login_url='users:login')
def sales(request):
    sales_helper = SalesHelper()
    helper = Helper()

    if request.method == 'POST':
        if request.POST['type'] == 'sales_day':
            """
            Returns a list with objects:
            Each object has the following characteristics
            """
            sales_day_list = []
            start_day = helper.naive_to_datetime(datetime.strptime(request.POST['date'], '%d-%m-%Y').date())
            end_date = helper.naive_to_datetime(start_day + timedelta(days=1))
            filtered_tickets = sales_helper.get_all_tickets().filter(created_at__range=[start_day, end_date])

            for ticket in filtered_tickets:
                """
                Filling in the sales list of the day
                """
                earnings_sale_object = {
                    'id_ticket': ticket.id,
                    'datetime': timezone.localtime(ticket.created_at),
                    'earnings': 0
                }
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        earnings_sale_object['earnings'] += ticket_detail.price
                sales_day_list.append(earnings_sale_object)
            return JsonResponse({'sales_day_list': sales_day_list})

        if request.POST['type'] == 'ticket_details':
            ticket_id = int(request.POST['ticket_id'])
            ticket_object = {
                'ticket_id': ticket_id,
                'ticket_order': '',
                'cartridges': [],
                'packages': [],
            }

            # Get cartridges details
            for ticket_detail in sales_helper.get_all_tickets_details():
                if ticket_detail.ticket.id == ticket_id:
                    ticket_object['ticket_order'] = ticket_detail.ticket.order_number

                    if ticket_detail.cartridge:
                        cartridge_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['cartridges'].append(cartridge_object)
                    elif ticket_detail.package_cartridge:
                        cartridges_list = []
                        package_cartridge_recipe = PackageCartridgeRecipe.objects.filter(
                            package_cartridge=ticket_detail.package_cartridge)

                        for cartridge_recipe in package_cartridge_recipe:
                            cartridges_list.append(cartridge_recipe.cartridge.name)

                        package_cartridge_object = {
                            'cartridges': cartridges_list,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['packages'].append(package_cartridge_object)

            return JsonResponse({'ticket_details': ticket_object})

        if request.POST['type'] == 'tickets':
            tickets_objects_list = []

            for ticket in sales_helper.get_all_tickets():
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        ticket_object = {
                            'ID': ticket.id,
                            'Fecha': timezone.localtime(ticket.created_at).date(),
                            'Hora': timezone.localtime(ticket.created_at).time(),
                            'Vendedor': ticket.seller.username,
                        }
                        if ticket.payment_type == 'CA':
                            ticket_object['Tipo de Pago'] = 'Efectivo'
                        else:
                            ticket_object['Tipo de Pago'] = 'Crédito'
                        if ticket_detail.cartridge:
                            ticket_object['Producto'] = ticket_detail.cartridge.name
                        else:
                            ticket_object['Producto'] = None
                        if ticket_detail.package_cartridge:
                            ticket_object['Paquete'] = ticket_detail.package_cartridge.name
                        else:
                            ticket_object['Paquete'] = None
                        ticket_object['Cantidad'] = ticket_detail.quantity
                        ticket_object['Total'] = ticket_detail.price
                        ticket_object['Precio Unitario'] = ticket_detail.price / ticket_detail.quantity

                        tickets_objects_list.append(ticket_object)

            return JsonResponse({'ticket': tickets_objects_list})

        if request.POST['type'] == 'sales_week':
            initial_date = request.POST['dt_week'].split(',')[0]
            final_date = request.POST['dt_week'].split(',')[1]
            initial_date = helper.parse_to_datetime(initial_date)
            final_date = helper.parse_to_datetime(final_date) + timedelta(days=1)

            filtered_sales = sales_helper.get_sales_list(initial_date, final_date)
            filtered_tickets = sales_helper.get_tickets_list(initial_date, final_date)
            data = {
                'sales': filtered_sales,
                'tickets': filtered_tickets,
                'week_number': helper.get_week_number(initial_date)
            }
            return JsonResponse(data)

    active_tickets = [x for x in sales_helper.get_tickets_today_list() if x['is_active'] == True]
    all_tickets = sales_helper.get_tickets_today_list()

    if request.user.is_superuser:
        user_tickets = all_tickets
    else:
        user_tickets = active_tickets


    total_cost = 0
    all_tickets_cost = 0
    for ticket in active_tickets:
        total_cost += ticket["ticket_parent"].total()

    for ticket in all_tickets:
        all_tickets_cost += ticket["ticket_parent"].total()

    # Any other request method:
    template = 'sales/sales_analytics.html'
    title = 'Registro de Ventas'
    print(sales_helper.get_sales_actual_week())
    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'actual_year': datetime.now().year,
        'sales_week': sales_helper.get_sales_actual_week(),
        'today_name': helper.get_name_day(datetime.now()),
        'today_number': helper.get_number_day(datetime.now()),
        'week_number': helper.get_week_number(datetime.now()),
        'total_cost' : total_cost,
        'all_tickets_cost': all_tickets_cost,
        'tickets': user_tickets,
        'user' : request.user,
        'dates_range': sales_helper.get_dates_range_json(),
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def delete_sale(request):
    if request.method == 'POST':
        ticket_id = request.POST['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)
        if request.POST['action'] == 'activate-ticket':
            ticket.is_active = True
            ticket.save()
            return JsonResponse({'result': 'excelente!'})
        if request.POST['action'] == 'deactivate-ticket':
            ticket.is_active = False
            ticket.save()
            return JsonResponse({'result': 'excelente!'})
        if request.POST['action'] == 'delete-ticket':
            ticket.delete()
            return JsonResponse({'result': 'excelente!'})



@login_required(login_url='users:login')
def new_sale(request):
    helper = Helper()

    if request.method == 'POST':
        if request.POST['ticket']:
            username = request.user
            user_profile_object = get_object_or_404(UserProfile, username=username)
            cash_register = CashRegister.objects.first()
            ticket_detail_json_object = json.loads(request.POST.get('ticket'))
            ticket_detail_json_object
            payment_type = ticket_detail_json_object['payment_type']
            order_number = 1
            """
            Gets the tickets in the week and returns n + 1
            where n is the Ticket.order_number biggest for the current week
            TODO:
            1. Get tickets in the current week range
            2. Search the ticket with the largest order_number atribute
            3. save the 'new_ticket_object' with the new atribute (n + 1)
            4. Save the new object
            """

            tickets = Ticket.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=helper.get_number_day(datetime.now())))

            for ticket in tickets:
                order_number_ticket = ticket.order_number
                if order_number_ticket >= order_number:
                    order_number = order_number_ticket + 1

            new_ticket_object = Ticket(
                cash_register=cash_register, seller=user_profile_object,
                payment_type=payment_type, order_number=order_number)
            new_ticket_object.save()

            """
            Saves the tickets details for cartridges
            """
            for ticket_detail in ticket_detail_json_object['cartridges']:
                cartridge_object = get_object_or_404(Cartridge, id=ticket_detail['id'])
                quantity = ticket_detail['quantity']
                price = ticket_detail['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    cartridge=cartridge_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

                cartridge_recipe = CartridgeRecipe.objects.filter(cartridge=cartridge_object)

                for element in cartridge_recipe:
                    try:
                        stock = Warehouse.objects.get(supply=element.supply, status="AS")
                        stock.quantity -= element.quantity
                        stock.save()

                    except ObjectDoesNotExist:
                        print("No Stock")
                        #No hay Stock, deberia no permitirse el cambio

            for ticket_detail in ticket_detail_json_object['extra_ingredients_cartridges']:
                cartridge_object = get_object_or_404(Cartridge, id=ticket_detail['cartridge_id'])
                quantity = ticket_detail['quantity']
                price = ticket_detail['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    cartridge=cartridge_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

                cartridge_recipe = CartridgeRecipe.objects.filter(cartridge=cartridge_object)

                for element in cartridge_recipe:
                    try:
                        stock = Warehouse.objects.get(supply=element.supply, status="AS")
                        stock.quantity -= element.quantity

                    except ObjectDoesNotExist:
                        print("No Stock")

                for ingredient in ticket_detail['extra_ingredients']:
                    extra_ingredient_object = ExtraIngredient.objects.get(id=ingredient['id'])
                    new_extra_ingredient_object = TicketExtraIngredient(
                        ticket_detail=new_ticket_detail_object,
                        extra_ingredient=extra_ingredient_object,
                        price=ingredient['cost']
                    )
                    new_extra_ingredient_object.save()

            for ticket_detail_package in ticket_detail_json_object['packages']:
                """
                Saves the tickets details for package cartridges
                """
                package_object = get_object_or_404(PackageCartridge, id=ticket_detail_package['id'])
                quantity = ticket_detail_package['quantity']
                price = ticket_detail_package['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    package_cartridge=package_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

            json_response = {
                'status': 'ready',
                'ticket_id': new_ticket_object.id,
                'ticket_order': new_ticket_object.order_number,
                'ticket_payment': new_ticket_object.payment_type,
            }
            return JsonResponse(json_response)

        return JsonResponse({'status': 'error'})

    cartridges_list = Cartridge.objects.all().order_by('name')
    package_cartridges = PackageCartridge.objects.all().order_by('name')
    extra_ingredients = ExtraIngredient.objects.all().prefetch_related('ingredient')
    extra_ingredients_products_list = []

    for cartridge in cartridges_list:
        cartridge_object = {
            'id': cartridge.id,
            'name': cartridge.name,
            'extra_ingredients': [],
        }
        for ingredient in extra_ingredients:
            if cartridge == ingredient.cartridge:
                ingredient_object = {
                    'id': ingredient.id,
                    'name': ingredient.ingredient.name,
                    'image': ingredient.image.url,
                    'cost': str(ingredient.cost),
                }
                cartridge_object['extra_ingredients'].append(ingredient_object)
        if len(cartridge_object['extra_ingredients']) > 0:
            extra_ingredients_products_list.append(cartridge_object)

    template = 'new/new_sale.html'
    title = 'Nueva venta'

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'cartridges': cartridges_list,
        'package_cartridges': package_cartridges,
        'extra_ingredients': extra_ingredients,
        'extra_ingredients_products_list': extra_ingredients_products_list,
        'extra_ingredients_products_list_json': json.dumps(extra_ingredients_products_list),
    }
    return render(request, template, context)


# -------------------------------- Test ------------------------------
def test(request):
    template = 'sales/test.html'

    tickets_details = TicketDetail.objects.select_related('ticket', 'ticket__seller', 'cartridge',
                                                          'package_cartridge').filter()
    tickets = Ticket.objects.all()
    tickets_list = []

    for ticket in tickets:
        ticket_object = {
            'ticket_parent': ticket,
            'cartridges': [],
            'packages': [],
            'total': Decimal(0.00),
        }

        for ticket_details in tickets_details:
            if ticket_details.ticket == ticket:
                if ticket_details.cartridge:
                    cartridge_object = {
                        'cartridge': ticket_details.cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['cartridges'].append(cartridge_object)
                    ticket_object['total'] += ticket_details.price
                elif ticket_details.package_cartridge:
                    package_cartridge_object = {
                        'package': ticket_details.package_cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['packages'].append(package_cartridge_object)
                    ticket_object['total'] += ticket_details.price

        tickets_list.append(ticket_object)
        print(tickets_list)

    context = {
        'tickets': tickets_list,
    }

    return render(request, template, context)
