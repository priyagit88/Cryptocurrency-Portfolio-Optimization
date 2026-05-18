import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
from matplotlib.figure import Figure
import tkinter as tk

class comparisonChart:
    def __init__(self, parent, bg_color):
        self.bg_color = bg_color
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=bg_color)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(bg_color)
        
        # Initial chart setup
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=bg_color)
        
        self.labels = ['DP', 'Greedy', 'B&B']
        self.colors = ['#00adb5', '#ffb300', '#9b59b6'] # Teal, Amber, Purple
        
        self.update_chart([0, 0, 0])

    def update_chart(self, results):
        self.ax.clear()
        self.ax.set_facecolor(self.bg_color)
        
        bars = self.ax.bar(self.labels, results, color=self.colors)
        
        # Styling
        self.ax.set_title("Algorithm Return Comparison", color='white', fontsize=12, pad=15)
        self.ax.set_ylabel("Max Return ($)", color='white')
        self.ax.tick_params(colors='white')
        
        # Spines color
        for spine in self.ax.spines.values():
            spine.set_color('#393e46')
        
        # Add labels on top
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'${height:.1f}', ha='center', va='bottom', color='white', fontweight='bold')
        
        self.fig.tight_layout()
        self.canvas.draw()

    def get_widget(self):
        return self.canvas_widget
