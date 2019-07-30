class MonthFindError(KeyError):
    pass


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
        find_num = months_dict[month_name]
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
