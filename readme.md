# Splatplost

Splatplost is a software-based Splatpost plotter based on [joycontrol](https://github.com/mart1nro/joycontrol). Unlike the former commonly used USB printer which requires a Teensy, or AVR based micro-controllers, You only need a device with bluetooth connection, which is easy to use. With an optimized printing algorithm, this can save you up to 1/3 time printing it.

## Usage

Generate the printing instructions

```bash
python ./insgen.py IMAGE.png IMAGE.order
```

Start the printer

```bash
sudo python ./print.py IMAGE.order
```

Enter the switch controller menu, and wait for the device to connect.

Then you may enter the game and splatpost interface. Press enter as instructed, the plotting will begin. You may see the progress and ETA time while printing.

## Contributing

All kinds of contributions are welcomed, especially:

**Algorithm Optimization**: The routing algorithm is pretty primitive.

**Timing**: Timing is needed for accurate ETA time displaying and find the best waiting time between button presses.

**Graphic User Interface**: Command line could be a barrier for our users.

**Localization**: Language could be a barrier for our users.

**Porting**: Non-linux users may have problem using this program due to O/S specific problems. For this please contribute to our upper stream source [joycontrol](https://github.com/mart1nro/joycontrol) directly.

## License

This project is based on joycontrol, so it is released under GPLv3.

