from flask import Flask, render_template, request, redirect, url_for, flash
import json
import calendar
from extensions import (get_month, get_rus_months, get_rus_month,
                        get_money, MonthFindError, DatesForCalendarCreation)
from db import (db_session, show_month_dbt_crt, add_trn_in_db,
                get_trans_type, get_owner, SQLError, DateError,
                get_transactions_per_day)
import datetime

app = Flask(__name__)
app.config['MONTH_YEAR'] = {'m': datetime.date.today().month,
                            'y': datetime.date.today().year}


@app.route('/')
@app.route('/main')
def show_main_page() -> 'html':
    return render_template('main.html', the_title='Main page')


@app.route('/dashboard')
def dashboard() -> 'html':
    return render_template('dashboard.html', the_title='Dashboard')


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

    # Creating calendar object with dates and calculating nessecary date values
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

    return render_template('calendar.html', the_title='Календарь', the_calendar=cal)


@app.route('/show')
def show() -> 'json':
    """For AJAX-requests"""
    trans_type = request.args.get('trtype')
    gr_id = request.args.get('group')
    d_params = {'d': request.args.get('trn_day'),
                'm': request.args.get('trn_month'),
                'y': request.args.get('trn_year')}

    # check get-request-arguments
    db_res = 'Parameters are not identified'
    if trans_type is not None:
        db_res = db_session.execute('''SELECT group_goods_id, name FROM group_goods
                            WHERE transacion_type_id = :w1''', {'w1': trans_type}).fetchall()
    elif gr_id is not None:
        db_res = db_session.execute('''SELECT purchase_id, name FROM purchase
                            WHERE group_goods_id = :w1''', {'w1': gr_id}).fetchall()
    elif None not in d_params.values():
        try:
            d_params['m'] = get_month(d_params['m'])
            db_res = get_transactions_per_day(d_params)
            if len(db_res) == 0:
                db_res = [['Данные не найдены']]
        except MonthFindError:
            pass

    # we need list-type for returning the json-answer
    db_res_for_json = [list(line) for line in db_res]

    # json-answer
    return json.dumps(db_res_for_json, sort_keys=True, ensure_ascii=False)


@app.route('/planning')
def planning() -> 'html':
    return render_template('planning.html', the_title='Планирование')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.close()


app.secret_key = 'J\xb5\x01?>\x9c\xb1C*c\xeb\x0e\xd6}%\xd7'


if __name__ == '__main__':
    app.run(debug=True)
