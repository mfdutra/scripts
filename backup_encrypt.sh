#!/bin/bash

# Encrypted Backup Script
# Usage: ./backup_encrypt.sh <directory1> [directory2] [directory3] ...

set -euo pipefail  # Exit on error, undefined vars, pipe failures
umask 077  # Restrict permissions on created files

# Check if at least one directory argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directories specified"
    echo "Usage: $0 <directory1> [directory2] [directory3] ..."
    exit 1
fi

# Set up public key file path from environment variable or default
PUB_KEY_FILE="${PUB_KEY:-pub.key}"

# Check if public key file exists
if [ ! -f "$PUB_KEY_FILE" ]; then
    echo "Error: Public key file '$PUB_KEY_FILE' not found"
    exit 1
fi

# Validate that all arguments are directories
for dir in "$@"; do
    if [ ! -d "$dir" ]; then
        echo "Error: '$dir' is not a valid directory"
        exit 1
    fi
done

# Generate timestamp for backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TARBALL="backup_${TIMESTAMP}.tar.gz"
ENCRYPTED_FILE="${TARBALL}.enc"
ENCRYPTED_KEY="${TARBALL}.key.enc"

echo "Creating tarball: $TARBALL"
tar -czf "$TARBALL" "$@"

echo "Generating random AES-256 key..."
# Generate a random 256-bit (32 byte) key for AES-256
AES_KEY_FILE=$(mktemp)
trap 'shred -u "$AES_KEY_FILE" 2>/dev/null || rm -f "$AES_KEY_FILE"' EXIT
openssl rand -hex 32 > "$AES_KEY_FILE"

echo "Encrypting tarball with AES-256-CBC..."
# Encrypt the tarball with AES-256-CBC using the random key
openssl enc -aes-256-cbc -salt -pbkdf2 -in "$TARBALL" -out "$ENCRYPTED_FILE" -pass file:"$AES_KEY_FILE"

echo "Encrypting AES key with RSA public key..."
# Encrypt the AES key with the RSA public key
openssl pkeyutl -encrypt -pubin -inkey "$PUB_KEY_FILE" -in "$AES_KEY_FILE" -out "$ENCRYPTED_KEY"

# Cleanup handled by trap EXIT

echo "Deleting original tarball..."
rm -f "$TARBALL"

echo ""
echo "Backup complete!"
echo "Encrypted backup: $ENCRYPTED_FILE"
echo "Encrypted key: $ENCRYPTED_KEY"
echo ""
echo "To decrypt, you'll need:"
echo "  1. The encrypted file: $ENCRYPTED_FILE"
echo "  2. The encrypted key: $ENCRYPTED_KEY"
echo "  3. The RSA private key corresponding to pub.key"
