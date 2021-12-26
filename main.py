import numpy as np
import pygame
from math import cos, sin
from random import randint
from time import time
from parse_csv import parse_csv
from play3d.models import Model
from play3d.three_d import Device, Camera

WIDTH, HEIGHT = 640, 480

SEQ_FILENAME = 'sequences/pulse-red.csv'
COORDS_FILENAME = 'coords/parker.csv'


class Light:
    def __init__(self, main, position, color=None, shimmering=True):
        self.main = main
        self.position = position
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
        x, y, z = pos[0, 0], pos[0, 1], pos[0, 2]
        self.model.set_position(x, y, z)
        self.model.draw()


class Main:
    def __init__(self):
        self.setup_scene()

        self.angle = 0

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
            self.lights.append(Light(self, position))
        ground_positions = []
        num_grounds = 1
        for i in range(-num_grounds, num_grounds+1):
            for j in range(-num_grounds, num_grounds+1):
                ground_positions.append([i/num_grounds, j/num_grounds, 0])
        for position in ground_positions:
            self.lights.append(Light(self, position, color=(255, 255, 255), shimmering=False))

    def mainloop(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            self.frame_number += 1
            t = time()

            self.screen.fill((20, 20, 20))

            self.angle += 0.02
            self.rotation_z = np.matrix([
                [cos(self.angle), sin(self.angle), 0],
                [-sin(self.angle), cos(self.angle), 0],
                [0, 0, 1]
            ])

            for i, light in enumerate(self.lights):
                light.set_color(i)
                light.draw()

            pygame.display.flip()
            if pygame.event.get(pygame.QUIT):
                quit()

            if time() != t:  # Fix divide by zero error
                print(round(1 / (time() - t), 2), 'FPS')


if __name__ == '__main__':
    Main()
