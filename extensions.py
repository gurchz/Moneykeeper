import datetime
import calendar
from db import get_balance, get_sber_balance


class MonthFindError(KeyError):
    """Custom error during month-searching"""
    pass


class NoJSONData(Exception):
    """Custom error for showing that object has no data"""
    pass


class InvalidJSONData(Exception):
    """Custom error for showing that object has invalid fields"""
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


class JSONData:
    """For storing and operating JSON data"""
    def __init__(self, json_obj):
        self.json_obj = json_obj
        self.duplicates = None
        self.fields_num = None
        self.grouped_json_obj = None

    def group_data(self):
        if type(self.json_obj) == list:
            self.__finding_duplicates()
            if self.duplicates is not None and self.fields_num is not None:
                self.__deviding_elements()
        return self.grouped_json_obj

    def __finding_duplicates(self):
        if len(self.json_obj) == 0:
            raise NoJSONData
        duplicates = {}
        for list_data in self.json_obj:
            try:
                duplicates.setdefault(list_data['name'], 0)
                duplicates[list_data['name']] += 1
            except KeyError:
                raise InvalidJSONData('Некорректный зарпос')
        return self.__checking_duplicates(duplicates)

    def __checking_duplicates(self, dupl):
        res_duplicates = {v for v in dupl.values()}
        len_dupl = len(res_duplicates)
        if len_dupl == 0 or len_dupl > 1:
            raise InvalidJSONData('Ошибка при сопоставлении записей')
        elif len_dupl == 1:
            self.duplicates = res_duplicates.pop()
            self.fields_num = len(dupl)

    def __deviding_elements(self):
        if self.duplicates is None or self.fields_num is None:
            raise InvalidJSONData('I have no info about JSON object fields')
        if type(self.json_obj) == list:
            self.grouped_json_obj = []
            form_collection = {}
            row_counter = 0
            for row in self.json_obj:
                try:
                    form_collection[row['name']] = row['value']
                except KeyError:
                    raise InvalidJSONData('Bad JSON object')
                row_counter += 1
                if row_counter == self.fields_num:
                    self.grouped_json_obj.append(form_collection)
                    form_collection = {}
                    row_counter = 0
            if len(self.grouped_json_obj) != self.duplicates:
                raise InvalidJSONData('Bad JSON Object: duplicates and grouped data mismatch')


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
    """Returns order number of month"""
    try:
        find_num = months_dict[month_name.lower()]
        return find_num
    except KeyError:
        raise MonthFindError


def get_rus_months() -> list:
    """Returns russian names of months"""
    month_list = [mon.capitalize() for mon in months_dict.keys()]
    return month_list


def get_rus_month(month_num) -> str:
    """Returns single russian month"""
    month_list = get_rus_months()
    return month_list[month_num - 1]


def get_money(date, trx_group: list) -> float:
    """Returns sum by date"""
    for trn in trx_group:
        if date == trn[0]:
            return trn[-1]
    return 0


def detect_general_parameters(m, y) -> dict:
    """Returns standard parameters of app"""
    return {'date': str(m) + '.' + str(y),
            'balance': get_balance(m, y),
            'sber_balance': get_sber_balance(m, y)}


def get_field_props(fields: list) -> list:
    """Returns html-tag and other properties by db-field (with mapping)"""
    # Mapping fields
    field_tag_map = [{'edit': False, 'tag': 'select', 'attr': None, 'name': 'pp_name', 'ref': 'pp_pur_id'},
                     {'edit': True, 'tag': 'input', 'attr': 'date', 'name': 'pp_date'},
                     {'edit': True, 'tag': 'input', 'attr': 'text', 'name': 'pp_val'}]

    # Extracting field keys which are mentioned in parameters
    return [field_attrs for field_attrs in field_tag_map if field_attrs['name'] in fields]
