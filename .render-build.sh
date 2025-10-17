#!/usr/bin/env bash
# Install Chrome & Chromedriver in Render environment

set -euxo pipefail

# Install Chrome
apt-get update
apt-get install -y wget unzip xvfb
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver that matches Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+(\.[0-9]+)*" | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

echo "✅ Chrome and Chromedriver installed successfully"
