import os

from PIL import Image, ImageDraw, ImageFont
try:
    from waveshare_epd import epd2in13b_V4
except ImportError:
    pass
from data.plot import Plot
from presentation.observer import Observer

SCREEN_HEIGHT = 122
SCREEN_WIDTH = 250

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roses.ttf'), 8)
FONT_LARGE = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'PixelSplitter-Bold.ttf'), 26)

class Epd2in13bv4(Observer):

    def __init__(self, observable, mode):
        super().__init__(observable=observable)
        self.epd = epd2in13b_V4.EPD()

        self.epd.init()
        self.image_black = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        self.image_ry = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        self.draw_black = ImageDraw.Draw(self.image_black)
        self.draw_ry = ImageDraw.Draw(self.image_ry)
        self.mode = mode
 
    def form_image(self, prices, screen_draw):
        screen_draw.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), fill="#ffffff")
        screen_draw = self.draw_black
        if self.mode == "candle":
            Plot.candle(prices, size=(SCREEN_WIDTH - 45, 93), position=(41, 0), draw=screen_draw)
        else:
            last_prices = [x[3] for x in prices]
            Plot.line(last_prices, size=(SCREEN_WIDTH - 42, 93), position=(42, 0), draw=screen_draw)

        flatten_prices = [item for sublist in prices for item in sublist]
        Plot.y_axis_labels(flatten_prices, FONT_SMALL, (0, 0), (38, 89), draw=screen_draw)
        screen_draw.line([(10, 98), (240, 98)])
        screen_draw.line([(39, 4), (39, 94)])
        screen_draw.line([(60, 102), (60, 119)])
        Plot.caption(flatten_prices[len(flatten_prices) - 1], 95, SCREEN_WIDTH, FONT_LARGE, screen_draw)

    def update(self, data):
        self.form_image(data, self.draw_black)
        image_black_rotated = self.image_black.rotate(180)
        # TODO: add a way to switch between partial and full update
        # epd.presentation(epd.getbuffer(screen_image_rotated))
        image_ry_rotated = self.image_ry.rotate(180)
        self.epd.display(
            self.epd.getbuffer(image_black_rotated),
            self.epd.getbuffer(image_ry_rotated)
        )

    def close(self):
        epd2in13b_V4.epdconfig.module_exit()
