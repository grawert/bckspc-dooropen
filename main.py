from flask import Flask, render_template, jsonify, request

import datetime
import settings
import MySQLdb
import helpers
import ldap

app = Flask(__name__)

ldap_con = ldap.initialize(settings.ldap['uri'])
ldap_con.protocol_version = ldap.VERSION3
ldap_con.bind(settings.ldap['dn'], settings.ldap['password'])

#db = MySQLdb.connect(**settings.mysql)
#db_cursor = db.cursor()

door_operator = helpers.DoorOperation()
door_operator.start()

@app.route('/')
def page_main():
    users = helpers.get_members(ldap_con)
    return render_template('door.html', users=users)

@app.route('/verify', methods=["POST"])
def ajax_verify():

    if not 'password' in request.form or not 'type' in request.form:
        return "password or type field missing", 200

    uid = request.form.get('uid')
    password = request.form.get('password')
    opentype = request.form.get('type')

    if helpers.verify_password(ldap_con, uid, password):

#        if settings.logging:
#            db_cursor.execute("INSERT INTO doorlog (type, uid, created) VALUES (:type, :uid, NOW())", {'type': opentype, 'uid': userid })
#            db.session.commit()

        if opentype == 'Open':
            door_operator.open_door()
        elif opentype == 'Close':
            door_operator.close_door()

        return jsonify(response=True)

    return jsonify(response=False)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

