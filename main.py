from flask import Flask, render_template, jsonify, request

import helpers

app = Flask(__name__)

door_operator = helpers.DoorOperation()

@app.route('/')
def page_main():
    users = helpers.get_members()
    return render_template('door.html', users=users)

@app.route('/verify', methods=["POST"])
def ajax_verify():

    if not 'password' in request.form or not 'type' in request.form:
        return "password or type field missing", 200

    uid = request.form.get('uid')
    password = request.form.get('password')
    opentype = request.form.get('type')

    if helpers.verify_password(uid, password):

        helpers.log_action(opentype, uid)

        if opentype == 'Buzzer':
            door_operator.open_door()
        elif opentype == 'Open':
            door_operator.open_door()
        elif opentype == 'Close':
            door_operator.close_door()

        return jsonify(response=True)

    return jsonify(response=False)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

