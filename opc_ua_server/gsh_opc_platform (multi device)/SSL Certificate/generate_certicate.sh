
: '
Generate your own x509v3 Certificate
Step 1: Change ssl.conf (subjectAltname, country, organizationName, ...)
Step 2: openssl genrsa -out key.pem 2048
Step 3: openssl req -x509 -days 365 -new -out certificate.pem -key key.pem -config ssl.conf
this way is proved with Siemens OPC UA Client/Server!
ssl.conf:
[ req ]
default_bits = 2048
default_md = sha256
distinguished_name = subject
req_extensions = req_ext
x509_extensions = req_ext
string_mask = utf8only
prompt = no
[ req_ext ]
basicConstraints = CA:FALSE
nsCertType = client, server
keyUsage = nonRepudiation, digitalSignature, keyEncipherment, dataEncipherment, keyCertSign
extendedKeyUsage= serverAuth, clientAuth
nsComment = "OpenSSL Generated Certificat"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
subjectAltName = URI:urn:opcua:python:server,IP: 127.0.0.1
[ subject ]
countryName = MY
stateOrProvinceName = PNG
localityName = BY
organizationName = GSHPrecision
commonName = PythonOpcUaServer
'
openssl genrsa -out gsh_private_key.pem 2048
openssl req -x509 -days 365 -new -out gsh_private_certificate.pem -key gsh_private_key.pem -config ssl.conf
openssl req -x509 -newkey rsa:4096 -sha256 -keyout gsh_private_key.pem -out gsh_private_certificate.pem -days 3650 -nodes -addext "subjectAltName = URI:urn:opcua:python:server,IP: 127.0.0.1"
openssl x509 -outform der -in gsh_private_certificate.pem -out gsh_private_certificate.der