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

delay_factor = 0.08

async def loader(recon):
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')
    transport, protocol, recon_addr = await create_hid_server(controller_protocol_factory(Controller.from_arg("PRO_CONTROLLER"), spi_flash=FlashMemory()),
                                                              reconnect_bt_addr=recon,
                                                              ctl_psm=17,
                                                              itr_psm=19)
    controller_state = protocol.get_controller_state()
    with open("./.reconnect", "w+") as f:
        f.write(recon_addr)
    return transport, controller_state


async def reset(controller_state, left=True, up=True):
    if left:
        await button_push(controller_state, 'left', sec=5)
    else:
        await button_push(controller_state, 'right', sec=5)
    if up:
        await button_push(controller_state, 'up', sec=5)
    else:
        await button_push(controller_state, 'down', sec=5)


async def printcf(order_list: list, recon_addr):
    # waits until controller is fully connected
    if recon_addr is not None:
        print("You've already paired with a switch and is now connecting"
        " to it. To reconnect, please remove .reconnect file in the folder."
        " (This file is ususally a hidden one)")
    else:
        print("Open the pairing menu on switch.")
    transport, controller_state = await loader(recon_addr)
    await controller_state.connect()
    t = "Placeholder"
    while t != "":
        t = await ainput(prompt="Press <enter> to draw, or some words ending "
        "with <enter> to press the A on the pairing menu.")
        await button_press(controller_state, "a")

    await asyncio.sleep(1)

    # Goto (0,0) point
    await reset(controller_state)

    # Clear
    await button_push(controller_state, 'minus')
    await asyncio.sleep(1)

    for order in tqdm.tqdm(order_list):
        if order.strip('\n') == "lu":
            await reset(controller_state, left=True, up=True)
            await asyncio.sleep(delay_factor)
            continue
        if order.strip('\n') == "ru":
            await reset(controller_state, left=False, up=True)
            await asyncio.sleep(delay_factor)
            continue
        if order.strip('\n') == "ld":
            await reset(controller_state, left=True, up=False)
            await asyncio.sleep(delay_factor)
            continue
        if order.strip('\n') == "rd":
            await reset(controller_state, left=False, up=False)
            await asyncio.sleep(delay_factor)
            continue
        await button_push(controller_state, order.strip('\n'), sec=0.08)
        await asyncio.sleep(delay_factor)
    await transport.close()

if __name__ == "__main__":
    try:
        with open("./.reconnect") as f:
            recon_addr = f.read()
    except FileNotFoundError:
        recon_addr = None
    with open(sys.argv[1]) as f:
        orders = f.readlines()
        if len(sys.argv) >= 3:
            delay_factor = float(sys.argv[2])
        asyncio.run(printcf(orders, recon_addr))
