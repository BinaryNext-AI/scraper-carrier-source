#!/usr/bin/env bash
# Exit on any error
set -e

# Update package lists
apt-get update

# Install Chrome dependencies
apt-get install -y wget gnupg

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update package lists again
apt-get update

# Install Google Chrome
apt-get install -y google-chrome-stable

# Verify Chrome installation
google-chrome --version

echo "Chrome installation completed successfully"
