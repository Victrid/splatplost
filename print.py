#!/usr/bin/env python3

import asyncio
import os
import sys
import tqdm

from aioconsole import ainput

from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server


async def loader():
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')
    transport, protocol = await create_hid_server(controller_protocol_factory(Controller.from_arg("PRO_CONTROLLER"), spi_flash=FlashMemory()),
                                                  ctl_psm=17,
                                                  itr_psm=19)
    controller_state = protocol.get_controller_state()
    return transport, controller_state


async def printcf(order_list: list):
    # waits until controller is fully connected
    print("Open the pairing menu on switch.")
    transport, controller_state = await loader()
    await controller_state.connect()

    await ainput(prompt='Press <enter> to draw.')
    await asyncio.sleep(1)

    # Goto (0,0) point
    await button_push(controller_state, 'left', sec=5)
    await button_push(controller_state, 'up', sec=5)

    # Clear
    await button_push(controller_state, 'minus')
    await asyncio.sleep(1)

    for order in tqdm.tqdm(order_list):
        await button_push(controller_state, order.strip('\n'), sec=0.08)
        await asyncio.sleep(0.08)
    await transport.close()

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        orders = f.readlines()
        asyncio.run(printcf(orders))
