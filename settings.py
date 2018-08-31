logging = True
logging_ident = "opensesame"

relais = {
    'url': 'https://localhost',
    'user': 'foobar',
    'passwd': 'bar',
    'functions': {
        'open': 3,
        'close': 4,
        'buzzer': 5
    }
}

ldap = {
    'uri': 'ldaps://localhost',
    'port': 636,
    'dn': 'cn=reader,ou=users,dc=b1-systems,dc=de',
    'password': 'secret',
    'dyngroup': 'cn=dooropen,ou=groups,dc=b1-systems,dc=de',
    'users_container': 'ou=users,dc=b1-systems,dc=de',
    'user_id': 'uid',
}

