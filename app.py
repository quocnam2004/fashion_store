from flask import Flask
from app.routes import app_routes
from app.account_module import account_bp


app = Flask(__name__)

app.secret_key = "assa-fashion-secret"

app.register_blueprint(app_routes, url_prefix="")
app.register_blueprint(account_bp, url_prefix="")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
