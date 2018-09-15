import os
import re
import pytz
from datetime import date, datetime
import icalendar
import threading
import settings
import requests
import syslog
import Queue
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

        # set door buzzer
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

def get_allowed_users():
    return sorted(get_allowed_users_from_ical())

def verify_password(uid, password):
    uid = ldap.filter.escape_filter_chars(uid)
    basedn = settings.ldap['users_container']
    user_id = settings.ldap['user_id_attribute']
    userdn = '%s=%s,%s' % (user_id, uid, basedn)

    verified = False

    try:
        if uid not in get_allowed_users():
            raise Exception('User not allowed to authenticate')

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

def event_is_ongoing(start, end):
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)

    if not isinstance(start, datetime):
        start = datetime.combine(start, now.time())
        start = start.replace(tzinfo=pytz.utc)
    if not isinstance(end, datetime):
        end = datetime.combine(end, now.time())
        end = end.replace(tzinfo=pytz.utc)

    return start <= now and end > now

def extract_uid(mail_to):
    return re.match('mailto:(.+)@', mail_to).group(1)

def get_allowed_users_from_ical():
    f_ical = open(settings.ical['file_location'], "r")
    cal = icalendar.Calendar.from_ical(f_ical.read())

    allowed_users = []
    for event in cal.walk('vevent'):
        if event['STATUS'] != 'CONFIRMED':
          continue

        # check if attendees are defined
        try:
            attendees = event.decoded('ATTENDEE')
        except KeyError:
           continue

        start = event.decoded('DTSTART')
        end   = event.decoded('DTEND')

        if event_is_ongoing(start, end):
            for attendee in attendees:
                allowed_users.append(extract_uid(attendee))

    return set(allowed_users)

def get_allowed_users_from_ldap():
    con = get_ldap_connection()
    basedn = settings.ldap['members_container']
    search_filter = 'objectClass=%s' % settings.ldap['members_container_class']
    user_id = settings.ldap['user_id_attribute']
    entries = con.search_s(basedn, ldap.SCOPE_SUBTREE, search_filter, [user_id])

    allowed_users = []
    for entry in entries:
        data = entry[1]
        allowed_users = data[user_id]

    return set(allowed_users)
