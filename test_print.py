import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, writers
import sys
import tqdm


frame_num = 256


class Anim():
    def __init__(self):
        self.data = np.zeros((120, 320))
        self.pointer = (0, 0)
        with open(sys.argv[1]) as f:
            self.fig, self.axs = plt.subplots()
            t = f.readlines()
            self.orders = iter(t)
            self.step_bar = tqdm.tqdm(total=len(t), leave=False)
        self.ani = FuncAnimation(self.fig, self.update,
                                 interval=0, save_count=len(t))
        self.data[0, 0] = 0.49
        self.axs.imshow(self.data, cmap='gray_r')
        self.axs.axis('off')
        plt.show()

    def update(self, n):
        self.step_bar.update(1)
        try:
            order = next(self.orders).strip("\n")
        except StopIteration:
            self.ani.event_source.stop()
            return
        self.data[self.pointer] = 0 if self.data[self.pointer] == 0.49 else 1
        if order == "up":
            self.pointer = (self.pointer[0] - 1, self.pointer[1])
        elif order == "down":
            self.pointer = (self.pointer[0] + 1, self.pointer[1])
        elif order == "left":
            self.pointer = (self.pointer[0], self.pointer[1] - 1)
        elif order == "right":
            self.pointer = (self.pointer[0], self.pointer[1] + 1)
        elif order == "lu":
            self.pointer = (0, 0)
        elif order == "ld":
            self.pointer = (119, 0)
        elif order == "ru":
            self.pointer = (0, 319)
        elif order == "rd":
            self.pointer = (119, 319)
        elif order == "a":
            self.data[self.pointer] = 1.0
        self.data[self.pointer] = 0.51 if self.data[self.pointer] == 1 else 0.49
        self.axs.clear()
        self.axs.imshow(self.data, cmap='gray_r')
        self.axs.axis('off')


t = Anim()
