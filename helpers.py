import threading
import settings
import requests
import hashlib
import MySQLdb
import base64
import Queue
import time
import ldap
import ldap.filter
import re

from requests.auth import HTTPBasicAuth

class DoorOperation(threading.Thread):

    def __init__(self):
        self.queue = Queue.Queue(10)
        super(DoorOperation, self).__init__()

        self.setDaemon(True)
        self.start()

    def run(self):

        while True:
            if self.queue.get():
                self.__unlock()
            else:
                self.__lock()

            self.queue.task_done()

    def open_door(self):
        self.queue.put(True)

    def close_door(self):
        self.queue.put(False)

    def __unlock(self):

        functions = settings.relais['functions']

        # set door summer
        if 'buzzer' in functions:
            self.__switch_relais(functions['buzzer'], True)

        # open the door
        self.__switch_relais(functions['open'], True)
        time.sleep(0.1)
        self.__switch_relais(functions['open'], False)

        # stop door buzzer
        if 'buzzer' in functions:
            time.sleep(3)
            self.__switch_relais(functions['buzzer'], False)

    def __lock(self):

        functions = settings.relais['functions']

        # close the door
        self.__switch_relais(functions['close'], True)
        time.sleep(0.1)
        self.__switch_relais(functions['close'], False)

    def __switch_relais(self, relais, on):

        url = settings.relais['url'] + '/relais/' + str(relais)
        basic_auth = HTTPBasicAuth(settings.relais['user'], settings.relais['passwd'])

        if on:
            response = requests.post(url, auth=basic_auth)
        else:
            response = requests.delete(url, auth=basic_auth)


def log_action(opentype, uid):
    db = MySQLdb.connect(host=settings.mysql['host'], user=settings.mysql['user'],
                         passwd=settings.mysql['passwd'], db=settings.mysql['db'])

    db_cursor = db.cursor()
    db_cursor.execute("INSERT INTO " + settings.mysql['table'] + " (type, uid, created) VALUES (%s, %s, NOW())", (opentype, uid))

    db.commit()


def get_ldap_connection():

    if 'CAFile' in settings.ldap:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.ldap['CAFile'])

    ldap_con = ldap.initialize(settings.ldap['uri'])
    ldap_con.protocol_version = ldap.VERSION3
    ldap_con.bind(settings.ldap['dn'], settings.ldap['password'])

    return ldap_con

def get_members():
    con = get_ldap_connection()
    entries = con.search_s('ou=member,dc=backspace', ldap.SCOPE_SUBTREE, '(&(objectClass=backspaceMember)(serviceEnabled=door))', ['uid'])

    users = []
    for entry in entries:
        data = entry[1]
        users.append(data['uid'][0])

    return sorted(users)

def verify_password(uid, password):

    con = get_ldap_connection()
    uid = ldap.filter.escape_filter_chars(uid)

    entries = con.search_s('ou=member,dc=backspace', ldap.SCOPE_SUBTREE, '(&(objectClass=backspaceMember)(serviceEnabled=door)(uid=%s))' % (uid,), ['doorPassword'])

    if len(entries) > 1 or len(entries) == 0:
        return False

    entry = entries[0][1]

    m = re.search(r'^{SSHA512}(.*)$', entry['doorPassword'][0])
    if not m:
        return False

    decoded = base64.b64decode(m.group(1))

    sha512 = decoded[:64] # hash is 64 byte (512 bit) long
    salt = decoded[64:] # everything else is salt

    mypass = hashlib.sha512(password + salt).digest()

    return (sha512 == mypass)

