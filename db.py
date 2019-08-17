from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime

eng = create_engine('mysql://root:mysql@localhost/moneykeeper?charset=utf8mb4')
db_session = scoped_session(sessionmaker(autoflush=False,
                                         bind=eng))
md = MetaData(bind=eng)


def show_month_dbt_crt(start_date, last_date) -> dict:
    """Shows incomes and credits during date period"""
    sql_for_trans = '''SELECT date, transacion_type_id, SUM(value)
        FROM transaction
        WHERE date BETWEEN :w1 AND :w2
            AND transacion_type_id IN (:w3)
        GROUP BY date, transacion_type_id
        ORDER BY date, transacion_type_id'''

    res_trn = {'dbt': db_session.execute(sql_for_trans, {'w1': start_date, 'w2': last_date, 'w3': 1}).fetchall(),
               'crt': db_session.execute(sql_for_trans, {'w1': start_date, 'w2': last_date, 'w3': 2}).fetchall(),
               'sums': {
                   'plus': show_sums(start_date, last_date, 1),
                   'minus': show_sums(start_date, last_date, 2)
               }}

    return res_trn


def show_sums(fdate, ldate, trn_type_id: int) -> float:
    """Shows sum per date period"""
    sql_for_sum = '''SELECT SUM(value)
                    FROM transaction
                    WHERE date BETWEEN :w1 AND :w2
                        AND transacion_type_id = :w3'''
    sum_of_period = db_session.execute(sql_for_sum, {'w1': fdate, 'w2': ldate, 'w3': trn_type_id}).fetchone()
    if sum_of_period[0] is None:
        return 0
    else:
        return sum_of_period[0]


def add_trn_in_db(usr, trn_t_id, prc_id, d, val=0, acc_fr=1, comment=''):
    if type(d) != datetime.date:
        try:
            d = datetime.datetime.strptime(d, '%Y-%m-%d')
        except TypeError:
            raise DateError('Error in date')

    try:
        int_tr_id = int(trn_t_id)
    except ValueError:
        raise TrnTypeIdError('Ошибка идентификатора вида расходов//расходов')

    try:
        float_val = float(val)
    except ValueError:
        raise InputError('Неверный формат суммы')

    try:
        int_acc_fr = int(acc_fr)
    except ValueError:
        raise InputError('Счет отправки не существует')

    if int_tr_id == 2 or (trn_t_id == 3 and int_acc_fr == 1):
        new_balance = get_balance() - float_val
    elif int_tr_id == 3 and int_acc_fr == 2:
        new_balance = get_sber_balance() - float_val
    else:
        new_balance = 0

    if new_balance < 0:
        raise BalanceBelowZeroError('Баланс не может быть меньше нуля')

    try:
        sql_for_adding_trans = '''INSERT INTO transaction(user_id, transacion_type_id, 
        purchase_id, date, value, account_from_id, comment)
        VALUES(:v1, :v2, :v3, :v4, :v5, :v6, :v7)'''
        db_session.execute(sql_for_adding_trans, {'v1': usr, 'v2': trn_t_id,
                                                  'v3': prc_id, 'v4': d,
                                                  'v5': val, 'v6': acc_fr, 'v7': comment})
        db_session.commit()
    except ValueError:
        raise DateError
    except Exception:
        db_session.rollback()
        raise SQLError('Error in SQL-code')


def get_transactions_per_day(date_parameters: dict):
    """Selects transactions per day"""
    sql_for_tr_per_day = '''SELECT t_t.name tt_id, 
        CONCAT(g.name, ' - ', p.name) group_purchase, u.fname, t.value
        FROM transaction t 
        INNER JOIN transacion_type t_t ON t.transacion_type_id = t_t.transacion_type_id
        INNER JOIN purchase p ON t.purchase_id = p.purchase_id
        INNER JOIN group_goods g ON p.group_goods_id = g.group_goods_id
        INNER JOIN user u ON t.user_id = u.user_id
        WHERE t.date = :u1'''
    try:
        tr_per_day = db_session.execute(sql_for_tr_per_day, {'u1': datetime.date(int(date_parameters['y']),
                                                                                 int(date_parameters['m']),
                                                                                 int(date_parameters['d']))}).fetchall()
    except ValueError:
        raise DateError

    return tr_per_day


def get_trans_type():
    """Selects all transaction types"""
    return db_session.execute('SELECT transacion_type_id, name FROM transacion_type').fetchall()


def get_owner():
    """Selects all users from user"""
    return db_session.execute('SELECT user_id, fname FROM user').fetchall()


def get_month_values(fday, lday, trn_type_id):
    """Selects incomes/costs per month"""
    sql_for_month_values = '''SELECT g.name g_name, SUM(value) sum_value
                            FROM transaction t 
                            INNER JOIN purchase p ON t.purchase_id = p.purchase_id 
                            INNER JOIN group_goods g ON p.group_goods_id = g.group_goods_id
                            WHERE t.date BETWEEN :w1 AND :w2
                            AND t.transacion_type_id = :w3
                            GROUP BY 1 ORDER BY 2 DESC;'''
    return db_session.execute(sql_for_month_values, {'w1': fday, 'w2': lday, 'w3': trn_type_id}).fetchall()


