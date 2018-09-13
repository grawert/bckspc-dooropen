import threading
import settings
import requests
import syslog
import Queue
import time
import ldap
import ldap.filter

from requests.auth import HTTPBasicAuth

syslog.openlog(settings.logging_ident)

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

        functions = settings.pi_buzzer['functions']

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

        functions = settings.pi_buzzer['functions']

        # close the door
        self.__switch_relais(functions['close'], True)
        time.sleep(0.1)
        self.__switch_relais(functions['close'], False)

    def __switch_relais(self, relais, on):

        url = settings.pi_buzzer['url'] + '/' + str(relais)
        basic_auth = HTTPBasicAuth(settings.pi_buzzer['user'], settings.pi_buzzer['passwd'])

        tls_verify = settings.pi_buzzer['tls_verify']

        if on:
            response = requests.post(url, auth=basic_auth, verify=tls_verify)
        else:
            response = requests.delete(url, auth=basic_auth, verify=tls_verify)

        return response

def log_action(opentype, uid):
    if settings.logging == True:
        syslog.syslog(syslog.LOG_INFO, ("%s: %s" % (opentype, uid)))

def log_auth_fail(uid, reason):
    if settings.logging == True:
        msg = "Password verification failed: %s [%s]" % (uid, reason)
        syslog.syslog(syslog.LOG_WARNING, msg)

def get_ldap_connection():
    ldap_con = ldap.initialize(settings.ldap['uri'])
    ldap_con.protocol_version = ldap.VERSION3

    if 'CAFile' in settings.ldap:
        ldap_con.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
        ldap_con.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.ldap['CAFile'])
        ldap_con.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        ldap_con.start_tls_s()

    ldap_con.simple_bind_s(settings.ldap['dn'], settings.ldap['password'])

    return ldap_con

def get_members():
    con = get_ldap_connection()
    basedn = settings.ldap['members_container']
    search_filter = 'objectClass=%s' % settings.ldap['members_container_class']
    user_id = settings.ldap['user_id_attribute']
    entries = con.search_s(basedn, ldap.SCOPE_SUBTREE, search_filter, [user_id])

    users = []
    for entry in entries:
        data = entry[1]
        users = data[user_id]

    return sorted(users)

def verify_password(uid, password):
    uid = ldap.filter.escape_filter_chars(uid)
    basedn = settings.ldap['users_container']
    user_id = settings.ldap['user_id_attribute']
    userdn = '%s=%s,%s' % (user_id, uid, basedn)

    verified = False

    try:
        if uid not in get_members():
            raise Exception('User not found in members group')

        ldap_con = ldap.initialize(settings.ldap['uri'])
        ldap_con.protocol_version = ldap.VERSION3

        if 'CAFile' in settings.ldap:
            ldap_con.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
            ldap_con.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.ldap['CAFile'])
            ldap_con.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
            ldap_con.start_tls_s()

        ldap_con.bind_s(userdn, password)
        ldap_con.unbind()
    except Exception as error:
        log_auth_fail(uid, repr(error))
    else:
        verified = True

    return verified
