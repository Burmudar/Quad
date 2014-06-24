from PIL import Image, ImageDraw, ImageFont

class Quad(object):
    pass

class Box(object):
    def __init__(self, x0,y0, x1, y1, min_size=50):
        self.width = x1-x0
        self.height = y1-y0
        self.size = (self.width,self.height)
        self.x0 = x0
        self.x1 = x1
        self.y1 = y1
        self.y0 = y0
        self.chilldren = []
        self.min_size=min_size
        self.point = []

    def is_larger(self, width, height):
        return width < self.width and height < self.height

    def is_smaller(self, width, height):
        return width < self.width and height > self.height

    def is_inside(self, x, y):
        return (self.x0 < x and x < self.x1) and (self.y0 < y and y < self.y1)

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
        content = 'Box<x0: {}, y0: {}, x1: {}, y1: {}, width: {}, height: {}, chilldren: {}, points: {}'.format(self.x0,
                self.y0,
                self.x1,
                self.y1,
                self.width,
                self.height,
                len(self.chilldren),
                self.point
                )
        return content

    def subdivide(self):
        if self.pixel_size() < self.min_size:
            return []
        half_x_point = self.x0 + (self.width / 2.0)
        half_y_point = self.y0 + (self.height / 2.0)
        top_left_quad = Box(self.x0, self.y0, half_x_point, half_y_point)
        top_right_quad = Box(half_x_point, self.y0, self.x1, half_y_point)
        bot_left_quad = Box(self.x0, half_y_point, half_x_point, self.y1)
        bot_right_quad = Box(half_x_point, half_y_point, self.x1, self.y1)
        return [top_left_quad, top_right_quad, bot_left_quad, bot_right_quad]

    def is_valid_colour(self, col, invert):
        if isinstance(col, int):
            return col != 0
        elif len(col) >= 3:
            r = col[0]
            g = col[1]
            b = col[2]
            return (r == 255 and g == 255 and b == 255) if invert is True else (r != 255 and g != 255 and b != 255)

    def insert(self, x,y, col, invert=False):
        if self.is_valid_colour(col,invert) == False:
            return None
        if self.is_inside(x,y):
            if len(self.chilldren) == 0:
                self.point.append((x,y))
                if len(self.point) == 5:
                    self.chilldren = self.subdivide()
                    for p in self.point:
                        x0,y0 = p
                        self.insert_into_chilldren(x0,y0,col,invert)
            else:
                self.insert_into_chilldren(x,y,col,invert)

    def insert_into_chilldren(self,x,y,col,invert):
        for c in self.chilldren:
            c.insert(x,y,col,invert)

    def coord_list(self, x_offset=0, y_offset=0):
        return [x_offset+self.x0,y_offset+self.y0, y_offset+self.x1, y_offset+self.y1]

    def draw(self, canvas, color='red', no_point=False):
        if len(self.point) == 0:
            return
        if no_point is not True:
            for p in self.point:
                canvas.point(p, color)
        canvas.rectangle(self.coord_list(), outline=color)
        for c in self.chilldren:
            c.draw(canvas,color, no_point)


def create_image_with_text(text='Hello', size=(1400,900), font_size=200):
    font = ImageFont.truetype('/Library/Fonts/Microsoft/Gill Sans MT Bold.ttf', font_size)
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
            root.insert(x_offset + x, y_offset + y,source.getpixel((x,y)), invert)

def signature(title, subtitle):
    title = title
    subtitle = subtitle
    base = Image.new(mode='RGB', color='white', size=(1400,190))
    logo = Image.open('logo.png')
    img1 = create_image_with_text(title, size=(650,190), font_size=90)
    img2 = create_image_with_text(subtitle, size=(650,190), font_size=90)
    root = Box(0,0,1400,190,min_size=5)
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
    root = Box(0,0,1400,900,min_size=5)
    quadrasize(img1,0,0, False, root)
    quadrasize(img2,0,600,True,root)
    draw_tree(base,color=(220,20,60),root=root)
    base.save(title+'-'+subtitle+"-top_down.png")

def single(text):
    base = Image.new(mode='RGB', color='white', size=(1400,900))
    img1 = create_image_with_text(text, size=(1400,900), font_size=375)
    root = Box(0,0,1400,900,min_size=5)
    quadrasize(img1,0,0, False, root)
    p = (600,475)
    import datetime
    start = datetime.datetime.now()
    print('Start: {}'.format(start))
    print("Intersect {}: {}".format(p, root.intersect(p)))
    end = datetime.datetime.now()
    print('Start: {}'.format(end))
    print('Duration: {}'.format((end-start).total_seconds()))
    draw_tree(base,color=(220,20,60),root=root, no_point=True)
    base.save(text+"-single.png")


if __name__ == '__main__':
    #single('Masters')
    top_down_signature('Andre','Doos')
