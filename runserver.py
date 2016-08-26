__author__ = 'anthonyfox'

from app import app

if app.config['DEBUG']:
    app.run(debug=True, port=5001)
