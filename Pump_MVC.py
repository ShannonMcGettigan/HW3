# region imports
import numpy as np
import PyQt5.QtWidgets as qtw
from LeastSquares import LeastSquaresFit_Class
# endregion

# region class definitions
## chatgpt assisted in code creation ##
class Pump_Model():
    """
    Stores all pump data. Pure data — no logic, no display.
    """
    def __init__(self):
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData  = np.array([])

        self.HeadCoefficients       = np.array([])
        self.EfficiencyCoefficients = np.array([])

        # Two least-squares fit objects
        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff  = LeastSquaresFit_Class()


class Pump_Controller():
    def __init__(self):
        self.Model = Pump_Model()
        self.View  = Pump_View()

    # ------------------------------------------------------------------
    # Methods that modify the Model
    # ------------------------------------------------------------------
    def ImportFromFile(self, data):
        """
        Parse the list of strings that make up the pump data file.

        Expected file format
        --------------------
        Line 0:  pump name  (e.g. "1/2 horsepower, 3450 rpm")
        Line 1:  column headers  (ignored – e.g. "flow head efficiency")
        Line 2:  units  (e.g. "gpm ft %")
        Lines 3+: numeric data rows  (flow  head  efficiency)
        """
        # Line 0 – pump name (strip trailing newline / whitespace)
        self.Model.PumpName = data[0].strip()

        # Line 2 – units (split on whitespace)
        units = data[2].split()
        self.Model.FlowUnits = units[0]   # e.g. "gpm"
        self.Model.HeadUnits = units[1]   # e.g. "ft"
        # units[2] would be the efficiency unit ("%"), stored implicitly

        # Lines 3 onward – numeric data
        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        """
        Parse rows of whitespace-delimited numeric data and build arrays.
        Each row: flow  head  efficiency
        """
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData  = np.array([])

        for line in data:
            line = line.strip()
            if not line:          # skip blank lines
                continue
            cells = line.split()  # split on whitespace
            self.Model.FlowData = np.append(self.Model.FlowData, float(cells[0]))
            self.Model.HeadData = np.append(self.Model.HeadData, float(cells[1]))
            self.Model.EffData  = np.append(self.Model.EffData,  float(cells[2]))

        self.LSFit()

    def LSFit(self):
        """Fit polynomials: quadratic for Head, cubic for Efficiency."""
        # Head – quadratic (degree 2)
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(2)

        # Efficiency – cubic (degree 3)
        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)

    # ------------------------------------------------------------------
    # Methods that interact with the View
    # ------------------------------------------------------------------
    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)


class Pump_View():
    def __init__(self):
        # Placeholder widgets until the real ones are passed in
        self.LE_PumpName  = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs  = qtw.QLineEdit()
        self.ax     = None
        self.canvas = None

    def setViewWidgets(self, w):
        (self.LE_PumpName,
         self.LE_FlowUnits,
         self.LE_HeadUnits,
         self.LE_HeadCoefs,
         self.LE_EffCoefs,
         self.ax,
         self.canvas) = w

    def updateView(self, Model):
        """Populate all output widgets from the Model."""
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """
        Draw the pump head (left y-axis) and efficiency (right y-axis) curves
        on the shared matplotlib axes that live inside the Qt canvas.
        """
        # Get smooth curve data + R² values
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(2, npoints=500)
        effx,  effy,  effRSq  = Model.LSFitEff.GetPlotInfo(3,  npoints=500)

        ax1 = self.ax
        ax1.clear()

        # --- Primary axis: Head ---
        ax1.set_xlabel(f'Flow Rate ({Model.FlowUnits})')
        ax1.set_ylabel(f'Head ({Model.HeadUnits})', color='black')

        # Scatter – raw head data
        head_scatter = ax1.scatter(Model.FlowData, Model.HeadData,
                                   marker='o', color='black', zorder=5,
                                   label='Head')
        # Curve – fitted head
        head_line, = ax1.plot(headx, heady,
                              linestyle='--', color='black',
                              label=f'Head($R^2$={headRSq:.3f})')

        # --- Secondary axis: Efficiency ---
        ax2 = ax1.twinx()
        ax2.set_ylabel('Efficiency (%)', color='black')

        # Scatter – raw efficiency data
        eff_scatter = ax2.scatter(Model.FlowData, Model.EffData,
                                  marker='^', color='black', zorder=5,
                                  label='Efficiency')
        # Curve – fitted efficiency
        eff_line, = ax2.plot(effx, effy,
                             linestyle=':', color='black',
                             label=f'Efficiency($R^2$={effRSq:.3f})')

        # --- Title ---
        ax1.set_title('Pump Head and Efficiency Curves')

        # --- Combined legend (both axes) ---
        handles = [head_line, head_scatter, eff_line, eff_scatter]
        ax1.legend(handles=handles, loc='upper right')

        # Redraw the canvas
        self.canvas.draw()

# endregion
