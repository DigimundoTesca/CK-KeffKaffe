import json
import math
import pytz
from datetime import datetime, date, timedelta, time
from decimal import Decimal
from django.db.models import Min, Max, Sum
from django.utils import timezone
from diners.models import AccessLog, Diner
from kitchen.models import Warehouse, ProcessedProduct
from products.models import Supply, Cartridge, PackageCartridge, CartridgeRecipe, PackageCartridgeRecipe, \
    ExtraIngredient
from sales.models import Ticket, TicketDetail, TicketExtraIngredient


class Helper(object):
    def __init__(self):
        self.tz = pytz.timezone('America/Mexico_City')
        self.days_dict = {
            'MONDAY': 'Lunes',
            'TUESDAY': 'Martes',
            'WEDNESDAY': 'Miércoles',
            'THURSDAY': 'Jueves',
            'FRIDAY': 'Viernes',
            'SATURDAY': 'Sábado',
            'SUNDAY': 'Domingo'
        }
        self.number_days_dict = {
            'Lunes': 0,
            'Martes': 1,
            'Miércoles': 2,
            'Jueves': 3,
            'Viernes': 4,
            'Sábado': 5,
            'Domingo': 6,
        }
        super(Helper, self).__init__()

    def naive_to_datetime(self, nd):
        if type(nd) == datetime:
            if nd.tzinfo is not None and nd.tzinfo.utcoffset(nd) is not None:  # Is Aware
                return nd
            else:  # Is Naive
                return self.tz.localize(nd)

        elif type(nd) == date:
            d = nd
            t = time(0, 0)
            new_date = datetime.combine(d, t)
            return self.tz.localize(new_date)

    def get_name_day(self, datetime_now):
        name_day = date(datetime_now.year, datetime_now.month, datetime_now.day)
        return self.days_dict[name_day.strftime('%A').upper()]

    def get_number_day(self, dt):
        return self.number_days_dict[self.get_name_day(dt)]

    def start_datetime(self, back_days):
        start_date = date.today() - timedelta(days=back_days)
        return self.naive_to_datetime(start_date)

    def end_datetime(self, back_days):
        end_date = self.start_datetime(back_days) + timedelta(days=1)
        return self.naive_to_datetime(end_date)

    def parse_to_datetime(self, dt):
        day = int(dt.split('-')[0])
        month = int(dt.split('-')[1])
        year = int(dt.split('-')[2])
        parse_date = date(year, month, day)
        return self.naive_to_datetime(parse_date)

    def are_equal_lists(self, list_1, list_2):
        """
         Checks if two lists are identical
        """
        list_1 = self.items_list_to_int(list_1)
        list_2 = self.items_list_to_int(list_2)

        list_1.sort()
        list_2.sort()

        if len(list_1) != len(list_2):
            return False
        else:
            for element in range(0, len(list_1)):
                if list_1[element] != list_2[element]:
                    return False

        return True

    @staticmethod
    def get_week_number(dt):
        return dt.isocalendar()[1]

    @staticmethod
    def items_list_to_int(list_to_cast):
        """
        Evaluates each of the elements of the list received and casts them to integers
        """
        cast_list = []
        for item in range(0, len(list_to_cast)):
            cast_list.append(int(list_to_cast[item]))

        return cast_list


