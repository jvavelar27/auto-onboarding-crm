#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Installing Playwright browsers..."
export PLAYWRIGHT_BROWSERS_PATH=0
playwright install chromium
echo "Playwright installation complete."
