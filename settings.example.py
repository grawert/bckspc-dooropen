logging = True

relais = {
    'url': 'https://webrelais.core.bckspc.de',
    'user': 'foobar',
    'passwd': 'bar',
    'functions': {
        'open': 3,
        'close': 4,
        'buzzer': 5
    }
}

relais_projektraum = {
    'url': 'https://webrelais.projektraum.core.bckspc.de',
    'user': 'foobar',
    'passwd': 'bar',
    'functions': {
        'open': 3,
        'close': 4,
    }
}

mysql = {
    'host': 'mysql.at.home',
    'user': 'dbuser',
    'passwd': 'dbpass',
    'db': 'dbdbdb'
}

ldap = {
    'uri': 'ldaps://ldap.at.home',
    'port': 636,
    'dn': 'cn=reader,ou=ldapuser,dc=yourDC',
    'password': 'ldappass'
}