class LeastSquares(object):
    def __init__(self, x: list, y: list):
        super(LeastSquares, self).__init__()
        if len(x) != len(y):
            raise NameError('Las listas deben tener misma longitud.')

        self.__x = x
        self.__y = y
        self.__periodic_list = []
        self.__n = len(self.__x)
        self.set_periodic_list()

    def get_sum_x(self):
        return sum(self.__x)

    def get_sum_y(self):
        return sum(self.__y)

    def get_x_average(self):
        return math.ceil(self.get_sum_x() / len(self.__x))

    def get_y_average(self):
        return math.ceil(self.get_sum_y() / len(self.__y))

    def get_sum_x_pow(self):
        auxiliary_list = []
        count = 0

        for _ in self.__x:
            auxiliary_list.append(self.__x[count] ** 2)
            count += 1
        return sum(auxiliary_list)

    def get_sum_y_pow(self):
        auxiliary_list = []
        count = 0

        for _ in self.__y:
            auxiliary_list.append(self.__y[count] ** 2)
            count += 1
        return sum(auxiliary_list)

    def get_sum_x_y_prod(self):
        count = 0
        auxiliary_list = []

        for _ in self.__x:
            auxiliary_list.append(self.__x[count] * self.__y[count])
            count += 1

        return sum(auxiliary_list)

    def set_periodic_list(self):
        difference_list = []
        count = 0
        is_periodic = True

        for _ in self.__x:
            if count != 0:
                difference_list.append(self.__x[count] - self.__x[count - 1])

            count += 1

        count = 0

        for _ in difference_list:
            if count != 0:
                if difference_list[count] != difference_list[count - 1]:
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

    def get_a(self):
        return math.ceil(self.get_y_average() - self.get_b() * self.get_x_average())

    def get_b(self):
        return math.ceil((self.get_sum_x_y_prod() - (self.get_sum_x() * self.get_sum_y() / self.__n)) / (
            self.get_sum_x_pow() - (self.get_sum_x() ** 2) / self.__n))

    def get_forecast(self):
        forecast_list = []
        count = 0

        for _ in self.__x:
            forecast_list.append(self.get_a() + self.get_b() * self.__periodic_list[count])
            count += 1

        return forecast_list


class KitchenHelper(object):
    def __init__(self):
        super(KitchenHelper, self).__init__()
        self.__all_processed_products = None
        self.__all_warehouse = None

    def get_all_processed_products(self):
        """		
        rtype: django.db.models.query.QuerySet 		
        """
        if self.__all_processed_products is None:
            self.set_all_processed_products()
        return self.__all_processed_products

    def get_all_warehouse(self):
        """		
        :rtype: django.db.models.query.QuerySet 		
        """
        if self.__all_warehouse is None:
            self.set_all_processed_products()
        return self.__all_warehouse

    def get_processed_products(self):
        processed_products_list = []
        sales_helper = SalesHelper()
        products_helper = ProductsHelper()

        for processed in self.get_all_processed_products().filter(status='PE')[:15]:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': [],
                'ticket_order': processed.ticket.order_number
            }

            for ticket_detail in sales_helper.get_all_tickets_details():
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge,
                        }
                        for extra_ingredient in sales_helper.get_all_extra_ingredients():
                            if extra_ingredient.ticket_detail == ticket_detail:
                                try:
                                    cartridge['name'] += extra_ingredient['extra_ingredient']
                                except Exception as e:
                                    cartridge['name'] = ticket_detail.cartridge.name
                                    cartridge['name'] += ' con ' + extra_ingredient.extra_ingredient.ingredient.name
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = products_helper.get_all_packages_cartridges_recipes().filter(
                            package_cartridge=ticket_detail.package_cartridge)

                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    def set_all_warehouse(self):
        self.__all_warehouse = Warehouse.objects.select_related('supply').all()

    def set_all_processed_products(self):
        self.__all_processed_products = ProcessedProduct.objects. \
            select_related('ticket'). \
            all()


