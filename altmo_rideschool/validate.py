from functools import wraps
from flask import session, redirect, url_for 

def user_required(route_func):
    @wraps(route_func)
    def decorated_route(*args, **kwargs):
        if session.get('role') != 'participant':
            error_message = 'Please login as a valid user to view this page.'
            return redirect(url_for('logins.index', error_message=error_message))
        return route_func(*args, **kwargs)
    return decorated_route

def trainer_required(route_func):
    @wraps(route_func)
    def decorated_route(*args, **kwargs):
        if session.get('role') != 'trainer':
            error_message = 'Please login as a valid user to view this page.'
            return redirect(url_for('logins.index', error_message=error_message))
        return route_func(*args, **kwargs)
    return decorated_route

def admin_required(route_func):
    @wraps(route_func)
    def decorated_route(*args, **kwargs):
        if session.get('role') != 'admin': 
            error_message = 'Please login as a valid user to view this page.'
            return redirect(url_for('logins.index', error_message=error_message))
        return route_func(*args, **kwargs)
    return decorated_route

