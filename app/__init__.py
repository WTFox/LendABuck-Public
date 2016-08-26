__author__ = 'anthonyfox'
from flask import Flask

from app.views_paypal import paypal

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(paypal)

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404


from app import views