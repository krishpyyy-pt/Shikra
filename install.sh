#!/bin/bash

echo "========================================"
echo "      Installing Shikra Gateway         "
echo "========================================"

# 1. Get the absolute directory where the user downloaded the folder
INSTALL_DIR=$(pwd)

# 2. Make the master console executable
echo "[*] Setting execution permissions..."
chmod +x "$INSTALL_DIR/shikra.py"

# 3. Create the global symlink (asking for sudo if needed)
echo "[*] Creating global system command 'shikra'..."
# The -f flag forces an overwrite if they are updating an older version
sudo ln -sf "$INSTALL_DIR/shikra.py" /usr/local/bin/shikra

echo "========================================"
echo "[✔] Installation Complete!"
echo "[✔] You can now type 'shikra' anywhere in your terminal."
echo "========================================"
