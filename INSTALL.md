# Door unlocking via web interface using LDAP authentication

## Install software requirements

    sudo apt-get install build-essential openssl libsasl2-dev python-dev libldap2-dev libssl-dev python-pip
    pip install -r requirements.txt

## Create self signed certificate for Nginx TLS connections

    sudo mkdir /etc/nginx/pki
    sudo openssl genrsa -out /etc/nginx/pki/server.key.pem
    sudo openssl req -new -key /etc/nginx/pki/server.key.pem -out /etc/nginx/pki/server.csr.pem
    sudo openssl x509 -req -days 365 -in /etc/nginx/pki/server.csr.pem -signkey /etc/nginx/pki/server.key.pem -out /etc/nginx/pki/server.cert.pem

## Install OpenLDAP Server

    sudo apt-get install ldap-server ldap-client ldap-utils

### Setup TLS

```
sudo ldapmodify -Y EXTERNAL -H ldapi:/// <<EOF

dn: cn=config
changetype: modify
add: olcTLSCACertificateFile
olcTLSCACertificateFile: /etc/ldap/pki/ca.cert.pem
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
```
sudo systemctl restart slapd
```

### Create new database in OpenLDAP

```
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

```
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: dynlist

EOF
```

```
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/dyngroup.ldif
```

```
sudo ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: olcOverlay=dynlist,olcDatabase={2}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcDynamicList
olcOverlay: dynlist

EOF
```

### Create containers and users

```
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
