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

mysql = {
    'host': 'mysql.at.home',
    'user': 'dbuser',
    'passwd': 'dbpass',
    'db': 'dbdbdb',
    'table': 'dooropen'
}

ldap = {
    'uri': 'ldaps://ldap.at.home',
    'port': 636,
    'dn': 'cn=reader,ou=ldapuser,dc=yourDC',
    'password': 'ldappass'
}

