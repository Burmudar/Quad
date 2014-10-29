from PIL import Image, ImageDraw, ImageFont
import math
class Quad(object):
    pass

class ColorUtil(object):
    def __init__(self):
        self._sum = [0.0, 0.0, 0.0]
        self._count = 0

    @property
    def sum_r(self):
        return self._sum[0]

    @sum_r.setter
    def sum_r(self, val):
        self._sum[0] = val

    @property
    def sum_g(self):
        return self._sum[1]

    @sum_g.setter
    def sum_g(self, val):
        self._sum[1] = val

    @property
    def sum_b(self):
        return self._sum[2]

    @sum_b.setter
    def sum_b(self, val):
        self._sum[2] = val

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, val):
        self._count = val

    def add(self, pixel):
        self.sum_r += pixel.r
        self.sum_g += pixel.g
        self.sum_b += pixel.b
        self.count += 1


    def avg(self):
        avg = [0.0,0.0,0.0]
        if self.count != 0:
            avg[0] = self.sum_r / self.count
            avg[1] = self.sum_g / self.count
            avg[2] = self.sum_b / self.count
        return avg

    def distance_from_avg_normalized(self, p):
        avg = self.avg()
        distance = [0.0,0.0,0.0]
        distance[0] = math.fabs(avg[0] - p.r)
        distance[1] = math.fabs(avg[1] - p.g)
        distance[2] = math.fabs(avg[2] - p.b)
        return ((distance[0] + distance[1] + distance[2]) / 3.0) / 255.0

class Point(object):

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x;

    @x.setter
    def x(self, val):
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._x = val

class Pixel(object):

    def __init__(self, p, col):
        self._pos = p
        self._colour = col

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, val):
        if isinstance(val, Point):
            self._pos = val
        else:
            raise ValueError("Only Point type accepted as valid for position")

    @property
    def r(self):
        return self._colour[0]

    @r.setter
    def r(self, val):
        self._colour[0] = val

    @property
    def g(self):
        return self._colour[1]

    @g.setter
    def g(self, val):
        self._colour[1] = val

    @property
    def b(self):
        return self._colour[2]

    @b.setter
    def b(self, val):
        self._colour[2] = val

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, val):
        if len(val) >= 3:
            self._colour = val
        else:
            raise ValueError("Only colour vectors with length 3 or more is allowed")

    def draw(self, canvas):
        canvas.point((self.position.x, self.position.y), self.colour)

    
class Box(object):
    def __init__(self, p0, p1, min_size=50):
        self.width = p1.x - p0.x
        self.height = p1.y - p0.y
        self.size = (self.width,self.height)
        self.p0 = p0
        self.p1 = p1
        self.chilldren = []
        self.min_size=min_size
        self.pixels = []
        self.ColorUtil = ColorUtil()
        self.threshold = 0.5

    def is_larger(self, width, height):
        return width < self.width and height < self.height

    def is_smaller(self, width, height):
        return width < self.width and height > self.height

    def is_inside(self, p):
        return (self.p0.x < p.x and p.x < self.p1.x) and (self.p0.y < p.y and p.y < self.p1.y)

    def pixel_size(self):
        return self.width * self.height;

    def intersect(self, point):
        if self.is_inside(point[0], point[1]):
            if len(self.chilldren) > 0:
                for c in self.chilldren:
                    leaf = c.intersect(point)
                    if leaf is not None:
                        return leaf
                return None
            else:
                return self
        else:
            return None

    def __repr__(self):
        content = 'Box<p0: {}, p1: {}, width: {}, height: {}, chilldren: {}, pixels: {}'.format(
                self.p0,
                self.p1,
                self.width,
                self.height,
                len(self.chilldren),
                self.pixels
                )
        return content

    def subdivide(self):
        if self.pixel_size() < self.min_size:
            return []
        half_x_point = self.p0.x + (self.width / 2.0)
        half_y_point = self.p0.y + (self.height / 2.0)
        top_left_quad = Box(Point(self.p0.x, self.p0.y), Point(half_x_point, half_y_point))
        top_right_quad = Box(Point(half_x_point, self.p0.y), Point(self.p1.x, half_y_point))
        bot_left_quad = Box(Point(self.p0.x, half_y_point), Point(half_x_point, self.p1.y))
        bot_right_quad = Box(Point(half_x_point, half_y_point), Point(self.p1.x, self.p1.y))
        return [top_left_quad, top_right_quad, bot_left_quad, bot_right_quad]

    def is_close_to_pixel_avg(self, pixel):
        if len(self.pixels) == 0:
            return True
        dist = self.ColorUtil.distance_from_avg_normalized(pixel)
        if dist < 0.3:
            return True
        return False


    def add_pixel(self, pixel):
        self.pixels.append(pixel)
        self.ColorUtil.add(pixel)

    def insert(self, pixel, invert=False):
        if self.is_inside(pixel.position):
            if len(self.chilldren) == 0:
                if self.is_close_to_pixel_avg(pixel):
                    self.add_pixel(pixel)
                else:
                    self.chilldren = self.subdivide()
                    for p in self.pixels:
                        self.insert_into_chilldren(p,invert)
            else:
                self.insert_into_chilldren(pixel,invert)

    def insert_into_chilldren(self,pixel,invert):
        for c in self.chilldren:
            c.insert(pixel,invert)

    def coord_list(self, x_offset=0, y_offset=0):
        return [x_offset+self.p0.x,y_offset+self.p0.y, y_offset+self.p1.x, y_offset+self.p1.y]

    def draw(self, canvas, color='black', no_point=False):
        if len(self.pixels) == 0:
            return
        #for p in self.pixels:
            #p.draw(canvas)
        avg = self.ColorUtil.avg()
        canvas.rectangle(self.coord_list(), outline=color, fill=(int(avg[0]), int(avg[1]), int(avg[2])))
        for c in self.chilldren:
            c.draw(canvas,color, no_point)


