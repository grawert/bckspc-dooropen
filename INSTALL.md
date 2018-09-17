# Door unlocking via web interface using LDAP authentication

## Install software requirements

```shell
sudo apt-get install build-essential openssl libsasl2-dev python-dev libldap2-dev libssl-dev python-pip ldap-server ldap-client ldap-utils
pip install -r requirements.txt
```

## Create self signed certificate for Nginx and OpenLDAP

```shell
SSL_DIR=/etc/ssl
SSL_PRIVATE=$SSL_DIR/private
SSL_CERTSDIR=$SSL_DIR/certs

PKI_NGINX=/etc/nginx/pki
PKI_LDAP=/etc/ldap/pki

NGINX_HOSTNAME=$HOSTNAME
LDAP_HOSTNAME=$HOSTNAME
LDAP_UID="openldap"

sudo openssl genrsa -out $SSL_PRIVATE/ca.key.pem
sudo openssl req -x509 -new -nodes -key $SSL_PRIVATE/ca.key.pem -days 1024 -out $SSL_CERTSDIR/ca.cert.pem -extensions v3_ca -subj "/C=DE/O=B1 Systems GmbH/L=Vohbburg/CN=CA"

sudo mkdir -p $PKI_NGINX
sudo openssl genrsa -out $PKI_NGINX/server.key.pem
sudo openssl req -new -key $PKI_NGINX/server.key.pem -out $PKI_NGINX/server.csr.pem -subj "/C=DE/O=B1 Systems GmbH/L=Vohbburg/CN=$NGINX_HOSTNAME"
sudo openssl x509 -req -days 365 -extensions server -in $PKI_NGINX/server.csr.pem -out $PKI_NGINX/server.cert.pem -CAcreateserial -CAserial $SSL_PRIVATE/CA.srl -CA $SSL_CERTSDIR/ca.cert.pem -CAkey $SSL_PRIVATE/ca.key.pem

sudo mkdir -p $PKI_LDAP
sudo openssl genrsa -out $PKI_LDAP/server.key.pem && sudo chown ${LDAP_UID}: $PKI_LDAP/server.key.pem
sudo openssl req -new -key $PKI_LDAP/server.key.pem -out $PKI_LDAP/server.csr.pem -subj "/C=DE/O=B1 Systems GmbH/L=Vohbburg/CN=$LDAP_HOSTNAME"
sudo openssl x509 -req -days 365 -extensions server -in $PKI_LDAP/server.csr.pem -out $PKI_LDAP/server.cert.pem -CAcreateserial -CAserial $SSL_PRIVATE/CA.srl -CA $SSL_CERTSDIR/ca.cert.pem -CAkey $SSL_PRIVATE/ca.key.pem
```

### Setup TLS

```shell
sudo ldapmodify -Y EXTERNAL -H ldapi:/// <<EOF

dn: cn=config
changetype: modify
add: olcTLSCACertificateFile
olcTLSCACertificateFile: /etc/ssl/certs/ca.cert.pem
-
add: olcTLSCertificateFile
olcTLSCertificateFile: /etc/ldap/pki/server.cert.pem
-
add: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/ldap/pki/server.key.pem

EOF
```

#### Enable LDAPS

/etc/default/slapd:
```
SLAPD_SERVICES="ldap:/// ldapi:/// ldaps:///"
```

#### Restart OpenLDAP server

```shell
sudo systemctl restart slapd
```

### Create new database in OpenLDAP

```shell
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: olcDatabase=mdb,cn=config
objectClass: olcMdbConfig
olcDatabase: mdb
olcSuffix: dc=b1-systems,dc=de
olcDbDirectory: /var/lib/ldap
olcRootDN: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
olcDbIndex: objectClass eq
olcDbIndex: cn,uid eq
olcDbIndex: uidNumber,gidNumber eq
olcDbIndex: member,memberUid eq
olcAccess: to attrs=userPassword by self write by anonymous auth by * none
olcAccess: to attrs=shadowLastChange by self write by * read
olcAccess: to * by * read

EOF
```

### Add dynamic groups to OpenLDAP schema

```shell
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: dynlist

EOF
```

```shell
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/dyngroup.ldif
```

```shell
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: olcOverlay=dynlist,olcDatabase={2}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcDynamicList
olcOverlay: dynlist

EOF
```

### Create containers and users

```shell
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: dc=b1-systems,dc=de
dc: b1-systems
objectClass: domain
objectClass: top

dn: ou=users,dc=b1-systems,dc=de
ou: users
objectClass: organizationalUnit
objectClass: top

dn: ou=groups,dc=b1-systems,dc=de
ou: groups
objectClass: organizationalUnit
objectClass: top

dn: cn=dooropen,ou=groups,dc=b1-systems,dc=de
objectclass: groupOfURLs
cn: dooropen
description: People allowed to open the door
memberURL: ldap:///ou=users,dc=b1-systems,dc=de?uid?one?(uid=*)

dn: uid=alice,ou=users,dc=b1-systems,dc=de
objectclass: person
objectClass: inetOrgPerson
objectclass: organizationalperson
uid: alice
cn: Alice
sn: Alice
userPassword: secret

dn: uid=bob,ou=users,dc=b1-systems,dc=de
objectclass: person
objectClass: inetOrgPerson
objectclass: organizationalperson
uid: bob
cn: Bob
sn: Bob
userPassword: secret

dn: uid=reader,ou=users,dc=b1-systems,dc=de
objectclass: person
objectClass: inetOrgPerson
objectclass: organizationalperson
uid: reader
cn: reader
sn: reader
userPassword: secret

EOF
```