class SalesHelper(object):
    def __init__(self):
        self.__all_tickets = None
        self.__all_tickets_details = None
        self.__all_extra_ingredients = None
        super(SalesHelper, self).__init__()

    def set_all_tickets(self):
        self.__all_tickets = Ticket.objects.select_related('seller').all()

    def set_all_tickets_details(self):
        self.__all_tickets_details = TicketDetail.objects. \
            select_related('ticket'). \
            select_related('cartridge'). \
            select_related('ticket__seller'). \
            select_related('package_cartridge'). \
            all()

    def set_all_extra_ingredients(self):
        self.__all_extra_ingredients = TicketExtraIngredient.objects. \
            select_related('ticket_detail'). \
            select_related('extra_ingredient'). \
            select_related('extra_ingredient__ingredient'). \
            all()

    def get_all_tickets(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets is None:
            self.set_all_tickets()
        return self.__all_tickets

    def get_all_tickets_details(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()
        return self.__all_tickets_details

    def get_tickets_details(self, initial_date, final_date):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()
        return self.__all_tickets_details.filter(ticket__created_at__range=[initial_date, final_date])

    def get_all_extra_ingredients(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_extra_ingredients is None:
            self.set_all_extra_ingredients()
        return self.__all_extra_ingredients

    def get_years_list(self):
        """
        Returns a list of all the years in which there have been sales
        """
        years_list = []

        for ticket in self.get_all_tickets():
            if ticket.created_at.year not in years_list:
                years_list.append(ticket.created_at.year)

        return years_list

    def get_tickets_today_list(self):
        helper = Helper()

        tickets_list = []
        filtered_tickets = self.get_all_tickets().filter(created_at__gte=helper.naive_to_datetime(date.today()))

        for ticket in filtered_tickets:
            ticket_object = {
                'ticket_parent': ticket,
                'order_number': ticket.order_number,
                'cartridges': [],
                'packages': [],
                'total': Decimal(0.00),
                'is_active': ticket.is_active,
            }

            for ticket_details in self.get_all_tickets_details():
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

        return tickets_list

    def get_dates_range_json(self):
        """
        Returns a JSON with a years list.
        The years list contains years objects that contains a weeks list
            and the Weeks list contains a weeks objects with two attributes: 
            start date and final date. Ranges of each week.
        """
        helper = Helper()
        try:
            min_year = self.get_all_tickets().aggregate(Min('created_at'))['created_at__min'].year
            max_year = self.get_all_tickets().aggregate(Max('created_at'))['created_at__max'].year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]
        except:
            min_year = datetime.now().year
            max_year = datetime.now().year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]

        while max_year >= min_year:
            year_object = {  # 2015:object or 2016:object or 2017:object ...
                'year': max_year,
                'weeks_list': [],
            }

            tickets_per_year = self.get_all_tickets().filter(
                created_at__range=[helper.naive_to_datetime(date(max_year, 1, 1)),
                                   helper.naive_to_datetime(date(max_year, 12, 31))])
            for ticket_item in tickets_per_year:
                if len(year_object['weeks_list']) == 0:
                    """
                    Creates a new week_object in the weeks_list of the actual year_object
                    """
                    week_object = {
                        'week_number': ticket_item.created_at.isocalendar()[1],
                        'start_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                        'end_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                    }
                    year_object['weeks_list'].append(week_object)
                    # End if
                else:
                    """
                    Validates if exists some week with an similar week_number of the actual year
                    If exists a same week in the list validates the start_date and the end_date,
                    In each case valid if there is an older start date or a more current end date 
                        if it is the case, update the values.
                    Else creates a new week_object with the required week number
                    """
                    existing_week = False
                    for week_object in year_object['weeks_list']:

                        if week_object['week_number'] == ticket_item.created_at.isocalendar()[1]:
                            # There's a same week number
                            if datetime.strptime(week_object['start_date'],
                                                 "%d-%m-%Y").date() > ticket_item.created_at.date():
                                week_object['start_date'] = ticket_item.created_at.date().strftime("%d-%m-%Y")
                            elif datetime.strptime(week_object['end_date'],
                                                   "%d-%m-%Y").date() < ticket_item.created_at.date():
                                week_object['end_date'] = ticket_item.created_at.date().strftime("%d-%m-%Y")

                            existing_week = True
                            break

                    if not existing_week:
                        # There's a different week number
                        week_object = {
                            'week_number': ticket_item.created_at.isocalendar()[1],
                            'start_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                            'end_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                        }
                        year_object['weeks_list'].append(week_object)

                        # End else
            years_list.append(year_object)
            max_year -= 1
        # End while
        return json.dumps(years_list)

    def get_sales_list(self, start_dt, final_dt):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        helper = Helper()
        limit_day = start_dt + timedelta(days=1)
        total_days = (final_dt - start_dt).days
        week_sales_list = []
        count = 1
        total_earnings = 0

        while count <= total_days:
            day_tickets = self.get_all_tickets().filter(created_at__range=[start_dt, limit_day])
            day_object = {
                'date': str(start_dt.date().strftime('%d-%m-%Y')),
                'day_name': None,
                'earnings': None,
                'number_day': helper.get_number_day(start_dt),
            }

            for ticket_item in day_tickets:
                for ticket_detail_item in self.get_all_tickets_details():
                    if ticket_detail_item.ticket == ticket_item:
                        total_earnings += ticket_detail_item.price

            day_object['day_name'] = helper.get_name_day(start_dt.date())
            day_object['earnings'] = str(total_earnings)

            week_sales_list.append(day_object)

            # Reset data
            limit_day += timedelta(days=1)
            start_dt += timedelta(days=1)
            total_earnings = 0
            count += 1

        return week_sales_list

    def get_sales_actual_week(self):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        helper = Helper()
        week_sales_list = []
        total_earnings = 0
        days_to_count = helper.get_number_day(datetime.now())
        day_limit = days_to_count
        start_date_number = 0

        while start_date_number <= day_limit:
            day_object = {
                'date': str(helper.start_datetime(days_to_count).date().strftime('%d-%m-%Y')),
                'day_name': None,
                'earnings': None,
                'number_day': helper.get_number_day(helper.start_datetime(days_to_count).date()),
            }

            day_tickets = self.get_all_tickets().filter(
                created_at__range=[helper.start_datetime(days_to_count), helper.end_datetime(days_to_count)])

            for ticket_item in day_tickets:
                for ticket_detail_item in self.get_all_tickets_details():
                    if ticket_detail_item.ticket == ticket_item:
                        total_earnings += ticket_detail_item.price

            day_object['earnings'] = str(total_earnings)
            day_object['day_name'] = helper.get_name_day(helper.start_datetime(days_to_count).date())

            week_sales_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_earnings = 0
            start_date_number += 1

        return json.dumps(week_sales_list)

    def get_tickets_list(self, initial_date, final_date):
        """
        :rtype: list
        :param initial_date: datetime 
        :param final_date: datetime
        """
        all_tickets = self.get_all_tickets().filter(
            created_at__range=(initial_date, final_date)).order_by('-created_at')
        all_tickets_details = self.get_all_tickets_details()
        tickets_list = []

        for ticket in all_tickets:
            ticket_object = {
                'id': ticket.id,
                'order_number': ticket.order_number,
                'created_at': datetime.strftime(ticket.created_at, "%B %d, %Y, %H:%M:%S %p"),
                'seller': ticket.seller.username,
                'ticket_details': {
                    'cartridges': [],
                    'packages': [],
                },
                'total': 0,
            }

            for ticket_detail in all_tickets_details:
                if ticket_detail.ticket == ticket:
                    ticket_detail_object = {}
                    if ticket_detail.cartridge:
                        ticket_detail_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'price': float(ticket_detail.price),
                        }
                        ticket_object['ticket_details']['cartridges'].append(ticket_detail_object)
                    elif ticket_detail.package_cartridge:
                        ticket_detail_object = {
                            'name': ticket_detail.package_cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'price': float(ticket_detail.price),
                        }
                        ticket_object['ticket_details']['packages'].append(ticket_detail_object)

                    ticket_object['total'] += float(ticket_detail.price)

                    try:
                        ticket_object['ticket_details'].append(ticket_detail_object)
                    except Exception as e:
                        pass
            ticket_object['total'] = str(ticket_object['total'])
            tickets_list.append(ticket_object)
        return tickets_list


