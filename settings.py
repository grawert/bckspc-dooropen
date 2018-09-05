logging = True
logging_ident = "opensesame"

listen = {
    'address': '0.0.0.0',
    'port': 80,
}

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
    'uri': 'ldap://localhost',
    'CAFile': '/etc/ldap/pki/ca.cert.pem',
    'dn': 'uid=reader,ou=users,dc=b1-systems,dc=de',
    'password': 'secret',
    'members_container': 'cn=dooropen,ou=groups,dc=b1-systems,dc=de',
    'members_container_class': 'groupOfURLs',
    'users_container': 'ou=users,dc=b1-systems,dc=de',
    'user_id_attribute': 'uid',
}
