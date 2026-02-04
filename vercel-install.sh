#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Installing Playwright browsers..."
export PLAYWRIGHT_BROWSERS_PATH=api/playwright_browsers
playwright install chromium
echo "Playwright installation complete."
