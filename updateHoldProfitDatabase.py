

from tkinter import Tk, filedialog
from DataManagement.Database.HoldProfitTable import updateHoldProfitTable


if __name__ == "__main__":
    root = Tk()
    filenames = list(filedialog.askopenfilenames(parent=root, title='Choose a file'))
    root.withdraw() # make window go away 
    updateHoldProfitTable(filenames)