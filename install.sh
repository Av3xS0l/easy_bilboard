#!/bin/bash
# Script to install dependencies on Debian/Ubuntu or Arch Linux based systems

# Python and Multimedia packages for Debian/Ubuntu (apt)
APT_PACKAGES="python3-pip python3-venv libqt5multimedia5-plugins libpulse-mainloop-glib0 gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-base gstreamer1.0-libav gstreamer1.0-tools imagemagick"

# Python and Multimedia packages for Arch Linux (pacman)
PACMAN_PACKAGES="python qt5-multimedia libpulse gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav imagemagick"

if command -v apt &> /dev/null; then
    # Debian based system
    sudo apt update -y
    sudo apt install ${APT_PACKAGES} -y
    PYTHON_CMD="python3"
elif command -v pacman &> /dev/null; then
    # Arch linux based system
    sudo pacman -Syu --noconfirm # Full system update recommended on Arch
    sudo pacman -S ${PACMAN_PACKAGES} --noconfirm
    PYTHON_CMD="python"
else
    echo "Error: Neither apt nor pacman found. Cannot install system dependencies."
    exit 1
fi

${PYTHON_CMD} -m venv EASY_BILBOARD
source ./EASY_BILBOARD/bin/activate
pip install -r requirements.pip

# ==========================================
# Automated Counter & Cron Job Configuration
# ==========================================

# Use the current working directory to guarantee an absolute path for cron
SCRIPT_DIR=$(pwd)
COUNTER_SCRIPT="$SCRIPT_DIR/counter_init.sh"

if [ -f "$COUNTER_SCRIPT" ]; then
    # Make the script executable
    chmod +x "$COUNTER_SCRIPT"
    
    # Check if the cron job already exists to avoid duplicates
    if ! crontab -l 2>/dev/null | grep -q "$COUNTER_SCRIPT"; then
        # Append the new cron job silently
        (crontab -l 2>/dev/null; echo "0 0 * * * $COUNTER_SCRIPT") | crontab -
        echo "Successfully added $COUNTER_SCRIPT to crontab."
    else
        echo "Cron job for $COUNTER_SCRIPT is already configured. Skipping."
    fi
else
    echo "Warning: $COUNTER_SCRIPT not found in $SCRIPT_DIR. Cron setup skipped."
fi