class ProductsHelper(object):
    def __init__(self):
        super(ProductsHelper, self).__init__()
        self.__all_cartridges = None
        self.__all_packages_cartridges = None
        self.__all_supplies = None
        self.__all_cartridges_categories = None
        self.__all_extra_ingredients = None
        self.__all_cartridges_recipes = None        
        self.__all_tickets_details = None
        self.__elements_in_warehouse = None        
        self.__predictions = None
        self.__required_supplies_list = None
        self.__today_popular_cartridge = None
        self.__all_packages_cartridges_recipes = None
        self.__always_popular_cartridge = None

    def set_all_supplies(self):
        self.__all_supplies = Supply.objects. \
            select_related('category'). \
            select_related('supplier'). \
            select_related('location').order_by('name')

    def set_all_cartridges(self):
        self.__all_cartridges = Cartridge.objects.all()

    def set_all_packages_cartridges(self):
        self.__all_packages_cartridges = PackageCartridge.objects.all()

    def set_all_cartridges_recipes(self):
        self.__all_cartridges_recipes = CartridgeRecipe.objects. \
            select_related('cartridge'). \
            select_related('supply'). \
            all()

    def set_all_cartridges_categories(self):
        cartridges = self.get_all_cartridges()
        cartridges_categories_list = []
        for cartridge in cartridges:
            cartridges_categories_list.append(cartridge.category)
        self.__all_cartridges_categories = cartridges_categories_list

    def set_all_package_cartridges_recipes(self):
        self.__all_packages_cartridges_recipes = PackageCartridgeRecipe.objects. \
            select_related('package_cartridge'). \
            select_related('cartridge'). \
            all()

    def set_all_extra_ingredients(self):
        self.__all_extra_ingredients = ExtraIngredient.objects. \
            select_related('ingredient'). \
            select_related('cartridge'). \
            all()

    def set_predictions(self):
        sales_helper = SalesHelper()
        all_tickets_details = sales_helper.get_all_tickets_details()

        prediction_list = []

        for ticket_details in all_tickets_details:
            cartridge_object = {
                'cartridge': ticket_details.cartridge,
                'cantidad': 1,
            }

            prediction_list.append(cartridge_object)

        self.__predictions = prediction_list

    def set_all_tickets_details(self):
        self.__all_tickets_details = TicketDetail.objects.select_related(
            'ticket').select_related('cartridge').select_related('package_cartridge').all()

    def set_always_popular_cartridge(self):
        sales_helper = SalesHelper()
        cartridges_frequency_dict = {}
        for cartridge in self.get_all_cartridges():
            cartridges_frequency_dict[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }
        for ticket_detail in sales_helper.get_all_tickets_details():
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
        self.__elements_in_warehouse = Warehouse.objects.select_related('supply').all().order_by('supply__name')

    def set_today_popular_cartridge(self):
        sales_helper = SalesHelper()
        cartridges_frequency_dict = {}
        helper = Helper()
        start_date = helper.naive_to_datetime(date.today())
        limit_day = helper.naive_to_datetime(start_date + timedelta(days=1))
        filtered_ticket_details = sales_helper.get_tickets_details(start_date, limit_day)

        for cartridge in self.get_all_cartridges():
            cartridges_frequency_dict[cartridge.id] = {
                'frequency': 0,
                'name': cartridge.name,
            }

        for ticket_detail in filtered_ticket_details:
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

    def get_sales_by_date(self,initial_date,final_date):

        ticket_details = self.get_all_tickets().filter(
            created_at__range=(initial_date, final_date)).order_by('-created_at')
        cartridges = self.get_all_cartridges()
        packages = self.get_all_packages_cartridges()
        packages_recipes = self.get_all_packages_cartridges_recipes()


        cartridges_sales = []

        for cartridge in cartridges:
            cartridge_on_ticket = ticket_details.filter(cartridge=cartridge)
            quantity = cartridge_on_ticket.aggregate(sum=Sum('quantity'))
            sale_count = {
                'name': cartridge.name,
                'category': cartridge.category,
                'quantity': quantity['sum']
            }
            cartridges_sales.append(sale_count)

        for package in packages:
            packages_on_ticket = ticket_detail.filter(package_cartridge=package_cartridge)
            for package_on_ticket in packages_on_ticket:
                recipee = packages_recipes.filter(package_cartridge=packages_on_ticket)
                for recipe in recipes:
                    cartridge_on_recipe = ticket_details.filter(cartridge=cartridge)
                    quantity = cartridge_on_ticket.aggregate(sum=Sum('quantity'))
                    sale_count = {
                        'name': cartridge.name,
                        'category': cartridge.category,
                        'quantity': quantity['sum']
                    }
                    cartridges_sales.append(sale_count)

        return cartridges_sales

    def get_all_ticket_details(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()
        return self.__all_tickets_details

    def get_all_supplies(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_supplies is None:
            self.set_all_supplies()
        return self.__all_supplies

    def get_all_cartridges(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_cartridges is None:
            self.set_all_cartridges()
        return self.__all_cartridges

    def get_all_packages_cartridges(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_packages_cartridges is None:
            self.set_all_packages_cartridges()
        return self.__all_packages_cartridges

    def get_all_cartridges_categories(self):
        if self.__all_cartridges_categories is None:
            self.set_all_cartridges_categories()
        return self.__all_cartridges_categories

    def get_all_extra_ingredients(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_extra_ingredients is None:
            self.set_all_extra_ingredients()

        return self.__all_extra_ingredients

    def get_all_cartridges_recipes(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_cartridges_recipes is None:
            self.set_all_cartridges_recipes()

        return self.__all_cartridges_recipes

    def get_all_packages_cartridges_recipes(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_packages_cartridges_recipes is None:
            self.set_all_package_cartridges_recipes()

        return self.__all_packages_cartridges_recipes

    def get_all_elements_in_warehouse(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__elements_in_warehouse is None:
            self.set_elements_in_warehouse()
        return self.__elements_in_warehouse

    def get_required_supplies(self):
        """
        :rtype: list 
        """
        required_supplies_list = []
        all_cartridges = self.get_all_cartridges()
        predictions = self.get_predictions_supplies()
        supplies_on_stock = self.get_all_elements_in_warehouse().filter(status="ST")

        ingredients = self.get_all_cartridges_recipes()
        
        for prediction in predictions:
            for cartridge in all_cartridges:
                if prediction['cartridge'] == cartridge:

                    ingredientes = ingredients.filter(cartridge=cartridge)                    

                    for ingredient in ingredientes:           

                        supply = ingredient.supply
                        name = ingredient.supply.name
                        cost = ingredient.supply.presentation_cost                        
                        measurement_unit = ingredient.supply.unit_conversion(ingredient.quantity)
                        measurement_quantity = ingredient.supply.measurement_conversion(ingredient.quantity)
                        supplier_unit = ingredient.supply.unit_conversion(ingredient.supply.measurement_quantity)
                        supplier_quantity = ingredient.supply.measurement_conversion(ingredient.supply.measurement_quantity)
                        quantity = ingredient.quantity
                        supplier = ingredient.supply.supplier
                            
                        count = 0

                        required_supply_object = {
                            'supply': supply,
                            'name': name,
                            'cost': cost,
                            'measurement_unit': measurement_unit,
                            'measurement_quantity': measurement_quantity,
                            'supplier_unit': supplier_unit,
                            'supplier_quantity': supplier_quantity,
                            'quantity': quantity,
                            'supplier': supplier,
                            'stock': 0,
                            'required': 0,
                            'full_cost': 0,
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
            if len(supplies_on_stock) > 0:
                for supply_on_stock in supplies_on_stock:
                    if supply_on_stock.supply == required_supply['supply']:
                        required_supply['stock'] = supply_on_stock.quantity
                        required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
                        required_supply['full_cost'] = \
                            required_supply['cost'] * \
                            math.ceil(required_supply['required'] / required_supply['measurement_quantity'])
                        break
                    else:
                        required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
                        required_supply['full_cost'] = \
                            required_supply['cost'] * \
                            math.ceil(required_supply['required'] / required_supply['measurement_quantity'])
                        required_supply['full_cost'] = \
                            required_supply['cost'] * \
                            math.ceil(required_supply['required'] / required_supply['measurement_quantity'])

            else:
                required_supply['required'] = max(0, required_supply['quantity'] - required_supply['stock'])
                required_supply['full_cost'] = \
                    required_supply['cost'] * \
                    math.ceil(required_supply['required'] / required_supply['measurement_quantity'])

        return required_supplies_list

    def get_always_popular_cartridge(self):
        """ 
        :rtype: django.db.models.query.QuerySet 
        """
        if self.__always_popular_cartridge is None:
            self.set_always_popular_cartridge()
        return self.__always_popular_cartridge

    def get_predictions_supplies(self):
        """ :rtype: list """
        if self.__predictions is None:
            self.set_predictions()
        return self.__predictions

    def get_supplies_on_stock_list(self):
        """ :rtype: list """
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
        if self.__today_popular_cartridge is None:
            self.set_today_popular_cartridge()
        return self.__always_popular_cartridge


class DinersHelper(object):
    def __init__(self):
        self.__all_diners = None
        self.__all_access_logs = None
        super(DinersHelper, self).__init__()

    def get_all_diners_logs_list(self, initial_date, final_date):
        helper = Helper()
        diners_logs_list = []

        diners_logs_objects = self.get_access_logs(initial_date, final_date)

        for diner_log in diners_logs_objects:
            diner_log_object = {
                'rfid': diner_log.RFID,
                'access': datetime.strftime(timezone.localtime(diner_log.access_to_room), "%B %d, %I, %H:%M:%S %p"),
                'number_day': helper.get_number_day(diner_log.access_to_room),
            }
            if diner_log.diner:
                diner_log_object['SAP'] = diner_log.diner.employee_number
                diner_log_object['name'] = diner_log.diner.name
            else:
                diner_log_object['SAP'] = ''
                diner_log_object['name'] = ''
            diners_logs_list.append(diner_log_object)
        return diners_logs_list

    def get_weeks_entries(self, initial_dt, final_dt):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()

        helper = Helper()
        limit_day = initial_dt + timedelta(days=1)
        weeks_list = []
        count = 1
        total_days = (final_dt - initial_dt).days

        while count <= total_days:
            diners_entries = self.__all_access_logs.filter(access_to_room__range=[initial_dt, limit_day])
            day_object = {
                'date': str(timezone.localtime(initial_dt).date().strftime('%d-%m-%Y')),
                'day_name': helper.get_name_day(initial_dt.date()), 'entries': diners_entries.count(),
                'number_day': helper.get_number_day(initial_dt)}

            weeks_list.append(day_object)

            # Reset data
            limit_day += timedelta(days=1)
            initial_dt += timedelta(days=1)
            count += 1

        return weeks_list

    def get_access_logs(self, initial_date, final_date):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()

        return self.__all_access_logs. \
            filter(access_to_room__range=(initial_date, final_date)). \
            order_by('-access_to_room')

    def get_access_logs_today(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()

        helper = Helper()
        year = int(datetime.now().year)
        month = int(datetime.now().month)
        day = int(datetime.now().day)
        initial_date = helper.naive_to_datetime(date(year, month, day))
        final_date = helper.naive_to_datetime(initial_date + timedelta(days=1))
        return self.__all_access_logs. \
            filter(access_to_room__range=(initial_date, final_date)). \
            order_by('-access_to_room')

    def get_all_access_logs(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()
        return self.__all_access_logs

    def get_diners_per_hour_json(self):
        hours_list = []
        hours_to_count = 12
        start_hour = 5
        customer_count = 0
        logs = self.get_access_logs_today()

        while start_hour <= hours_to_count:
            hour = {'count': None, }
            for log in logs:
                log_datetime = str(log.access_to_room)
                log_date, log_time = log_datetime.split(" ")

                if log_time.startswith("0" + str(start_hour)):
                    customer_count += 1
                hour['count'] = customer_count

            hours_list.append(hour)
            customer_count = 0
            start_hour += 1

        return json.dumps(hours_list)

    def get_diners_actual_week(self):
        if self.__all_access_logs is None:
            self.set_all_access_logs()
        helper = Helper()
        week_diners_list = []
        total_entries = 0
        days_to_count = helper.get_number_day(date.today())
        day_limit = days_to_count
        start_date_number = 0

        while start_date_number <= day_limit:
            day_object = {
                'date': str(helper.start_datetime(days_to_count).date().strftime('%d-%m-%Y')),
                'day_name': None,
                'entries': None,
                'number_day': helper.get_number_day(helper.start_datetime(days_to_count).date())
            }

            logs = self.__all_access_logs. \
                filter(access_to_room__range=[helper.start_datetime(days_to_count), helper.end_datetime(days_to_count)])

            for _ in logs:
                total_entries += 1

            day_object['entries'] = str(total_entries)
            day_object['day_name'] = helper.get_name_day(helper.start_datetime(days_to_count).date())

            week_diners_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_entries = 0
            start_date_number += 1

        return json.dumps(week_diners_list)

    def get_all_diners(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_diners is None:
            self.set_all_diners()
        return self.__all_diners

    def set_all_access_logs(self):
        self.__all_access_logs = AccessLog.objects.select_related('diner').order_by('-access_to_room')

    def set_all_diners(self):
        self.__all_diners = Diner.objects.all()


class PIDControl(object):
    def __init__(self):
        super(PIDControl, self).__init__()
        self.k1 = 1
        self.k2 = 1
        self.k3 = 1

    def get_pid_control(self):
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

                k1 * 5  = 7; 	k1 > 1
                k2 * 7  = 1; 	k2 = 1 ... aquí se mantuvo :D
                k3 * 13 = 13; 	k3 < 1 

                Ejemplo:
                De k3 ...
                si k3 > 1 entonces:
                    k3 > 13 ... por lo tanto k3 * 13 > 7... y eso no nos sirve, ya que
                    la venta real fue de 7, entonces nos estaríamos alejando más...
                    la idea es realizarle ajustes a la constante para que el valor se acerque a 7 :D
                    
        Debemos enviarle un dato, el cual es el día que queremos calcular la predicción. 
        Imaginando que hoy es DOMINGO 21 de mayo, por lo tanto enviamos el día a predecir. Es decir el Lunes 22 de mayo
        """

        day_to_predict = datetime.today() + timedelta(days=1)
        control_p = self.get_control_proporcional(day_to_predict)

    @staticmethod
    def get_control_proporcional(day_to_predict: datetime, product_object: Cartridge):
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
            febero... 28 ? :v
            marzo 31...
            abril .. 30
            mayo ... -> 15

            por lo tanto, 31 + 28 + 31 + 30 +15 = 135 -> Mayo es el día 135 del año
            Ap sería el promedio de todos los días 135 de todos los años que se tenga registro

        Primero debemos hacer las consultas pertinentes

        En esta parte nos auxiliaremos de isoweekday que nos proveé python... 
        https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday

        nos retornará un numero del 1 al 7 dependiendo de cada día
        siendo 1 lunes y 7 domingo
        así que una vez obtenidos todos los tickets, iteraremos su fecha de creacion
        y validaremos uno a uno los que cumplan a condicion requerida...

        Recordar: ya tenemos un método en helpers que nos retorna el numero de un día,
        pero nos retorna numero del 0 al 6, siendo lunes el 0 y 6 domingo

        Le tenemos que enviar el día del cual queremos obtener el numero
        correspondiente para hacer las validaciones 

        :rtype int
        """
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

        """ 
        Ahora obtendremos el promedio de todos esos días, como son tickets details
        entonces ya incluye el producto vendido y obvio, el precio base y el total, pero necesitamos conocer el
        id de la gelatina, por lo tanto debemos pasarlo por argumento en la funcion
        en este caso pasaremos el objecto como tal...
        Una vez encontrado el ticket detail correspondiente podremos añadir las elementos que se 
        vendieron en ese movimiento
        """

        total_elements = 0

        for ticket_detail in tickets_details_list:
            if ticket_detail.cartridge.id == product_object.id:
                'significa que es un ticket detail que vendio una gelatina'
                total_elements += ticket_detail.quantity

        # Y listo, ahora total_elements nos indicará los elementos vendidos en todos los tiempos
        #  en los cuales haya sido una venta en un día lunes :3 -> Procedemos a promediar

        day_average = total_elements / len(total_days_dict)
        # Promedio de dia = cantidad de elementos vendidos entre total de dias obtenidos

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

        # Aquí debe estar la lógica para obtener la variable Mp

        # Aquí debe estar la lógica para obtener la variable Ap

    @staticmethod
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


def get_control_derivativo(self):
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