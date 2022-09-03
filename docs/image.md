# Use Pre-configured Image

If you've encountered problems like:
- `Type is not subscriptable` (which is a problem in typing grammar changed in around python 3.9)
- Any problem regarding `dbus-python` and bluetooth
- Cannot discover Switch, stuck on "Open pair menu" (which might be bluetooth problem in your VM software)
- Don't have a linux machine and know nothing about VM

You may download the flash-able image, and use [Balena Etcher](https://www.balena.io/etcher/) to flash it to a USB drive.

Reboot your computer, and get into Boot menu. This is usually done by pressing F12, F2, F10, or F8, or other keys, depending on your computer. You may need to check your computer's manual. Select your USB device to continue.

If your computer is bought recently with Windows already installed, you may encounter problems like "Secure boot forbids you from booting from USB". You may need to disable secure boot in your BIOS. (You can re-enable it after using the image, or your windows might not boot) You may need to check your computer's manual.

After booting, you should see a desktop environment with an icon "Konsole" on it. Get yourself internet connected (on the tray), and click it to open a terminal.

Run `install_splatplost` in the terminal, and after that everything should be ready. Continue to "Use" section on readme.md.