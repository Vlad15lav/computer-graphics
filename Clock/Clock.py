import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import json
import math

class Clock:
    def __init__(self, path_digits):
        # Digits coordinates and curves
        self.__digits = self.__readjson(path_digits)
        self.__vertexes = self.__parsingobj()

        # Time and timezone
        self.__zone = self.__getzone()
        self.__time = self.__gettime()

        # Plot
        self.fig, self.ax = plt.subplots(figsize=(6, 1.5))
        self.fig.suptitle('Bezier clock')
        self.ax.set_axis_off()
        self.img = np.zeros((500, 3000, 3), dtype=np.uint8)
        self.im = plt.imshow(self.img, animated=True)

        # Animation values
        self.__fps = 4
        self.__cur_frame = 0
        self.__tanim = np.linspace(0, 1, self.__fps)
        self.__changedigits = self.__addsecond()
        self.__hidesplit = True

        # User setting
        self.__color = np.array([0, 255, 0])
        self.__bgcolor = np.array([0, 0, 0])
        self.__bright = 5  # 0 - 25

    # Read json file
    def __readjson(self, path_digits):
        f = open(path_digits, 'r')
        digits = json.load(f)
        f.close()
        return digits

    # Parsing obj digits
    def __parsingobj(self):
        t_thresh = 10
        digits_curve = []
        for i, digit in enumerate(self.__digits):
            num = []
            for segment in self.__digits[digit]:
                xy = np.array(self.__digits[digit][segment], dtype=np.float32)
                for t in np.linspace(0, 1, t_thresh):
                    num.append(self.__bezier(xy, t))
            digits_curve.append(num)
        digits_curve = np.array(digits_curve, dtype=np.float32)
        for dig in range(digits_curve.shape[0]):
            xy_min, xy_max = digits_curve[dig].min(axis=0), digits_curve[dig].max(axis=0)
            xy_center = (xy_min + xy_max) / 2
            digits_curve[dig] += 250 - xy_center
        return np.array(digits_curve, dtype=np.int32)

    # Get local time
    def __gettime(self):
        h, m, s = time.strftime('%X').split(':')
        return np.array([h, m, s], dtype=np.int32)

    # Get local timezone
    def __getzone(self):
        return np.int(-time.timezone / 3600)

    # hms to hhmmss
    def __splitnumbers(self, time):
        h, m, s = time
        return np.array([*list('0{}'.format(h)[-2:]), *list('0{}'.format(m)[-2:]), *list('0{}'.format(s)[-2:])], dtype=np.int32)

    # Check change digits
    def __addsecond(self):
        numbers_before = self.__splitnumbers(self.__time)
        h, m, s = self.__time
        s += 1
        if s == 60:
            m, s = m + 1, 0
            if m == 60:
                h, m = h + 1, 0
                if h == 24:
                    h = 0
        numbers_after = self.__splitnumbers(np.array([h, m, s]))
        return np.stack((numbers_before, numbers_after), axis=1)

    # Bezier curve 3 orders
    def __bezier(self, xy_cord, tr):
        xy_value = xy_cord[0, :] * ((1 - tr) ** 3) + 3 * xy_cord[1, :] * tr * ((1 - tr) ** 2) + 3 * xy_cord[2, :] * \
                   (1 - tr) * (tr ** 2) + xy_cord[3, :] * (tr ** 3)
        xy_value = np.array(xy_value, dtype=np.int32)
        return xy_value[0], xy_value[1]

    # Intermediate representation for switch digits
    def __transition(self, s1, s2, u):
        xy = (1 - u) * s1 + u * s2
        xy = np.int_(xy)
        return xy[0], xy[1]

    # Draw pixel
    def __drawpixel(self, x0, y0):
        b = self.__bright
        self.img[y0-b:y0+b, x0-b:x0+b] = self.__color

    # The Algorithm Bresenham
    def __drawline(self, x0, y0, x1, y1):
        deltaX, deltaY = x1 - x0, y1 - y0
        move_x, deltaX = int(math.copysign(1, deltaX)), abs(deltaX)
        move_y, deltaY = int(math.copysign(1, deltaY)), abs(deltaY)
        if deltaX > deltaY:
            step_x, step_y, step, length = move_x, 0, deltaY, deltaX  # movement x
        else:
            step_x, step_y, step, length = 0, move_y, deltaX, deltaY  # movement y
        x, y = x0, y0
        error = 0
        for i in range(length):
            error -= step
            if error < 0:
                error += length
                x += move_x
                y += move_y
            else:
                x += step_x
                y += step_y
            self.__drawpixel(x, y)

    # Update function for animation
    def __update(self, idx):
        if idx % 5 == 0:
            self.__drawsplit()

        # Change
        if self.__cur_frame == self.__fps:
            time_tick = self.__gettime()
            time_tick[0] = (time_tick[0] + self.__zone) % 24
            if time_tick[2] != self.__time[2]:
                self.__cur_frame = 0
                self.__time = time_tick
                self.__changedigits = self.__addsecond()
        else:
            for i, num in enumerate(self.__changedigits):
                if num[0] != num[1]:
                    shift = i * 500
                    # Clear digit
                    self.img[:, shift + 10:shift + 490] = self.__bgcolor
                    # Change digit
                    now_num, next_num = num
                    for j in range(self.__vertexes[i].shape[0] - 1):
                        xy0_from = np.array([self.__vertexes[now_num][j][0] + shift, self.__vertexes[now_num][j][1]])
                        xy0_to = np.array([self.__vertexes[next_num][j][0] + shift, self.__vertexes[next_num][j][1]])
                        xy1_from = np.array([self.__vertexes[now_num][j+1][0] + shift, self.__vertexes[now_num][j+1][1]])
                        xy1_to = np.array([self.__vertexes[next_num][j+1][0] + shift, self.__vertexes[next_num][j+1][1]])
                        x0, y0 = self.__transition(xy0_from, xy0_to, self.__tanim[self.__cur_frame])
                        x1, y1 = self.__transition(xy1_from, xy1_to, self.__tanim[self.__cur_frame])
                        self.__drawline(x0, y0, x1, y1)

            self.im.set_array(self.img)
            self.__cur_frame += 1
        return self.im,

    # Draw split points
    def __drawsplit(self):
        left_p, right_p = 3000 // 3, (3000 * 2) // 3
        if self.__hidesplit:
            top_p, bot_p = 500 // 3, (500 * 2) // 3
            self.img[top_p - 5:top_p + 5, left_p - 5:left_p + 5] = self.__color
            self.img[bot_p - 5:bot_p + 5, left_p - 5:left_p + 5] = self.__color
            self.img[top_p - 5:top_p + 5, right_p - 5:right_p + 5] = self.__color
            self.img[bot_p - 5:bot_p + 5, right_p - 5:right_p + 5] = self.__color
        else:
            self.img[:, left_p - 5:left_p + 5] = self.__bgcolor
            self.img[:, right_p - 5:right_p + 5] = self.__bgcolor
        self.__hidesplit = not self.__hidesplit

    # First frame for plot
    def __start_time(self):
        self.cur_frame = 0
        self.__time = self.__gettime()
        self.__time[0] = (self.__time[0] + self.__zone) % 24
        self.__drawsplit()
        # Draw digits
        for i, digit in enumerate(self.__splitnumbers(self.__time)):
            for j in range(self.__vertexes[digit].shape[0] - 1):
                self.__drawline(self.__vertexes[digit][j][0] + i * 500, self.__vertexes[digit][j][1],
                              self.__vertexes[digit][j + 1][0] + i * 500, self.__vertexes[digit][j + 1][1])

    # Set color for digits and split points
    def setcolor(self, color):
        self.__color = color

    # Set color for background
    def setbgcolor(self, color):
        self.__bgcolor = color

    # Set the brightness value
    def setbrightness(self, value):
        self.__bright = value

    # Show clock
    def show(self, zone=None):
        self.__zone = self.__getzone()
        self.img[:] = self.__bgcolor
        if zone is not None:
            self.__zone = zone - self.__zone
        else:
            self.__zone = 0
        self.__start_time()
        self.__cur_frame = self.__fps
        animation = FuncAnimation(self.fig, self.__update, blit=True, interval=10)
        plt.show()

clock = Clock('digits.json')
clock.setcolor((0, 0, 255)) # Digits and split points color
clock.setbgcolor((0, 0, 0)) # Background color
clock.setbrightness(5) # 0 - 25
clock.show(zone=None) # Select timezone