#!/bin/sh

# This script is used to create the Linux installer for the application.

rm -rf dist
rm -rf build

pyinstaller massdash.spec -y

mkdir -p dist/massdash_linux/usr/local/bin
mv dist/massdash dist/massdash_linux/usr/local/bin/massdash
mkdir dist/massdash_linux/DEBIAN
mkdir -p dist/massdash_linux/usr/share/applications
mkdir -p dist/massdash_linux/usr/share/icons
cp ../linux/massdash.desktop dist/massdash_linux/usr/share/applications/massdash.desktop
cp ../../massdash/assets/img/MassDash_Logo.ico dist/massdash_linux/usr/share/icons/massdash.ico
cp ../linux/control dist/massdash_linux/DEBIAN/control
dpkg-deb --build --root-owner-group dist/massdash_linux