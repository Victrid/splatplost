# Splatplost

[中文](readme.zh-CN.md)

Splatplost is a software-based Splatpost plotter based on [libnxctrl](https://github.com/Victrid/libnxctrl). Unlike the former commonly used USB printer which requires a Teensy, or AVR based microcontrollers, You only need a device with bluetooth connection, which is easy to use. With an optimized printing algorithm, this can save you up to 1/3 time printing it.

## Basic Usage

### Installation

It's recommended to use a physical linux machine. If you don't have one, you may check the [flashable image](docs/image.md). Windows or macOS is not supported, as libnxctrl is based on bluez, the linux bluetooth stack.

You need to use `sudo`, or root, as altering bluetooth is a privileged operation.

```bash
sudo pip install splatplost
```

This will automatically install the required dependencies.

If you need to update the library, you can use `pip install --upgrade splatplost`.

### Use

Start the GUI with:

```bash
sudo splatplost
```

## Help needed / I found a bug / Feature request

Click the "Issues" link above to open an issue on the repository.

If you find bugs on connection, please open issues to [libnxctrl](https://github.com/Victrid/libnxctrl).

## Contributing

- **Internationalization**: No coding skills needed, see [translation](docs/translation.md) for more information.
- **Documentation**: No coding skills needed
- Help resolving issues
- Refactor, bug fixes
- Algorithm optimization

## License

This project is based on libnxctrl, so it is released under GPLv3.

