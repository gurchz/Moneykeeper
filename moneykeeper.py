from flask import Flask, render_template, request, redirect, url_for, flash
import json
import calendar
from extensions import (get_month, get_rus_months, get_rus_month,
                        get_money, MonthFindError, DatesForCalendarCreation, detect_general_parameters,
                        get_field_props, JSONData)

from db import (db_session, show_month_dbt_crt, add_trn_in_db,
                get_trans_type, get_owner, SQLError, DateError,
                get_transactions_per_day, get_month_values, show_sums,
                get_top, get_last_months_purchase, get_balance, get_accounts,
                get_sber_balance, get_sber_transactions, get_planning_parameters,
                get_planning_sums_by_user, get_planning_groups, update_planning_from_json)
import datetime

app = Flask(__name__)
app.config['MONTH_YEAR'] = {'m': datetime.date.today().month,
                            'y': datetime.date.today().year}


@app.route('/')
@app.route('/main')
def show_main_page() -> 'html':
    return render_template('main.html', the_title='Main page')


@app.route('/dashboard', methods=['GET'])
def dashboard() -> 'html':
    d_date = DatesForCalendarCreation(app.config['MONTH_YEAR']['y'], app.config['MONTH_YEAR']['m'])
    dash = dict()
    fday, lday = (d_date.f_day(), d_date.l_day())
    dash['month_incomes'] = get_month_values(fday, lday, 1)
    dash['month_costs'] = get_month_values(fday, lday, 2)
    dash['month_totals'] = {'incomes': show_sums(fday, lday, 1),
                            'costs': show_sums(fday, lday, 2)}
    dash['top_purchase'] = get_top(fday, lday)
    dash['cur_balance'] = get_balance()
    dash['sber_balance'] = 100
    return render_template('dashboard.html',
                           the_title='Dashboard',
                           the_dash=dash,
                           for_nav=detect_general_parameters(app.config['MONTH_YEAR']['m'],
                                                             app.config['MONTH_YEAR']['y']))


@app.route('/money_calendar', methods=['GET', 'POST'])
def money_calendar() -> 'html':
    # when data is posted
    if request.method == 'POST':
        """For adding new transactions"""
        try:
            add_trn_in_db(request.form['owner'], request.form['trtype'], request.form['subgr'],
                          val=request.form['val'], d=request.form['date'])
        except SQLError:
            flash('Error in SQL-code', 'danger')
        except DateError:
            flash('Error in date', 'danger')
        except Exception as e:
            flash(str(e), 'danger')
        else:
            flash('Data was added successfully', 'success')
        finally:
            return redirect(url_for('money_calendar'))

    # When new date was chosen by form
    if request.args.get('month') is not None and request.args.get('year') is not None:
        try:
            app.config['MONTH_YEAR'] = {'m': get_month(request.args.get('month').lower()),
                                        'y': int(request.args.get('year'))}
        except MonthFindError and ValueError and KeyError:
            flash('Error In Date', 'danger')

    # Creating calendar object with dates and calculating necessary date values
    cal_obj = calendar.Calendar(0)
    cal_pars_prev, cal_pars_next = ['prev', 'next']
    dates = DatesForCalendarCreation(app.config['MONTH_YEAR']['y'], app.config['MONTH_YEAR']['m'])

    # When we need to choose previous or next year by pointers
    if request.args.get('date_change') == cal_pars_prev:
        app.config['MONTH_YEAR']['m'], app.config['MONTH_YEAR']['y'] = dates.prev_date()
    elif request.args.get('date_change') == cal_pars_next:
        app.config['MONTH_YEAR']['m'], app.config['MONTH_YEAR']['y'] = dates.next_date()

    # Creating dictionary with calendar values and trn info
    cal = dict()
    cal['months'] = get_rus_months()
    cal['weekdays'] = [weekday for weekday in calendar.day_abbr]
    cal['years'] = [yr for yr in range(2015, 2020)]
    cal['transactions'] = show_month_dbt_crt(dates.f_day(), dates.l_day())
    cal['days'] = [{'date': d,
                    'minus': get_money(datetime.date(dates.cal_year, dates.cal_month, d),
                                       cal['transactions']['dbt']) if d != 0 else 0,
                    'plus': get_money(datetime.date(dates.cal_year, dates.cal_month, d),
                                      cal['transactions']['crt']) if d != 0 else 0}
                   for w in cal_obj.monthdayscalendar(dates.cal_year, dates.cal_month) for d in w]
    cal['first_date'] = datetime.datetime(dates.cal_year, dates.cal_month, 1).strftime('%Y-%m-%d')
    cal['new_date'] = {'m': get_rus_month(dates.cal_month), 'y': dates.cal_year}
    cal['trans_type'] = get_trans_type()
    cal['owners'] = get_owner()
    cal['previous_month'], cal['next_month'] = [cal_pars_prev, cal_pars_next]

    return render_template('calendar.html',
                           the_title='Календарь',
                           the_calendar=cal,
                           for_nav=detect_general_parameters(app.config['MONTH_YEAR']['m'],
                                                             app.config['MONTH_YEAR']['y']))


