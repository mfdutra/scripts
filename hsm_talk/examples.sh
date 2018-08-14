#!/bin/bash

echo "Do not run this as a script, as it's destructive"
exit 1

######################################################################

# Exhaust failures, so reset is possible
yubico-piv-tool -averify-pin -P000000
yubico-piv-tool -averify-pin -P000000
yubico-piv-tool -averify-pin -P000000
yubico-piv-tool -achange-puk -P000000 -N6756789
yubico-piv-tool -achange-puk -P000000 -N6756789
yubico-piv-tool -achange-puk -P000000 -N6756789
yubico-piv-tool -areset

# Initialize yubikey
yubico-piv-tool -a set-chuid  # sets a unique identifier
yubico-piv-tool -a change-pin -P 123456  # 123456 is the default PIN
yubico-piv-tool -a change-puk -P 12345678  # 12345678 is the default PUK
MGMT=$(head -c 24 /dev/urandom | hexdump -v -e '/1 "%02X"')
echo "Management key: $MGMT"
yubico-piv-tool -a set-mgm-key -n "$MGMT"

# Generating key and self certificate
yubico-piv-tool -a generate -s 9c -k -o pubkey.pem
cat pubkey.pem
yubico-piv-tool -a verify-pin -a selfsign-certificate -s 9c \
  -S '/CN=Marlon Dutra/' --valid-days=10957 \
  -i pubkey.pem -o cert.pem
openssl x509 -text -noout -in cert.pem
yubico-piv-tool -a import-certificate -s 9c -k -i cert.pem

# Testing encryption
echo "super secret message" > msg
openssl rsautl -encrypt -inkey pubkey.pem -pubin \
  -in msg -out msg.crypt
pkcs11-tool --decrypt -i msg.crypt -m RSA-PKCS

# Testing signing
pkcs11-tool -s -m SHA256-RSA-PKCS -i msg -o signature
openssl dgst -sha256 -verify pubkey.pem -signature signature msg

# Retrieving pubkey for OpenSSH
yubico-piv-tool -a read-certificate -s 9c -K SSH
yubico-piv-tool -a read-certificate -s 9c -K SSH > ~/.ssh/authorized_keys
ssh -o PKCS11Provider=/usr/local/lib/opensc-pkcs11.so \
  root@your_server_hostname

# Creating OpenSSH certificate
ssh-keygen \
  -s cert.pem \
  -D /usr/local/lib/opensc-pkcs11.so \
  -I user \
  -n user \
  -V +52w \
  -z 12345 \
  user.pub

# OpenSSL config
cat > openssl.conf << EOF
openssl_conf = openssl_init

[openssl_init]
engines = engine_section

[engine_section]
pkcs11 = pkcs11_section

[pkcs11_section]
engine_id = pkcs11
dynamic_path = /engines/pkcs11.dylib
MODULE_PATH = /usr/local/lib/opensc-pkcs11.so
init = 0
EOF

# Testing OpenSSL
alias openssl='/usr/local/Cellar/openssl/1.0.2o_2/bin/openssl'
OPENSSL_CONF=openssl.conf openssl dgst \
  -engine pkcs11 -keyform engine -sign slot_0 \
  -sha256 -out signature msg

openssl dgst -sha256 -verify pubkey.pem \
  -signature signature msg

# MacOS environment
brew install openssl

cd libp-directory/
OPENSSL_CFLAGS='-I/usr/local/Cellar/openssl/1.0.2o_2/include' OPENSSL_LIBS='-L/usr/local/Cellar/openssl/1.0.2o_2/lib/ -lcrypto -lssl' ./configure
make
sudo make install
