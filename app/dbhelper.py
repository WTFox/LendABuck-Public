# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import pymssql as sql
import _mssql as sql2


class DB(object):
    """ Context manager class to wrap the stored procedure calls.

    """

    def __init__(self, db_name=False, db_servername='', db_serveruser='', db_serverpass='', as_list=False,
                 as_json=False):
        """ Starts the context manager with access to a database.

        """
        self.db_servername = db_servername
        self.db_serveruser = db_serveruser
        self.db_serverpass = db_serverpass
        self.db_name = db_name
        self.as_list = as_list
        self.as_json = as_json
        if self.as_list:
            self.sqldriver = sql
        else:
            self.sqldriver = sql2

    def __enter__(self):
        """ Initializes the connection to the database.

        """
        self.conn = self.sqldriver.connect(
            server=self.db_servername,
            user=self.db_serveruser,
            password=self.db_serverpass,
            database=self.db_name
        )
        return self

    def __exit__(self, type, value, traceback):
        """ Closes the connection to the database when leaving the context

        """
        self.conn.close()
        return

    def call_proc(self, sp, **kwargs):
        """ Function that accepts a stored procedure name, and any number of
            variables.

            Returns:
                A list of rows from the output of the stored procedure.
                The items can be accessed via index or attribute.
                See example.py

        """

        args = []
        for k, v in kwargs.items():
            if type(v) == str:
                args.append("@{}='{}'".format(k, str(v).replace("'", "''").replace(';', '')))
            elif type(v) == bytes:
                args.append("@{}='{}'".format(k, str(v.decode())))
            else:
                args.append("@{}={}".format(k, v))

        query = "use {}; exec {} {}".format(self.db_name, sp, ', '.join(args))

        if self.as_list:
            cur = self.conn.cursor()
            cur.execute(query)
            output = cur.fetchall()

        elif self.as_json:
            self.conn.execute_query(query)
            output = [{k: v for k, v in item.items() if not isinstance(k, int)} for item in self.conn]

        else:
            self.conn.execute_query(query)
            output = [AttributeDict(row) for row in self.conn]

        return output


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
        return


if __name__ == "__main__":
    pass
