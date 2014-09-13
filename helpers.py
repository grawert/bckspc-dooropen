import threading
import settings
import requests
import hashlib
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
        self.__switch_relais(functions['buzzer'], True)

        # open the door
        self.__switch_relais(functions['open'], True)
        time.sleep(0.1)
        self.__switch_relais(functions['open'], False)

        # stop door buzzer
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


def get_members(con):
    entries = con.search_s('ou=member,dc=backspace', ldap.SCOPE_SUBTREE, '(&(objectClass=backspaceMember)(serviceEnabled=door))', ['uid'])

    users = []
    for entry in entries:
        data = entry[1]
        users.append(data['uid'][0])

    return sorted(users)

def verify_password(con, uid, password):

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

