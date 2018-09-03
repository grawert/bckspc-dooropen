logging = True
logging_ident = "opensesame"

relais = {
    'url': 'http://localhost:5021/',
    'user': 'foo',
    'passwd': 'bar',
    'functions': {
        'open': 'door_open',
        'close': 'door_close',
        'buzzer': 'buzzer',
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
