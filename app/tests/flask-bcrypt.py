# coding:utf-8
import unittest
import sys
import os

import flask
from flask_bcrypt import (Bcrypt,
                          check_password_hash,
                          generate_password_hash)


sys.path.append(os.path.dirname(os.getcwd()))

from app.dbhelper import DB


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config.from_object('config')
        self.bcrypt = Bcrypt(self.app)


    def test_create_user_then_check_hash(self):
        userDisplayName = 'testName1'
        userEmail = 'testEmail1'
        userPassword = 'secretPassword1'
        pw_hash = generate_password_hash(userPassword)

        with DB(**self.app.config['ARVIXE_LENDA']) as db:
            result = db.call_proc('Ryan.FD_Lend_Create_users',
                                  emailaddress=userEmail,
                                  password=pw_hash,
                                  displayname=userDisplayName)[0]

        with DB(**self.app.config['ARVIXE_LENDA']) as db:
            result = db.call_proc('Ryan.FD_Lend_Login',
                                  emailaddress=userEmail)[0]

        pw_hash = result['password']

        self.assertTrue(check_password_hash(pw_hash, userPassword))


    @unittest.skip("demonstrating skipping")
    def test_create_multi_users(self):
        for x in range(10):
            userDisplayName = 'test{}'.format(x)
            userEmail = userDisplayName
            userPassword = userDisplayName
            pw_hash = generate_password_hash(userPassword)

            with DB(**self.app.config['ARVIXE_LENDA']) as db:
                result = db.call_proc('Ryan.FD_Lend_Create_users',
                                  emailaddress=userEmail,
                                  password=pw_hash,
                                  displayname=userDisplayName)[0]

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