def create_image_with_text(text='Hello', size=(1400,900), font_size=200):
    #font = ImageFont.truetype('/Library/Fonts/Microsoft/Gill Sans MT Bold.ttf', font_size)
    font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-M.ttf', font_size)
    text_img = Image.new(mode='RGB', color='white', size=size)
    canvas = ImageDraw.Draw(text_img)
    text_size = canvas.textsize(text, font)
    halfwidth = text_img.size[0] / 2.0
    halfheight = text_img.size[1] / 2.0
    x = halfwidth - (text_size[0] / 2.0)
    y = halfheight - (text_size[1] / 1.25)
    canvas.text((x,y),text=text,fill='black',font=font)
    text_img.save(text+'.png')
    return text_img

def draw_tree(dest, color='black', root=None, no_point=False):
    img = dest
    canvas = ImageDraw.Draw(img)
    root.draw(canvas,color,no_point)

def quadrasize(source,x_offset=0, y_offset=0, invert=False, root=None):
    width, height = source.size
    for x in range(width):
        for y in range(height):
            point  = Point(x_offset + x, y_offset + y)
            pixel = Pixel(point, source.getpixel((x,y)))
            root.insert(pixel, invert)

def signature(title, subtitle):
    title = title
    subtitle = subtitle
    base = Image.new(mode='RGB', color='white', size=(1400,190))
    logo = Image.open('logo.png')
    img1 = create_image_with_text(title, size=(650,190), font_size=90)
    img2 = create_image_with_text(subtitle, size=(650,190), font_size=90)
    root = Box(Point(0,0),Point(1400,190),min_size=5)
    quadrasize(logo, 10,40, False, root)
    quadrasize(img1,250,0, True, root)
    quadrasize(img2,830,0,False,root)
    draw_tree(base,color=(220,20,60),root=root)
    base.save(title+'-'+subtitle+"-signature.png")

def top_down_signature(title,subtitle):
    title = title
    subtitle = subtitle
    base = Image.new(mode='RGB', color='white', size=(1400,900))
    img1 = create_image_with_text(title, size=(1400,600), font_size=400)
    img2 = create_image_with_text(subtitle, size=(1400,300), font_size=250)
    root = Box(Point(0,0), Point(1400,900),min_size=5)
    quadrasize(img1,0,0, False, root)
    quadrasize(img2,0,600,True,root)
    draw_tree(base,color=(220,20,60),root=root)
    base.save(title+'-'+subtitle+"-top_down.png")

def pic():
    psize = (822,855)
    base = Image.new(mode="RGB", color="white", size=psize)
    filename_prefix = "nathan"
    img1 = Image.open(filename_prefix + ".png")
    root = Box(Point(0,0), Point(psize[0], psize[1]),min_size=5)
    import datetime
    start = datetime.datetime.now()
    print('Start: {}'.format(start))
    quadrasize(img1,0,0, False, root)
    end = datetime.datetime.now()
    print('End: {}'.format(end))
    print('Duration: {}'.format((end-start).total_seconds()))
    draw_tree(base,root=root, no_point=True)
    base.save(filename_prefix + "-single.png")

def single(text):
    base = Image.new(mode='RGB', color='white', size=(1400,900))
    img1 = create_image_with_text(text, size=(1400,900), font_size=375)
    root = Box(Point(0,0), Point(1400,900),min_size=5)
    quadrasize(img1,0,0, False, root)
    import datetime
    start = datetime.datetime.now()
    print('Start: {}'.format(start))
    end = datetime.datetime.now()
    print('End: {}'.format(end))
    print('Duration: {}'.format((end-start).total_seconds()))
    draw_tree(base,color=(220,20,60),root=root, no_point=True)
    base.save(text+"-single.png")


if __name__ == '__main__':
    pic()
    #single('Masters')
    #top_down_signature('Andre','Doos')
