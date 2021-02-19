import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime


THRESHOLD = 0.7
SCREEN_WIDTH = 100000
SCREEN_HEIGHT = 100000
class Image(object):
    def __init__(self, image, name = None):
        if isinstance(image, Image):
            self.name = image.name
            image = image.im.copy()
        else:
            self.name = name or ""
        self.im = image
        self.shape = image.shape
        self._canny = None
        self._scale = {}
        self._gray = None
        self._green = None
        self._negative = None
        
    def canny(self):
        if self._canny is None:
            self._canny = Image(cv.Canny(self.im, 100, 200))
        return self._canny
    
    def gray(self):
        if self._gray is None:
            if len(self.im.shape) <= 2 or self.im.shape[2] <= 2:
                self._gray = self
            else:
                self._gray = Image(cv.cvtColor(self.im, cv.COLOR_BGR2GRAY))
        return self._gray
    
    def negative(self):
        if self._negative is None:
            self._negative = Image(self.im.max() - self.im)
        return self._negative
    
    def green(self):
        if self._green is None:  
            hue_image = cv.cvtColor(self.im, cv.COLOR_BGR2HSV)
            green_mask = cv.inRange(hue_image, (30, 25, 25), (90, 255,255)) / 255
            self._green = Image(self.im * green_mask[:,:,None])
        return self._green        
        
    def show(self, vmin = 0, vmax = 255, height = 16, width = 9):
        fig = plt.figure()
        fig.set_figheight(height)
        fig.set_figwidth(width)
        image = self.im.copy()
        if len(self.im.shape) >= 3:
            image[:,:,(2,1,0)] = image[:,:,(0,1,2)]
            plt.imshow(image, aspect= 'equal', vmin = vmin, vmax = vmax)
        else:
            plt.imshow(image, cmap = "gray", aspect = 'equal', vmin = vmin, vmax = vmax)
        plt.show()
        
    def scale(self, factor):
        if factor in self._scale:
            pass
        elif factor == 1:
            self._scale[factor] = self
        else:
            
            interpolation = cv.INTER_AREA if factor < 1 else cv.INTER_CUBIC
            self._scale[factor] = Image(cv.resize(self.im,
                                                  None,
                                                  0,
                                                  fx = factor,
                                                  fy = factor,
                                                  interpolation = interpolation))
        return self._scale[factor]
        
        

class Screenshot(Image):
    def __init__(self, image, name = None, t = None):
        t = t or datetime.now()
        super(Screenshot, self).__init__(image, name)
        self.time = t
        
    def reset(self):
        self._canny = None
        self._scale = {}
        self._gray = None
        self._green = None
    
class Template(Image):
    def __init__(self, image, name = None, tolerance = THRESHOLD, **kwargs):
        """
        template constructor, with optional arguments to bound where on the screen to search, and
        if there is a guess as to where to search.
        """
        super(Template, self).__init__(image, name)
        self.kwargs = kwargs
        self.tolerance = tolerance
        if "guess" in kwargs:
            guess = kwargs["guess"]
            self.xmin = guess[0] - 2 * image.shape[1]
            self.xmax = guess[0] + 2 * image.shape[1]
            self.ymin = guess[1] - 2 * image.shape[0]
            self.ymax = guess[1] + 2 * image.shape[0]
            
        else:
            self.xmin = kwargs.get("xmin", 0)
            self.xmax = kwargs.get("xmax", SCREEN_WIDTH)
            self.ymin = kwargs.get("ymin", 0)
            self.ymax = kwargs.get("ymax", SCREEN_HEIGHT)
            
    def canny(self):
        if self._canny is None:
            self._canny = Template(super(Template, self).canny(), tolerance = self.tolerance, **self.kwargs)
        return self._canny
   
    def gray(self):
        if self._gray is None:
            self._gray = Template(super(Template, self).gray(), tolerance = self.tolerance, **self.kwargs)
        return self._gray
    
    def negative(self):
        if self._negative is None:
            self._negative = Template(super(Template, self).negative(), tolerance = self.tolerance, **self.kwargs)
        return self._negative
    
    def green(self):
        if self._green is None:
            self._green = Template(super(Template, self).green(), tolerance = self.tolerance, **self.kwargs)
        return self._green
        
    def scale(self, factor):
        if factor not in self._scale:
            self._scale[factor] = Template(super(Template, self).scale(factor), tolerance = self.tolerance, **self.kwargs)
        return self._scale[factor] 
        
            
def get_max_loc(ar):
    return np.unravel_index(ar.argmax(), ar.shape)
            
def read_image(filename):
    return cv.imread(filename, cv.IMREAD_UNCHANGED)
            
def search(image, template, guess = None, method = None):
    """returns the best match as the centre of the match and the confidence"""
    height, width = image.shape[:2]
    if guess is None:
        xmin = max(template.xmin, 0)
        xmax = min(template.xmax, image.shape[1])
        ymin = max(template.ymin, 0)
        ymax = min(template.ymax, image.shape[0])
    else:
        xmin = max(guess[0] - template.shape[1]/2, 0)
        xmax = max(guess[0] + template.shape[1]/2, 0)
        ymin = min(guess[1] - template.shape[0]/2, image.shape[0])
        ymax = min(guess[1] + template.shape[0]/2, image.shape[1])
    im = image.im[ymin : ymax, xmin : xmax]
    x, y, confidence = _search_ar(im, template.im, method = method)
    x = x + xmin + template.shape[1]/2
    y = y + ymin + template.shape[0]/2
    return x , y, confidence

def _search_ar(image, template, method):
    if method is None:
        method = cv.TM_CCORR_NORMED
    similarity = cv.matchTemplate(image, template, method = method)
    y, x = get_max_loc(similarity)
    confidence = similarity.max()
    return x, y, confidence

def search_all(image, template, guess = None, tolerance = 0.7, method = None):
    """returns the best match as the centre of the match and the confidence"""
    if method is None:
        method = cv.TM_CCORR_NORMED
    height, width = image.shape[:2]
    if guess is None:
        xmin = max(template.xmin, 0)
        xmax = min(template.xmax, image.shape[1])
        ymin = max(template.ymin, 0)
        ymax = min(template.ymax, image.shape[0])
    else:
        xmin = max(guess[0] - template.shape[1]/2, 0)
        xmax = max(guess[0] + template.shape[1]/2, 0)
        ymin = min(guess[1] - template.shape[0]/2, image.shape[0])
        ymax = min(guess[1] + template.shape[0]/2, image.shape[1])
    im = image.im[ymin : ymax, xmin : xmax]
    similarity = cv.matchTemplate(im, template.im, method = method)
    similarity[similarity < tolerance] = 0
    locs = []
    while similarity.max() > 0:
        y, x = get_max_loc(similarity)
        locs.append({"x": x + xmin + template.shape[1]/2,
                     "y": y + ymin + template.shape[0]/2,
                     "confidence": similarity.max()
        })
        similarity[max(0, y - template.shape[0]/2): min(similarity.shape[0], y + template.shape[0]/2),
                   max(0, x - template.shape[1]/2): min(similarity.shape[1], x + template.shape[1]/2)] = 0
    return locs
        
    
    
    
    
    