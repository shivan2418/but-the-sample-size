#!/bin/sh
# How GitHub Pages answers Range requests with and without a browser-like Accept-Encoding.
F=https://palermohub.github.io/PRG2004/particelle/prg.pmtiles     # a third-party .pmtiles on GitHub Pages
for AE in identity 'gzip, deflate, br, zstd'; do
  echo "== Accept-Encoding: $AE"
  curl -s -o /dev/null -D - -H 'Range: bytes=0-16383' -H "Accept-Encoding: $AE" $F | grep -iE '^(HTTP|content-type|content-range|content-encoding)'
  curl -s -H 'Range: bytes=0-6' -H "Accept-Encoding: $AE" $F | xxd | head -1
done
G=https://shivan2418.github.io/zonemapdb-demo-addresses/blockdb/blocks/24/247aee7e9972aed9.ndjson.gz   # a .gz file
echo "== .gz with gzip accepted"; curl -s -o /dev/null -D - -H 'Range: bytes=100-199' -H 'Accept-Encoding: gzip, br' $G | grep -iE '^(HTTP|content-type|content-range|content-encoding)'
J=https://shivan2418.github.io/zonemapdb-demo-addresses/assets/index-CscWDhTU.js
echo "== brotli only"; curl -s -o /dev/null -D - -H 'Accept-Encoding: br, zstd' $J | grep -iE '^(HTTP|content-length|content-encoding)'
