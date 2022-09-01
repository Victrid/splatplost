# Splatplost

[中文](readme.zh-CN.md)

Splatplost is a software-based Splatpost plotter based on [libnxctrl](https://github.com/Victrid/libnxctrl). Unlike the former commonly used USB printer which requires a Teensy, or AVR based microcontrollers, You only need a device with bluetooth connection, which is easy to use. With an optimized printing algorithm, this can save you up to 1/3 time printing it.

## Basic Usage

### Installation

It's recommended to use a physical linux machine. If you don't have one, you may download an Live-CD from [Ubuntu](https://www.ubuntu.com/download/desktop) and continue. Windows or MacOS is not supported, as libnxctrl is based on bluez, the linux bluetooth stack.

You need to use `sudo`, or root, as altering bluetooth is a privileged operation.

```bash
sudo pip install splatplost
```

This will automatically install the required dependencies.

If you need to update the library, you can use `pip install --upgrade splatplost`.

### Use

Generate a plotting plan with:

```bash
sudo splatplan -i <your image> -o <output filename>
```

Start the printer:

```bash
sudo splatplot --order <output filename>
```

You may check the printer's option (for example, stable mode, customizing delay and press time, etc.) with:

```bash
sudo splatplot --help
```

When "Open the pairing menu on switch." shows on the screen, go to the pairing menu, and the switch will be paired.

Then you may enter the game and enter splatpost interface using your own controller. Remember to set the brush to minimum one.

When everything is prepaired, disconnect your own controller, (for example, press the tiny pairing button on the top of the controller), and you'll enter the "connect to controller" menu.

Press enter or "A" button on your computer as instructed, the plotting will begin. You may see the progress and ETA time while printing.

## Help needed / I found a bug / Feature request

Click the "Issues" link above to open an issue on the repository.

If you find bugs on connection, please open issues to [libnxctrl](https://github.com/Victrid/libnxctrl).

## Contributing



## License

This project is based on libnxctrl, so it is released under GPLv3.

