import scipy
import numpy as np

class LinearCurve:
    def __init__(self, points):
        points = np.array(points)

        self.x = points.transpose()[0]
        self.y = points.transpose()[1]

        self.interpolation = scipy.interpolate.interp1d(self.x, self.y)

    def evaluate(self, length=None):
        if length is None:
            length = int(round(self.x[-1]))

        return self.interpolation(np.linspace(0, self.x[-1], length))

class CubicCurve:
    def __init__(self, points):
        points = np.array(points)

        self.x = points.transpose()[0]
        self.y = points.transpose()[1]

        self.interpolation = scipy.interpolate.CubicSpline(self.x, self.y)

    def evaluate(self, length=None):
        if length is None:
            length = int(round(self.x[-1]))

        return self.interpolation(np.linspace(0, self.x[-1], length))