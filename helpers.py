import math
import pytz

from datetime import datetime, date, timedelta, time


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
        print(datetime_now)
        name_day = date(datetime_now.year, datetime_now.month, datetime_now.day)
        print(name_day.strftime('%A').upper())
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
    """docstring for LeastSquares"""

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

        for item in self.__x:
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

        for item in self.__x:
            forecast_list.append(self.get_a() + self.get_b() * self.__periodic_list[count])
            count += 1

        return forecast_list
