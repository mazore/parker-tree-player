# import atexit
# from line_profiler import LineProfiler
import numpy as np
import pygame
from math import cos, sin, pi
from random import randint
from time import time
from parse_csv import parse_csv
from play3d.models import Model
from play3d.three_d import Device, Camera
import sys

try:
    SEQ_FILENAME = sys.argv[1]
except IndexError:
    SEQ_FILENAME ='sequences/pulse-red.csv'
COORDS_FILENAME = 'coords/parker.csv'
print('Playing file:', SEQ_FILENAME)
print('Using coords:', COORDS_FILENAME)

WIDTH, HEIGHT = 640, 480

# profiler = LineProfiler()
# atexit.register(profiler.print_stats)


class Light:
    def __init__(self, main, position, color=None, shimmering=False):
        self.main = main
        self.position = np.matrix(position).reshape((3, 1))
        if color is None:
            color = randint(0, 255), randint(0, 255), randint(0, 255)

        self.model = Model(
            position=position,
            data=[[0, 0, 0, 1]],
            color=color,
            shimmering=shimmering
        )

    def set_color(self, index):
        if self.main.frame_number >= len(self.main.animation_data):
            print('Finished')
            quit()
        frame = self.main.animation_data[self.main.frame_number]
        try:
            g, r, b = frame[index]
            self.model.color = r, g, b
        except IndexError:  # Account for floor objects without color data
            pass

    def draw(self):
        pos = np.dot(self.main.rotation_z, self.position)
        pos = np.dot(self.main.rotation_x, pos)
        x, y, z = pos[0, 0], pos[1, 0], pos[2, 0]
        self.model.set_position(x, y, z)
        self.model.draw()


class Main:
    def __init__(self):
        self.setup_scene()

        self.lights = []
        self.setup_lights()

        self.animation_data = parse_csv(SEQ_FILENAME)
        self.frame_number = 0

        self.mainloop()

    def set_pixel(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x, HEIGHT-y), 2)

    def setup_scene(self):
        Device.viewport(WIDTH, HEIGHT)
        Device.set_renderer(self.set_pixel)

        pygame.init()
        self.screen = pygame.display.set_mode(Device.get_resolution())
        self.camera = Camera.get_instance()
        self.camera.move(x=0, y=5, z=1.5)
        self.camera.rotate('x', 90)

    def setup_lights(self):
        for line in open(COORDS_FILENAME, encoding='utf-8'):
            position = [float(e) for e in line.strip('\ufeff').split(',')]
            self.lights.append(Light(self, position, shimmering=False))
        ground_positions = []
        subdivisions = 2
        for i in range(-subdivisions, subdivisions+1):
            for j in range(-subdivisions, subdivisions+1):
                ground_positions.append([i/subdivisions, j/subdivisions, 0])
        for position in ground_positions:
            self.lights.append(Light(self, position, color=(255, 255, 255)))

    def handle_rotation(self):
        if not pygame.mouse.get_pressed()[0] and 'rotation_z' in self.__dict__:
            return
        if 'rotation_z' not in self.__dict__:  # First frame
            angle_x = 0
            angle_z = 0
        else:
            x_ratio = pygame.mouse.get_pos()[0] / WIDTH
            y_ratio = pygame.mouse.get_pos()[1] / HEIGHT
            angle_z = x_ratio * pi * 2
            angle_x = y_ratio * pi/2 - pi/4
        self.rotation_z = np.matrix([
            [cos(angle_z), sin(angle_z), 0],
            [-sin(angle_z), cos(angle_z), 0],
            [0, 0, 1]
        ])
        self.rotation_x = np.matrix([
            [1, 0, 0],
            [0, cos(angle_x), sin(angle_x)],
            [0, -sin(angle_x), cos(angle_x)]
        ])

    def mainloop(self):
        while True:
            self.frame_number += 1
            t = time()

            self.screen.fill((50, 50, 50))

            self.handle_rotation()

            for i, light in enumerate(self.lights):
                light.set_color(i)
                light.draw()

            pygame.display.flip()
            if pygame.event.get(pygame.QUIT):
                quit()

            # if time() != t:  # Fix divide by zero error
                # print(round(1 / (time() - t), 2), 'FPS')


if __name__ == '__main__':
    Main()
