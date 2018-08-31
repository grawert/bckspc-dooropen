# Door unlocking via web interface using LDAP authentication

## Install software requirements for pip

    sudo apt-get install build-essential libsasl2-dev python-dev libldap2-dev libssl-dev python-pip
    pip install flask

## Install OpenLDAP Server

    sudo apt-get install ldap-server ldap-client ldap-utils

### Create new database in LDAP

```
ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

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

### Add dynamic groups to LDAP schema

```
ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: dynlist

EOF
```

```
ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/dyngroup.ldif
´´´

´´´
ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

dn: olcOverlay=dynlist,olcDatabase={2}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcDynamicList
olcOverlay: dynlist

EOF
```

### Create containers and users

```
ldapadd -Y EXTERNAL -H ldapi:/// <<EOF

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
