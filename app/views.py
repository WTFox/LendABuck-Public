# -- coding: utf-8 --

from datetime import timedelta

from flask import render_template, url_for, request, redirect, g, session, jsonify
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail, Message

from .dbhelper import DB

from app import app

bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

# TODO: Add logging.
# TODO: Add option to close requests that I own


class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    """
    Simple User class
    """

    def __init__(self, accountid):
        self.accountid = accountid
        with DB(**app.config['ARVIXE_LENDA']) as db:
            userInfo = db.call_proc('Ryan.FD_Lend_Details_by_accountid', accountid=accountid)[0]
            self.displayname = userInfo['displayName']
            self.emailaddress = userInfo['emailaddress']

    @classmethod
    def get(cls, accountid):
        """
        Return user instance of id, return None if not exist
        """

        try:
            return cls(accountid)
        except UserNotFoundError:
            return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.accountid)

    def __repr__(self):
        return '<User %r>' % self.accountid


@app.before_request
def before_request():
    g.user = current_user
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@login_manager.user_loader
def load_user(accountid):
    return User.get(accountid)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        userDisplayName = request.form['inputName']
        userEmail = request.form['inputEmail']
        userPassword = request.form['inputPassword']
        hash_pw = bcrypt.generate_password_hash(userPassword)

        with DB(**app.config['ARVIXE_LENDA']) as db:
            result = db.call_proc('Ryan.FD_Lend_Create_users', emailaddress=userEmail, password=hash_pw,
                                  displayname=userDisplayName)[0]

        if authenticate_user(userEmail, userPassword):
            return redirect(url_for('dashboard'))

        return jsonify(result=result)


@app.route('/signIn', methods=['POST'])
def signIn():
    userEmail = request.json['email']
    userPassword = request.json['password']

    if authenticate_user(userEmail, userPassword):
        return jsonify(url=url_for('dashboard'))

    return jsonify(message="Something went wrong.")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    requestsWithDetails = []
    with DB(**app.config['ARVIXE_LENDA']) as db:
        myOffers = db.call_proc('Ryan.fd_lend_list_offers_lenderid', accountid=g.user.get_id())
        myRequest = db.call_proc('Ryan.FD_List_request_per_userid', accountid=g.user.get_id())

        requests = db.call_proc('Ryan.FD_List_request', accountid=g.user.get_id())
        for request in requests:
            requestDetails = request
            requestDetails['Offers'] = db.call_proc('Ryan.FD_List_Offers_per_Request_ID', requestid=request['ID'])
            requestsWithDetails.append(requestDetails)

    context = dict(
        requests=requestsWithDetails,
        accountid=g.user.get_id(),
        displayname=g.user.displayname,
        myOffers=myOffers,
        myRequest=myRequest,
    )

    return render_template('dashboard.html', **context)


@app.route('/submitRequest', methods=["POST"])
@login_required
def submit_request():
    requestData = dict(
        AmountNeeded=request.form['amountNeeded'],
        ReasonNeeded=request.form['reasonNeeded'],
        AccountID=request.form['accountID'],
        ExpectedPaybackDays=request.form['expectedPaybackDays'],
        MaxInterest=int(request.form['maxInterest']) / 100,
        RequestExpiration=request.form['requestExpiration']
    )

    with DB(**app.config['ARVIXE_LENDA']) as db:
        resp = db.call_proc('ryan.FD_Lend_Create_Request', **requestData)

    return redirect(url_for('dashboard'))


@app.route('/submitOffer', methods=["POST"])
@login_required
def submit_offer():
    offerData = dict(
        LenderID=g.user.get_id(),
        RequestID=request.form['currentRequestID'],
        InterestRate=float(request.form['InterestRate']) / 100,
        PayBackDays=request.form['paybackDays'],
        note=request.form['message']
    )

    with DB(**app.config['ARVIXE_LENDA']) as db:
        resp = db.call_proc('Ryan.FD_Lend_Create_Offer', **offerData)

    return redirect(url_for('dashboard'))


@app.route('/requestDetails/<requestID>', methods=['GET'])
@login_required
def requestDetails(requestID):
    with DB(**app.config['ARVIXE_LENDA']) as db:
        requestWithDetails = db.call_proc('Ryan.FD_Lend_Details_Request_per_ID', requestid=requestID)[0]
        requestWithDetails['Offers'] = db.call_proc('Ryan.FD_List_Offers_per_Request_ID', requestid=requestID)

    context = dict(
        requestWithDetails=requestWithDetails,
        accountid=g.user.get_id(),
        displayname=g.user.displayname,
        current_page='requestDetails'
    )

    return render_template('requestDetails.html', **context)


@app.route('/contact', methods=['POST'])
def contact_us():
    name = request.json['name']
    phone = request.json['phone']
    email = request.json['email']
    message = request.json['message']
    subject = 'Message from {}'.format(name)

    payload = dict(
        name=name,
        email=email,
        phone=phone,
        message=message
    )

    send_email(subject, email, app.config['ADMINS'], message, payload)

    return jsonify(success=True)


def send_email(subject, sender, recipients, message, payload={}):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = render_template('contact_email.txt', sender=payload)
    msg.html = render_template('contact_email.html', sender=payload)
    mail.send(msg)


def authenticate_user(username, password):
    with DB(**app.config['ARVIXE_LENDA']) as db:
        result = db.call_proc('Ryan.FD_Lend_Login', emailaddress=username)[0]

    pw_hash = result['password']

    if bcrypt.check_password_hash(pw_hash, password):
        user = User(result['accountid'])
        login_user(user)
        return True

    return False