@app.route('/show')
def show() -> 'json':
    """For AJAX-requests"""
    trans_type = request.args.get('trtype')
    gr_id = request.args.get('group')
    d_params = {'d': request.args.get('trn_day'),
                'm': request.args.get('trn_month'),
                'y': request.args.get('trn_year')}
    last_m_pars = request.args.get('show_months')
    show_acc = request.args.get('show_accounts')

    # check get-request-arguments
    db_res = 'Parameters are not identified'
    if trans_type is not None:
        db_res = db_session.execute('''SELECT group_goods_id, name FROM group_goods
                            WHERE transacion_type_id = :w1''', {'w1': trans_type}).fetchall()
    elif gr_id is not None:
        db_res = db_session.execute('''SELECT purchase_id, name FROM purchase
                            WHERE group_goods_id = :w1''', {'w1': gr_id}).fetchall()

    elif last_m_pars is not None:
        if not json.loads(last_m_pars):
            return
        app_date = datetime.date(app.config['MONTH_YEAR']['y'], app.config['MONTH_YEAR']['m'], 1)
        last_m_pur = get_last_months_purchase(datepar=app_date)
        db_res = {k: [itm[k] if itm[k] is not None else 0 for itm in last_m_pur]
                  for rw in last_m_pur for k in rw.keys()}
        try:
            db_res['month'] = [get_rus_month(m) for m in db_res['month']]
        except KeyError:
            db_res.setdefault('month', '')

    elif None not in d_params.values():
        try:
            d_params['m'] = get_month(d_params['m'])
            db_res = get_transactions_per_day(d_params)
            if len(db_res) == 0:
                db_res = [['Данные не найдены']]
        except MonthFindError:
            pass

    elif show_acc is not None:
        if json.loads(show_acc):
            db_res = get_accounts()

    elif request.args.get('upd_sber_data') is not None:
        if json.loads(request.args.get('upd_sber_data')):
            m, y = [app.config['MONTH_YEAR']['m'], app.config['MONTH_YEAR']['y']]
            db_res = {'bal': get_balance(m, y),
                      'sber_bal': get_sber_balance(m, y),
                      'sber_tbl': [{ky: val if ky != 'date' else str(val.day) + ' ' + get_rus_month(val.month) + ' ' + str(val.year)
                                    for ky, val in line.items()} for line in get_sber_transactions(m, y)]}

    elif request.args.get('show_users') is not None:
        if json.loads(request.args.get('show_users')):
            db_res = get_owner()

    elif request.args.get('month_year') is not None:
        if json.loads(request.args.get('month_year')):
            db_res = {'month': app.config['MONTH_YEAR']['m'],
                      'year': app.config['MONTH_YEAR']['y']}

    elif request.args.get('show_planning') is not None and request.args.get('planning_group') is not None:
        if json.loads(request.args.get('show_planning')):
            d = datetime.date(app.config['MONTH_YEAR']['y'], app.config['MONTH_YEAR']['m'], 1)
            planning_groups = {pl_gr_row['pl_gr_id']: pl_gr_row['name'] for pl_gr_row in get_planning_groups()}
            par_plan_gr = request.args.get('planning_group')
            if par_plan_gr not in planning_groups:
                db_res = {'message': 'Не указана группа планирования'}
            else:
                db_res = {'title': planning_groups[par_plan_gr],
                          'data': [{k: v for k, v in plan_par_row.items()}
                                   for plan_par_row in get_planning_parameters(par_plan_gr,
                                                                               cur_date=d,
                                                                               with_pur_id=True)]}
                if len(db_res['data']) != 0:
                    db_res_keys = list(db_res['data'][0].keys())
                    db_res['keys'] = get_field_props(db_res_keys)

    # we need list-type for returning the json-answer
    if type(db_res) == list:
        db_res_for_json = [list(line) for line in db_res]
    else:
        db_res_for_json = db_res

    # json-answer
    return json.dumps(db_res_for_json, sort_keys=True, ensure_ascii=False)


@app.route('/submit/<obj>', methods=['POST'])
def submit(obj) -> 'json':
    try:
        if obj == 'default':
            add_trn_in_db(usr=request.form['user'], trn_t_id=3, prc_id=22,
                          d=datetime.date.today(), val=request.form['val'],
                          acc_fr=request.form['account_from'])
        elif obj == 'planning':
            json_inp_grouped = JSONData(json.loads(request.data)).group_data()
            date_of_planning = datetime.date(app.config['MONTH_YEAR']['y'],
                                             app.config['MONTH_YEAR']['m'], 1)
            update_planning_from_json(json_inp_grouped, date_of_planning)
        json_answ = {'class': 'success',
                     'txt': 'Данные добавлены успешно'}
    except SQLError:
        json_answ = {'class': 'danger',
                     'txt': 'Ошибка при записи'}
    except KeyError:
        json_answ = {'class': 'danger',
                     'txt': 'Не все обязательные поля заполенены'}
    except Exception as e:
        json_answ = {'class': 'danger',
                     'txt': str(e)}
    finally:
        return json.dumps(json_answ, ensure_ascii=False)


@app.route('/planning')
def planning() -> 'html':
    d = datetime.date(app.config['MONTH_YEAR']['y'], app.config['MONTH_YEAR']['m'], 1)
    plan = {'incomes': get_planning_parameters('INC', cur_date=d),
            'total_incomes': get_planning_sums_by_user(cur_date=d),
            'costs_man': get_planning_parameters('MAN', d),
            'costs_opt': get_planning_parameters(cur_date=d),
            'costs_out': get_planning_parameters('OUT', d)}

    return render_template('planning.html',
                           the_title='Планирование',
                           the_plan=plan,
                           for_nav=detect_general_parameters(app.config['MONTH_YEAR']['m'],
                                                             app.config['MONTH_YEAR']['y']))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.close()


app.secret_key = 'J\xb5\x01?>\x9c\xb1C*c\xeb\x0e\xd6}%\xd7'


if __name__ == '__main__':
    app.run(debug=True)
