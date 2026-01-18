import tkinter as tk
from gui.main_window import Graph3DApp

def main():
    root = tk.Tk()
    app = Graph3DApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()