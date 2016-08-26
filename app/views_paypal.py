__author__ = 'anthonyfox'

from flask import Blueprint

paypal = Blueprint('paypal', __name__, template_folder='templates/paypal', url_prefix='/paypal')

@paypal.route('/makePayment')
def make_payment():
    return 'This will be the route to make a payment.'