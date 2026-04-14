# region imports
import sys
import os
from pathlib import Path

import PyQt5.QtWidgets as qtw
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pump import Ui_Form          # generated UI class
from Pump_MVC import Pump_Controller
# endregion

# region class definitions

class PumpCurve_GUI_Class(Ui_Form, qtw.QWidget):
    """
    Main window.  Inherits layout from Ui_Form and event handling from
    QWidget.  Follows MVC: this class is only concerned with the GUI shell
    (signals, file dialog, passing data to the controller).
    """

    def __init__(self):
        super().__init__()          # runs QWidget.__init__ and Ui_Form.__init__
        self.setupUi(self)          # build all widgets defined in pump.py

        # Track the last-used directory so the dialog reopens there
        self.FilePath = os.getcwd()
        self.FileName = ""

        # --- Embed a matplotlib canvas inside the Output group box ---
        self.canvas = FigureCanvasQTAgg(
            Figure(figsize=(5, 3), tight_layout=True, frameon=True)
        )
        self.ax = self.canvas.figure.add_subplot(111)

        # Replace the W_Plot placeholder with the real canvas
        # (W_Plot was added at row 5, cols 0-3 in the grid layout)
        self.W_Plot.hide()
        self.GL_Output.addWidget(self.canvas, 5, 0, 1, 4)

        # --- Create controller and hand it the display widgets ---
        self.myPump = Pump_Controller()
        self.setViewWidgets()

        # --- Connect signals ---
        self.AssignSignals()

        self.show()

    # ------------------------------------------------------------------
    def AssignSignals(self):
        self.PB_Exit.clicked.connect(self.Exit)
        self.CMD_Open.clicked.connect(self.ReadAndCalculate)

    # ------------------------------------------------------------------
    def setViewWidgets(self):
        """Pass the output widgets to the controller → view."""
        w = [
            self.LE_PumpName,
            self.LE_FlowUnits,
            self.LE_HeadUnits,
            self.LE_HeadCoefs,
            self.LE_EffCoefs,
            self.ax,
            self.canvas,
        ]
        self.myPump.setViewWidgets(w)

    # ------------------------------------------------------------------
    def ReadAndCalculate(self):
        """
        Slot for the 'Read File and Calculate' button.
        Opens the file dialog, reads the file, hands data to the controller.
        """
        if self.OpenFile():
            with open(self.FileName, 'r') as f:
                data = f.readlines()
            self.myPump.ImportFromFile(data)

    # ------------------------------------------------------------------
    def OpenFile(self):
        """
        Open a QFileDialog starting at the last-used directory.
        Returns True if the user selected a file, False if they cancelled.
        """
        fname = qtw.QFileDialog.getOpenFileName(
            self,
            'Open Pump Data File',
            self.FilePath,
            'Text Files (*.txt);;All Files (*.*)'
        )

        success = len(fname[0]) > 0
        if success:
            self.FileName = fname[0]
            # Remember this directory for the next click
            self.FilePath = str(Path(fname[0]).parent) + '/'
            self.TE_Filename.setText(self.FileName)

        return success

    # ------------------------------------------------------------------
    def Exit(self):
        qapp.exit()

# endregion

# region main
def main():
    gui = PumpCurve_GUI_Class()
    qapp.exec_()

if __name__ == "__main__":
    qapp = qtw.QApplication(sys.argv)
    main()
# endregion
