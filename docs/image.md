# Use Pre-configured Image

If you've encountered problems like:
- `Type is not subscriptable` (which is a problem in typing grammar changed in around python 3.9)
- Any problem regarding `dbus-python` and bluetooth
- Cannot discover Switch, stuck on "Open pair menu" (which might be bluetooth problem in your VM software)
- Don't have a linux machine and know nothing about VM

You may download the flash-able image, and use [Balena Etcher](https://www.balena.io/etcher/) to flash it to a USB drive.

Download link (~1.8GB):
> mega.nz: https://mega.nz/file/CSBgnZpT#Us49WL1WAp0S_qww1qobISAWMDZ-COvCAOq14NHej3k
> 
> cloud.189.cn (need login): https://cloud.189.cn/web/share?code=NNviyqZjuUZn (access code: sfo9)
> 
> pan.baidu.com: https://pan.baidu.com/s/1182YwpjhaqwoLjEvUeM_9g?pwd=jxdb  (access code: jxdb)

(If you have better way sharing the image, please open an issue!)

Reboot your computer, and get into Boot menu. This is usually done by pressing F12, F2, F10, or F8, or other keys, depending on your computer. You may need to check your computer's manual. Select your USB device to continue.

If your computer is bought recently with Windows already installed, you may encounter problems like "Secure boot forbids you from booting from USB". You may need to disable secure boot in your BIOS. (You can re-enable it after using the image, or your windows might not boot) You may need to check your computer's manual.

After booting, you should see a desktop environment with an icon "Konsole" on it. Get yourself internet connected (on the tray), and click it to open a terminal.

Run `install_splatplost` in the terminal, and after that everything should be ready. Continue to "Use" section on readme.md.

Notice: the image will not try read/write your local disk and to do so needs some Linux tricks. If you're not familiar with Linux, please store your art in some netdisk, and retrieve them with Firefox browser installed on the image.

## Create image locally (Only for Linux Guru)

Use an Arch Linux machine (VM, bare metal are both OK) and install `archiso`. Enter the `imagebuilder` folder and run:

```bash
make build_packages
make build
```

Run `make clean_all` to clean all.