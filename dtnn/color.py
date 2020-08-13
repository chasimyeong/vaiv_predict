

class ColorPalette(object):

    def __init__(self, color):
        self.color = color

    def color_mapping(self):
        if self.color == 'R':
            return self.red()
        elif self.color == 'Y':
            return self.yellow()
        elif self.color == 'G':
            return self.green()
        elif self.color == 'B':
            return self.black()
        elif self.color == 'W':
            return self.white()

    @staticmethod
    def red():
        return 255, 51, 51

    @staticmethod
    def yellow():
        return 255, 255, 51

    @staticmethod
    def green():
        return 51, 255, 51

    @staticmethod
    def black():
        return 0, 0, 0

    @staticmethod
    def white():
        return 255, 255, 255


if __name__ == '__main__':
    print(ColorPalette('R').color_mapping())
