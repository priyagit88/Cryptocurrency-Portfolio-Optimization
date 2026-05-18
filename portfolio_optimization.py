import tkinter as tk
from tkinter import ttk, messagebox
import time
from core_logic import Asset, PortfolioOptimizer
from components import PortfolioSummaryFrame
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore

class PortfolioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Portfolio Optimizer Pro Dashboard")
        self.root.geometry("1300x900")
        
        # State Variables
        self.assets = []
        self.last_dp_table = None
        self.last_dp_path = None
        self.last_dp_assets = None
        self.last_dp_W = 0
        self.last_dp_scale = 1
        self.last_dp_return = 0.0
        self.chart_results = {"DP": 0.0, "Greedy": 0.0, "B&B": 0.0}

        # GUI Variables (Explicit separation to fix leaks)
        self.budget_var = tk.StringVar(value="600")
        self.name_var = tk.StringVar(value="")
        self.cost_var = tk.StringVar(value="")
        self.return_var = tk.StringVar(value="")
        
        self._setup_style()
        self._create_widgets()
        
        # Auto-run for immediate feedback
        self.load_demo_data()
        self.run_all()

    def _setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.bg_color = "#121212"
        self.card_bg = "#1e1e1e"
        self.accent_color = "#00adb5"
        self.root.configure(bg=self.bg_color)
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground="#eeeeee", font=('Segoe UI', 10))
        self.style.configure("Header.TLabel", font=('Segoe UI', 20, 'bold'), foreground=self.accent_color)
        self.style.configure("Card.TLabelframe", background=self.card_bg, foreground=self.accent_color, relief="flat")
        self.style.configure("Card.TLabelframe.Label", background=self.bg_color, foreground=self.accent_color, font=('Segoe UI', 11, 'bold'))
        
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.card_bg, foreground="white", padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)])

        self.style.configure("Treeview", background="#2d2d2d", foreground="white", fieldbackground="#2d2d2d", borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent_color)])
        self.style.configure("Treeview.Heading", background="#393e46", foreground="white", font=('Segoe UI', 10, 'bold'))
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white", font=('Segoe UI', 10, 'bold'))

    def _create_widgets(self):
        ttk.Label(self.root, text="Cryptocurrency Portfolio Optimization Dashboard", style="Header.TLabel").pack(pady=15)
        self.notebook = ttk.Notebook(self.root); self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # TAB 1: DASHBOARD
        tab1 = ttk.Frame(self.notebook); self.notebook.add(tab1, text=" Dashboard ")
        
        # Scrollable container
        self.dash_canvas = tk.Canvas(tab1, bg=self.bg_color, highlightthickness=0)
        dash_scroll = ttk.Scrollbar(tab1, orient="vertical", command=self.dash_canvas.yview)
        self.dash_canvas.configure(yscrollcommand=dash_scroll.set)
        dash_scroll.pack(side="right", fill="y"); self.dash_canvas.pack(side="left", fill="both", expand=True)
        
        self.dash_frm = ttk.Frame(self.dash_canvas)
        self.dash_win = self.dash_canvas.create_window((0, 0), window=self.dash_frm, anchor="nw")
        self.dash_frm.bind("<Configure>", lambda e: self.dash_canvas.configure(scrollregion=self.dash_canvas.bbox("all")))
        self.dash_canvas.bind("<Configure>", lambda e: self.dash_canvas.itemconfig(self.dash_win, width=e.width))
        self.dash_canvas.bind_all("<MouseWheel>", lambda e: self.dash_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        content = ttk.Frame(self.dash_frm); content.pack(fill="both", expand=True, padx=20, pady=10)
        left = ttk.Frame(content); left.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Config Panel
        p1 = ttk.LabelFrame(left, text=" Configuration ", style="Card.TLabelframe", padding=15); p1.pack(fill="x", pady=(0, 15))
        ttk.Label(p1, text="Budget ($):").grid(row=0, column=0); ttk.Entry(p1, textvariable=self.budget_var, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(p1, text="Load Demo", command=self.load_demo_data).grid(row=0, column=2, padx=5)
        ttk.Button(p1, text="Clear", command=self.clear_assets).grid(row=0, column=3, padx=5)

        # Add Panel
        p2 = ttk.LabelFrame(left, text=" Add Asset ", style="Card.TLabelframe", padding=15); p2.pack(fill="x", pady=(0, 15))
        ttk.Label(p2, text="Name:").grid(row=0, column=0); ttk.Entry(p2, textvariable=self.name_var, width=15).grid(row=0, column=1)
        ttk.Label(p2, text="Cost:").grid(row=0, column=2); ttk.Entry(p2, textvariable=self.cost_var, width=10).grid(row=0, column=3)
        ttk.Label(p2, text="Ret:").grid(row=0, column=4); ttk.Entry(p2, textvariable=self.return_var, width=10).grid(row=0, column=5)
        ttk.Button(p2, text="+ Add", command=self.add_asset).grid(row=0, column=6, padx=5)

        # Inventory Table
        p3 = ttk.LabelFrame(left, text=" Asset Inventory ", style="Card.TLabelframe", padding=15); p3.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(p3, columns=("N", "C", "R", "E"), show="headings", height=8)
        for c, h in zip(("N", "C", "R", "E"), ("Name", "Cost ($)", "Return ($)", "Efficiency (R/C)")):
            self.tree.heading(c, text=h); self.tree.column(c, width=90, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.summary = PortfolioSummaryFrame(left, self.bg_color, self.card_bg, self.accent_color, "#eeeeee"); self.summary.pack(fill="x", pady=(15,0))

        # Right Col
        right = ttk.Frame(content); right.pack(side="right", fill="both", expand=True, padx=(15, 0))
        p4 = ttk.LabelFrame(right, text=" Optimization Engine ", style="Card.TLabelframe", padding=15); p4.pack(fill="x", pady=(0, 15))
        ttk.Button(p4, text="Run Comprehensive Analysis", command=self.run_all, style="Accent.TButton").pack(fill="x", pady=(0, 10))
        bg = ttk.Frame(p4); bg.pack(fill="x")
        ttk.Button(bg, text="DP", command=self.run_dp).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(bg, text="Greedy", command=self.run_greedy).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(bg, text="B&B", command=self.run_bb).pack(side="left", expand=True, fill="x", padx=2)
        self.v_dp_btn = ttk.Button(p4, text="View DP Matrix Graph", command=self.show_dp_table_window); self.v_dp_btn.pack(pady=5)

        # Result Matrix
        p5 = ttk.LabelFrame(right, text=" Comparison Matrix ", style="Card.TLabelframe", padding=15); p5.pack(fill="x", pady=(0, 15))
        self.comp = ttk.Treeview(p5, columns=("S", "V", "T", "N"), show="headings", height=3)
        for c, h in zip(("S", "V", "T", "N"), ("Strategy", "Return ($)", "Time", "Note")):
            self.comp.heading(c, text=h); self.comp.column(c, width=100, anchor="center")
        self.comp.pack(fill="x")

        # CEX Panel
        p6 = ttk.LabelFrame(right, text=" Greedy Failure Proof ", style="Card.TLabelframe", padding=15); p6.pack(fill="x", pady=(0, 15))
        ttk.Button(p6, text="Load 0/1 Greedy vs DP Demo", command=self.load_counterexample).pack(anchor="w")
        self.cex_t = tk.StringVar(value="Load demo..."); ttk.Label(p6, textvariable=self.cex_t, font=('Consolas', 9)).pack(fill="x", pady=5)
        self.cex_w = tk.StringVar(); tk.Label(p6, textvariable=self.cex_w, font=('Segoe UI', 10, 'bold'), fg="#00ff00", bg=self.card_bg).pack(anchor="w")
        ttk.Label(p6, text="Note: Greedy picks high ratio Q (2.0) but DP captures R+P combinatorially", foreground="#888888", font=('Segoe UI', 9, 'italic')).pack(anchor="w")

        # Log Panel
        p7 = ttk.LabelFrame(right, text=" Execution Logs ", style="Card.TLabelframe", padding=15); p7.pack(fill="both", expand=True)
        self.logs = tk.Text(p7, height=10, bg="#2d2d2d", fg="white", font=('Consolas', 9), state='disabled', borderwidth=0); self.logs.pack(fill="both", expand=True)

        # TAB 2: ANALYSIS
        tab2 = ttk.Frame(self.notebook); self.notebook.add(tab2, text=" Charts & Analysis ")
        self.fig = Figure(figsize=(8, 4), facecolor='#121212')
        self.ax = self.fig.add_subplot(111); self.ax.set_facecolor('#1e1e1e')
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=tab2)
        self.canvas_chart.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
        self.update_chart()

    def update_chart(self):
        self.ax.clear(); self.ax.set_facecolor('#1e1e1e')
        algs = ['DP', 'Greedy (0/1)', 'B&B']; vals = [self.chart_results["DP"], self.chart_results["Greedy"], self.chart_results["B&B"]]
        colors = ['#00adb5', '#FFB300', '#9c27b0']
        bars = self.ax.bar(algs, vals, color=colors, width=0.5)
        for b, v in zip(bars, vals):
            self.ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'${v:.1f}', ha='center', color='white', fontweight='bold')
        self.ax.set_title('Algorithm Performance Benchmark', color='white', pad=20)
        self.ax.set_ylabel('Max Return ($)', color='#00adb5'); self.ax.tick_params(colors='white')
        self.fig.tight_layout(); self.canvas_chart.draw()

    def run_all(self): self.run_dp(); self.run_greedy(); self.run_bb()

    def load_demo_data(self):
        # Demo dataset chosen to provide 0/1 vs Fractional difference
        self.budget_var.set("600")
        self.assets = [Asset("Bitcoin (A)", 400, 1000), Asset("Ethereum (B)", 500, 1100), Asset("Solana (C)", 200, 400)]
        self.refresh(); self._log("Demo dataset loaded (600 budget).")

    def load_counterexample(self):
        self.assets = [Asset("P", 1, 1), Asset("Q", 2, 4), Asset("R", 3, 5)]; self.budget_var.set("4")
        self.refresh(); opt = PortfolioOptimizer(4, self.assets)
        g_v, _, _ = opt.greedy_01(); dp_v, _, _, _, _, _ = opt.dynamic_programming()
        self.cex_t.set(f"Greedy 0/1 Total: ${g_v} | DP Total: ${dp_v}")
        self.cex_w.set(f"DP Efficiency Win: +${dp_v - g_v}")
        self.run_all()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for a in self.assets: self.tree.insert("", "end", values=(a.name, f"${a.cost:.1f}", f"${a.expected_return:.1f}", f"{a.ratio:.2f}"))

    def clear_assets(self): self.assets = []; self.refresh(); self.chart_results = {"DP":0,"Greedy":0,"B&B":0}; self.update_chart()

    def add_asset(self):
        try:
            n = self.name_var.get(); c = float(self.cost_var.get()); r = float(self.return_var.get())
            if n and c > 0: self.assets.append(Asset(n, c, r)); self.refresh(); self.name_var.set(""); self.cost_var.set(""); self.return_var.set("")
        except: messagebox.showerror("Error", "Check Asset Inputs")

    def _log(self, m): self.logs.config(state='normal'); self.logs.insert(tk.END, f"> {m}\n"); self.logs.see(tk.END); self.logs.config(state='disabled')

    def run_dp(self):
        try:
            b = float(self.budget_var.get()); opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, ch, t, tbl, p, s = opt.dynamic_programming()
                self.last_dp_table = tbl; self.last_dp_path = p; self.last_dp_assets = opt.assets[:]; self.last_dp_W = int(b * s); self.last_dp_scale = s; self.last_dp_return = v
                self._update_matrix("DP (0/1)", v, t); self.summary.update_summary(ch, v, b); self.chart_results["DP"] = v; self.update_chart(); self._log(f"DP Result: ${v:.1f}")
        except Exception as e: self._log(f"DP Error: {e}")

    def run_greedy(self):
        try:
            b = float(self.budget_var.get()); opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, al, t = opt.greedy_fractional()
                self._update_matrix("Greedy (Frac)", v, t, "Approx")
                self.summary.update_summary(al, v, b); self._log(f"Greedy (Frac) Result: ${v:.1f}")
                # Use 0/1 Greedy version for chart to maintain apples-to-apples 0/1 comparison
                g01_v, _, _ = opt.greedy_01(); self.chart_results["Greedy"] = g01_v; self.update_chart()
        except Exception as e: self._log(f"Greedy Error: {e}")

    def run_bb(self):
        try:
            b = float(self.budget_var.get()); opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, ch, t = opt.branch_and_bound()
                self._update_matrix("B&B (0/1)", v, t); self.summary.update_summary(ch, v, b); self.chart_results["B&B"] = v; self.update_chart(); self._log(f"B&B Result: ${v:.1f}")
        except Exception as e: self._log(f"B&B Error: {e}")

    def _update_matrix(self, s, v, t, n="Optimal"):
        for i in self.comp.get_children():
            if self.comp.item(i)['values'][0] == s: self.comp.delete(i)
        self.comp.insert("", "end", values=(s, f"${v:.1f}", f"{t*1000:.1f}ms", n))

    def show_dp_table_window(self):
        if not self.last_dp_table:
            messagebox.showwarning("Incomplete", "Run DP algorithm first to generate matrix.")
            return
        tbl = self.last_dp_table; p_set = set(self.last_dp_path); assets = self.last_dp_assets
        W = self.last_dp_W; n = len(assets); v = self.last_dp_return; win = tk.Toplevel(self.root)
        win.title(f"DP State Transition Graph - Return: ${v:.1f}"); win.geometry("1000x700"); win.configure(bg=self.bg_color)
        cols = list(range(0, W+1, max(1, W//100)))
        if W not in cols: cols.append(W)
        c_p = ttk.Frame(win); c_p.pack(fill="both", expand=True, padx=20, pady=20)
        cnv = tk.Canvas(c_p, bg=self.bg_color, highlightthickness=0); vs = ttk.Scrollbar(c_p, orient="vertical", command=cnv.yview)
        hs = ttk.Scrollbar(win, orient="horizontal", command=cnv.xview); frm = tk.Frame(cnv, bg=self.bg_color)
        frm.bind("<Configure>", lambda e: cnv.configure(scrollregion=cnv.bbox("all"))); cnv.create_window((0,0), window=frm, anchor="nw")
        cnv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set); cnv.bind_all("<MouseWheel>", lambda e: cnv.yview_scroll(int(-1*(e.delta/120)),"units"))
        for idx, w in enumerate(cols): tk.Label(frm, text=f"w={w}", bg="#008080", fg="white", width=8).grid(row=0, column=idx+1)
        for i in range(n+1):
            nm = assets[i-1].name if i>0 else "Base"; tk.Label(frm, text=nm, bg="#008080", fg="white", width=25, anchor="w", padx=10).grid(row=i+1, column=0)
            for idx, w in enumerate(cols):
                is_p = (i,w) in p_set; bg = "#FFB300" if is_p else "#1a1a2e"; fg = "black" if is_p else "white"
                tk.Label(frm, text=f"{tbl[i][w]:.0f}"+(" *" if is_p else ""), bg=bg, fg=fg, width=8).grid(row=i+1, column=idx+1, padx=1, pady=1)
        cnv.pack(side="left", fill="both", expand=True); vs.pack(side="right", fill="y"); hs.pack(fill="x", padx=20)
        ttk.Button(win, text="Dismiss Visualization", command=win.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk(); app = PortfolioGUI(root); root.mainloop()
