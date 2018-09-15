from flask import Flask, render_template, jsonify, request
import settings
import helpers

app = Flask(__name__)

door_operator = helpers.DoorOperation()

@app.route('/')
def page_main():
    users = helpers.get_allowed_users()
    return render_template('door.html', users=users)

@app.route('/verify', methods=["POST"])
def ajax_verify():

    if not 'password' in request.form or not 'type' in request.form:
        return "password or type field missing", 200

    uid = request.form.get('uid')
    password = request.form.get('password')
    opentype = request.form.get('type')
    notice   = ''

    if helpers.verify_password(uid, password):

        helpers.log_action(opentype, uid)

        if opentype == 'Buzzer':
            notice = settings.notice['buzzer']
            door_operator.open_door()
        elif opentype == 'Open':
            notice = settings.notice['open']
            door_operator.open_door()
        elif opentype == 'Close':
            notice = settings.notice['close']
            door_operator.close_door()

        return jsonify(response=True, notice=notice)

    return jsonify(response=False)

if __name__ == '__main__':
    app.debug = True
    app.run(host=settings.listen['address'], port=settings.listen['port'])