def get_top(fday, lday):
    """Show top purchases per month"""
    sql_for_top = '''SELECT CONCAT(g.name, ' - ', p.name) p_name, SUM(t.value) val FROM transaction t
                    INNER JOIN purchase p ON t.purchase_id = p.purchase_id
                    INNER JOIN group_goods g ON p.group_goods_id = g.group_goods_id 
                    WHERE t.date BETWEEN :w1 AND :w2
                    AND t.transacion_type_id = 2 AND t.save_money = 'N'
                    GROUP BY p.name 
                    ORDER BY 2 DESC LIMIT 10;'''
    return db_session.execute(sql_for_top, {'w1': fday, 'w2': lday}).fetchall()


def get_last_months_purchase(m_for_show=6, datepar='NOW()'):
    """Getting incomes and costs grouped by month"""
    sql_for_exec = '''SELECT MONTH(t.date) month,
    ( SELECT SUM(t1.value) FROM transaction t1 WHERE t1.transacion_type_id = 1 AND t1.save_money = 'N'
        AND MONTH(t1.date) = MONTH(t.date) AND YEAR(t1.date) = YEAR(t.date) GROUP BY YEAR(t1.date), MONTH(t1.date) ) incomes,
    ( SELECT SUM(t2.value) FROM transaction t2 WHERE t2.transacion_type_id = 2 AND t2.save_money = 'N'
        AND MONTH(t2.date) = MONTH(t.date) AND YEAR(t2.date) = YEAR(t.date) GROUP BY YEAR(t2.date), MONTH(t2.date) ) costs
    FROM transaction t
    WHERE date BETWEEN DATE_SUB(DATE(:w2), INTERVAL :w1 MONTH) AND DATE(:w2)
    GROUP BY YEAR(t.date), MONTH(t.date);'''
    return db_session.execute(sql_for_exec, {'w1': m_for_show, 'w2': datepar}).fetchall()


def get_balance(last_month=datetime.date.today().month, last_year=datetime.date.today().year):
    """Get balance of account"""
    sql_for_balance = '''SELECT
    (SELECT IFNULL(SUM(t1.value), 0) FROM transaction t1 
        WHERE MONTH(t1.date) <= :w1 AND YEAR(t1.date) <= :w2
        AND t1.transacion_type_id = 1 AND t1.save_money = 'N') -
    (SELECT IFNULL(SUM(t2.value), 0) FROM transaction t2 
        WHERE MONTH(t2.date) <= :w1 AND YEAR(t2.date) <= :w2
        AND t2.transacion_type_id = 2 AND t2.save_money = 'N') balance;'''
    res = db_session.execute(sql_for_balance, {'w1': last_month, 'w2': last_year}).fetchall()[0][0] - get_sber_balance()
    return res if res is not None else 0


def get_accounts():
    """Get accounts"""
    sql_for_accs = '''SELECT * FROM account;'''
    return db_session.execute(sql_for_accs).fetchall()


def get_sber_balance(m=datetime.date.today().month, y=datetime.date.today().year):
    """Get sber balance"""
    sql_for_sber_balance = '''SELECT
    (SELECT IFNULL(SUM(t1.value), 0) FROM transaction t1 
        WHERE MONTH(t1.date) = :w1 AND YEAR(t1.date) = :w2 AND t1.transacion_type_id = 3 
        AND t1.account_from_id = 1) - 
    (SELECT IFNULL(SUM(t2.value), 0) FROM transaction t2
        WHERE MONTH(t2.date) = :w1 AND YEAR(t2.date) = :w2 AND t2.transacion_type_id = 3
        AND t2.account_from_id = 2) sber_bal'''
    res = db_session.execute(sql_for_sber_balance, {'w1': m, 'w2': y}).fetchall()[0][0]
    return res if res is not None else 0


def get_sber_transactions(m, y):
    """Get operions for current period"""
    sql_for_sber_trns = '''SELECT t.date, a.name, t.comment, u.fname, t.value FROM transaction t
            INNER JOIN account a ON t.account_from_id = a.account_id
            INNER JOIN user u ON t.user_id = u.user_id
            WHERE MONTH(t.date) = :w1 AND YEAR(t.date) = :w2
            AND transacion_type_id = 3 ORDER BY t.date'''
    return db_session.execute(sql_for_sber_trns, {'w1': m, 'w2': y}).fetchall()


class SQLError(Exception):
    pass


class DateError(Exception):
    pass


class TrnTypeIdError(Exception):
    pass


class BalanceBelowZeroError(Exception):
    pass


class InputError(Exception):
    pass
