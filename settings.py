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
    'dn': 'uid=reader,ou=users,dc=b1-systems,dc=de',
    'password': 'secret',
    'members_container': 'cn=dooropen,ou=groups,dc=b1-systems,dc=de',
    'members_container_class': 'groupOfURLs',
    'users_container': 'ou=users,dc=b1-systems,dc=de',
    'user_id_attribute': 'uid',
}

