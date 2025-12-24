#!/bin/bash

# Encrypted Backup Decryption Script
# Usage: ./backup_decrypt.sh <encrypted_file> <encrypted_key> <private_key>

set -euo pipefail  # Exit on error, undefined vars, pipe failures
umask 077  # Restrict permissions on created files

# Check arguments
if [ $# -ne 3 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: $0 <encrypted_file> <encrypted_key> <private_key>"
    echo ""
    echo "Example:"
    echo "  $0 backup_20231215_143022.tar.gz.enc backup_20231215_143022.tar.gz.key.enc priv.key"
    exit 1
fi

ENCRYPTED_FILE="$1"
ENCRYPTED_KEY="$2"
PRIVATE_KEY="$3"

# Validate inputs
if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo "Error: Encrypted file '$ENCRYPTED_FILE' not found"
    exit 1
fi

if [ ! -f "$ENCRYPTED_KEY" ]; then
    echo "Error: Encrypted key file '$ENCRYPTED_KEY' not found"
    exit 1
fi

if [ ! -f "$PRIVATE_KEY" ]; then
    echo "Error: Private key file '$PRIVATE_KEY' not found"
    exit 1
fi

# Remove .enc extension to get original tarball name
TARBALL="${ENCRYPTED_FILE%.enc}"

echo "Decrypting AES key with RSA private key..."
# Decrypt the AES key using the RSA private key
AES_KEY_FILE=$(mktemp)
trap 'shred -u "$AES_KEY_FILE" 2>/dev/null || rm -f "$AES_KEY_FILE"' EXIT
openssl pkeyutl -decrypt -inkey "$PRIVATE_KEY" -in "$ENCRYPTED_KEY" -out "$AES_KEY_FILE"

echo "Decrypting tarball with AES-256-CBC..."
# Decrypt the tarball using the decrypted AES key
openssl enc -d -aes-256-cbc -pbkdf2 -in "$ENCRYPTED_FILE" -out "$TARBALL" -pass file:"$AES_KEY_FILE"

# Cleanup handled by trap EXIT

echo ""
echo "Decryption complete!"
echo "Decrypted tarball: $TARBALL"
echo ""
echo "To extract the backup, run:"
echo "  tar -xzf $TARBALL"
