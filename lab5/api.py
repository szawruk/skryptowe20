from datetime import datetime

import flask
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

import lab5.db_service as db_service

DATE_FORMAT = "%y-%m-%d"
LIMITER_LIMIT = '1/second'
DEFAULT_CACHE_TIMEOUT = 60

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CACHE_TYPE'] = 'simple'
limiter = Limiter(app, key_func=get_remote_address)
cache = Cache(app)


def check_date(str_date):
    isValidDate = True
    try:
        year, month, day = str_date.split('-')
        datetime(int(year), int(month), int(day))
    except ValueError:
        isValidDate = False

    return isValidDate


@app.route('/api/rates/usd/<date>', methods=['GET'])
@limiter.limit(LIMITER_LIMIT)
@cache.cached(timeout=DEFAULT_CACHE_TIMEOUT)
def get_rate_for_one_day(date):
    if not check_date(date):
        return jsonify({'message': 'Entered date is not correct'})
    else:
        data = db_service.get_usd_exchange_rate_for_one_day(date)
        if data is None:
            return jsonify({'message': 'Brak danych dla tej daty'})
        else:
            return jsonify({'date': data['date'], 'rate': data['rate'], 'interpolated': data['interpolated']})


@app.route('/api/rates/usd/<start_date>/<end_date>', methods=['GET'])
@limiter.limit(LIMITER_LIMIT)
@cache.cached(timeout=DEFAULT_CACHE_TIMEOUT)
def get_rate_for_days_range(start_date, end_date):
    if not (check_date(start_date) and check_date(end_date)):
        return jsonify({'message': 'Entered date is not correct'})
    elif datetime.strptime(db_service.get_usd_exchange_min_date(), "%Y-%m-%d").date() > datetime.strptime(start_date, "%Y-%m-%d").date() or datetime.strptime(db_service.get_usd_exchange_max_date(), "%Y-%m-%d").date() < datetime.strptime(end_date, "%Y-%m-%d").date():
        return jsonify({'message': 'No data for this date range'})
    else:
        data = db_service.get_usd_exchange_rate_for_days_range(start_date, end_date)
        if data is None:
            return jsonify({'message': 'Brak danych dla tego zakresu'})
        else:
            return jsonify(data)


@app.route('/api/sales/<date>', methods=['GET'])
@limiter.limit(LIMITER_LIMIT)
@cache.cached(timeout=DEFAULT_CACHE_TIMEOUT)
def get_sales_sum_for_day_x(date):
    if not check_date(date):
        return jsonify({'message': 'Entered date is not correct'})
    else:
        data = db_service.get_sales_sum_for_day_x(date)
        if data is None:
            return jsonify({'message': 'Brak danych dla tej daty'})
        else:
            return jsonify(data)


app.run()
print("Input date is not valid..")
