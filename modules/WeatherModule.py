import datetime
import io
import logging
import os
import pygame
import requests
import sys


class Utils:
    color_maps = [
        # hot: red
        {
            "celsius_a": 28,
            "celsius_b": 99,
            "color_a": pygame.Color("red")[:3],
            "color_b": pygame.Color("red")[:3]
        },
        # fine: orange - red
        {
            "celsius_a": 23,
            "celsius_b": 28,
            "color_a": pygame.Color("orange")[:3],
            "color_b": pygame.Color("red")[:3]
        },
        # chilly: white - orange
        {
            "celsius_a": 15,
            "celsius_b": 23,
            "color_a": pygame.Color("white")[:3],
            "color_b": pygame.Color("orange")[:3]
        },
        # cold: blue - white
        {
            "celsius_a": 0,
            "celsius_b": 15,
            "color_a": pygame.Color("blue")[:3],
            "color_b": pygame.Color("white")[:3]
        },
        # cold: blue
        {
            "celsius_a": -99,
            "celsius_b": 0,
            "color_a": pygame.Color("blue")[:3],
            "color_b": pygame.Color("blue")[:3]
        }
    ]

    @staticmethod
    def strftime(timestamp, format):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime(format)

    @staticmethod
    def percentage_text(value):
        return "{}%".format(value)

    @staticmethod
    def speed_text(value, units):
        return ("{} km/h" if units == "si" else "{} mi/h").format(value)

    @staticmethod
    def temparature_text(value, units):
        return ("{}°C" if units == "si" else "{}°F").format(value)

    @staticmethod
    def heat_index(f, h):
        if (f < 80):
            return f
        return -42.379 + 2.04901523 * f + 10.14333127 * h - 0.22475541 * \
            f * h - 6.83783 * (10 ** -3) * (f ** 2) - 5.481717 * \
            (10 ** -2) * (h ** 2) + 1.22874 * (10 ** -3) * (f ** 2) * \
            h + 8.5282 * (10 ** -4) * f * (h ** 2) - 1.99 * \
            (10 ** -6) * (f ** 2) * (h ** 2)

    @staticmethod
    def heat_color(temperature, humidity, units):
        def celsius(f):
            return (f - 32.0) * 0.555556

        def fahrenheit(c):
            return (c * 1.8) + 32.0

        def gradation(color_a, color_b, val_a, val_b, val_x):
            def geometric(a, b, p):
                return int((b - a) * p / 100 + a)

            p = (val_x - val_a) / (val_b - val_a) * 100
            color_x = [geometric(color_a[i], color_b[i], p) for i in range(3)]
            return color_x

        f = fahrenheit(temperature) if units == "si" else temperature
        c = celsius(Utils.heat_index(f, humidity))

        color = pygame.Color("white")[:3]
        for cm in Utils.color_maps:
            if cm["celsius_a"] <= c and c < cm["celsius_b"]:
                color = gradation(cm["color_a"], cm["color_b"],
                                  cm["celsius_a"], cm["celsius_b"], c)
                break
        return color


class WeatherModule:
    def __init__(self, screen, fonts, language, units, config):
        self.screen = screen
        self.fonts = fonts
        self.language = language
        self.units = units
        self.config = config
        self.rect = pygame.Rect(config["rect"])

    def quit(self):
        pass

    def color(self, name):
        return pygame.Color(name)[:3]

    def font(self, style, size):
        return self.fonts[style][size]

    def draw(self, weather):
        self.screen.fill(self.color("white"), rect=self.rect)

    def clean(self):
        self.screen.fill(self.color("black"), rect=self.rect)

    def draw_text(self, text, style, size, color, position, align="left"):
        """
        :param text: text to draw
        :param style: font style. ["regular", "bold"]
        :param size: font size. ["small", "medium", "large"]
        :param color: color name or RGB color tuple
        :param position: render relative position (x, y)
        :param align: text align. ["left", "center", "right"]
        """
        (x, y) = position
        font = self.font(style, size)
        size = font.size(text)
        color = self.color(color) if isinstance(color, str) else color
        if align == "center":
            x = (self.rect.width - size[0]) / 2
        elif align == "right":
            x = self.rect.width - size[0]
        self.screen.blit(
            font.render(text, True, color),
            (self.rect.left + x, self.rect.top + y))

    def load_icon(self, icon):
        file = "{}/icons/{}".format(sys.path[0], icon)
        if os.path.isfile(file):
            return pygame.image.load(file)
        else:
            logging.error("{} not found.".format(file))
            return None

    def get_darksky_icon(self, name, size):
        try:
           response = requests.get(
                "https://darksky.net/images/weather-icons/{}.png".format(name))
            response.raise_for_status()

            image = pygame.image.load(io.BytesIO(response.content))

            pixels = pygame.PixelArray(image)
            pixels.replace(pygame.Color("black"), pygame.Color("dimgray"))
            del pixels

            (w, h) = image.get_size()
            if w >= h:
                (w, h) = (size, int(size / w * h))
            else:
                (w, h) = (int(size / w * h), size)
            image = pygame.transform.scale(image, (w, h))

            return image

        except Exception as e:
            logging.error(e)
            return None

    def draw_image(self, image, position, angle=0):
        """
        :param image: image to draw
        :param position: render relative position (x, y)
        :param angle: counterclockwise  degrees angle
        """
        if image:
            (x, y) = position
            if angle:
                (w, h) = image.get_size()
                image = pygame.transform.rotate(image, angle)
                x = x + (w - image.get_width()) / 2
                y = h + (h - image.get_height()) / 2
            self.screen.blit(image, (self.rect.left + x, self.rect.top + y))
