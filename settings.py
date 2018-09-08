logging = True
logging_ident = "opensesame"

listen = {
    'address': '0.0.0.0',
    'port': 80,
}

notice = {
    'buzzer': 'This is your door PIN: 1234',
}

pi_buzzer = {
    'url': 'https://localhost:5021/',
    'user': 'foo',
    'passwd': 'bar',
    'tls_verify': False,
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
