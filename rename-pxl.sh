#!/bin/bash
for f in "$@"; do
    mv -v -- "$f" "${f//PXL_/}"
done
