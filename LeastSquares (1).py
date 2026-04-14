# region imports
import numpy as np
# endregion

# region class definitions
class LeastSquaresFit_Class():
    def __init__(self, xdata=None, ydata=None):
        self.x = xdata if xdata is not None else np.array([])
        self.y = ydata if ydata is not None else np.array([])
        self.coeffs = np.array([])

    def RSquared(self, a):
        AvgY = np.mean(self.y)
        SSTot = 0
        SSRes = 0
        for i in range(len(self.y)):
            SSTot += (self.y[i] - AvgY) ** 2
            SSRes += (self.y[i] - self.Poly(self.x[i], a)) ** 2
        RSq = 1 - SSRes / SSTot
        return RSq

    def Poly(self, xval, a):
        p = np.poly1d(a)
        return p(xval)

    def LeastSquares(self, power):
        self.coeffs = np.polyfit(self.x, self.y, power)
        return self.coeffs

    def GetCoeffsString(self):
        s = ''
        n = 0
        for c in self.coeffs:
            s += ('' if n == 0 else ', ') + "{:0.4f}".format(c)
            n += 1
        return s

    def GetPlotInfo(self, power, npoints=500):
        Xmin = min(self.x)
        Xmax = max(self.x)
        dX = 1.0 * (Xmax - Xmin) / npoints
        a = self.LeastSquares(power)
        xvals = []
        yvals = []
        for i in range(npoints):
            xvals.append(Xmin + i * dX)
            yvals.append(self.Poly(xvals[i], a))
        RSq = self.RSquared(a)
        return xvals, yvals, RSq
# endregion
