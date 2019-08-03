import datetime
import calendar


class MonthFindError(KeyError):
    pass


class DatesForCalendarCreation:
    """For getting changed dates for calendar"""
    def __init__(self, cal_year, cal_month):
        self.cal_month = cal_month
        self.cal_year = cal_year

    def __setattr__(self, key, value):
        try:
            if key == 'cal_month':
                datetime.date(2015, value, 1)
            elif key == 'cal_year':
                datetime.date(value, 1, 1)
            elif key == 'prev_parameter' or key == 'last_parameter':
                if type(key) != 'str':
                    raise AttributeError('Invalid next or prev parameter. It must be \'str\'')
            else:
                raise AttributeError('Only month and year maybe inited')
        except TypeError and ValueError:
            raise AttributeError('Bad parameters for date')
        self.__dict__[key] = value

    def f_day(self):
        return datetime.date(self.cal_year, self.cal_month, 1)

    def l_day(self):
        return datetime.date(self.cal_year,
                             self.cal_month,
                             calendar.monthrange(self.cal_month, self.cal_month)[1])

    def prev_date(self):
        new_date = self.f_day() - datetime.timedelta(days=1)
        return self.__change_date(new_date.month, new_date.year)

    def next_date(self):
        new_date = self.l_day() + datetime.timedelta(days=1)
        return self.__change_date(new_date.month, new_date.year)

    def __change_date(self, new_month, new_year):
        self.cal_month, self.cal_year = [new_month, new_year]
        return self.cal_month, self.cal_year




months_dict = {
    'январь': 1,
    'февраль': 2,
    'март': 3,
    'апрель': 4,
    'май': 5,
    'июнь': 6,
    'июль': 7,
    'август': 8,
    'сентябрь': 9,
    'октябрь': 10,
    'ноябрь': 11,
    'декабрь': 12,
}


def get_month(month_name: str) -> int:
    try:
        find_num = months_dict[month_name.lower()]
        return find_num
    except KeyError:
        raise MonthFindError


def get_rus_months() -> list:
    month_list = [mon.capitalize() for mon in months_dict.keys()]
    return month_list


def get_rus_month(month_num) -> str:
    month_list = get_rus_months()
    return month_list[month_num - 1]


def get_money(date, trx_group: list) -> float:
    for trn in trx_group:
        if date == trn[0]:
            return trn[-1]
    return 0
