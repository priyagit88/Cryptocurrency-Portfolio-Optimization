import tkinter as tk
from tkinter import ttk, messagebox
import time
from core_logic import Asset, PortfolioOptimizer
from components import PortfolioSummaryFrame
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
import customtkinter as ctk

class PortfolioGUI:
    def __init__(self, root):
        self.root = root
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root.title("Crypto Portfolio Optimizer Pro Dashboard")
        self.root.geometry("1300x820")
        
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
        self.bg_color = "#121212"
        self.card_bg = "#1e1e1e"
        self.accent_color = "#00adb5"
        self.root.configure(fg_color=self.bg_color)
        
        # Style standard ttk Treeview to fit CustomTkinter theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", 
                             background="#1e1e1e", 
                             foreground="white", 
                             fieldbackground="#1e1e1e", 
                             rowheight=38,
                             borderwidth=0, 
                             font=('Segoe UI', 14))
        self.style.map("Treeview", background=[('selected', self.accent_color)], foreground=[('selected', 'white')])
        self.style.configure("Treeview.Heading", 
                             background="#2d2d2d", 
                             foreground="white", 
                             relief="flat", 
                             font=('Segoe UI', 14, 'bold'))
        self.style.map("Treeview.Heading", background=[('active', '#3c3c3c')])

    def _create_widgets(self):
        # Title Header
        title_lbl = ctk.CTkLabel(
            self.root, 
            text="Cryptocurrency Portfolio Optimization Dashboard", 
            font=('Segoe UI', 24, 'bold'), 
            text_color=self.accent_color
        )
        title_lbl.pack(pady=8)
        
        # Notebook (Tabview)
        self.notebook = ctk.CTkTabview(
            self.root, 
            segmented_button_selected_color=self.accent_color,
            segmented_button_selected_hover_color="#008080",
            fg_color="transparent"
        )
        self.notebook.pack(fill="both", expand=True, padx=12, pady=5)
        
        self.notebook.add(" Dashboard ")
        self.notebook.add(" Charts & Analysis ")
        
        tab1 = self.notebook.tab(" Dashboard ")
        tab2 = self.notebook.tab(" Charts & Analysis ")

        # TAB 1: DASHBOARD
        # Scrollable container using CTkScrollableFrame
        self.dash_frm = ctk.CTkScrollableFrame(tab1, fg_color="transparent")
        self.dash_frm.pack(fill="both", expand=True)

        content = ctk.CTkFrame(self.dash_frm, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=4, pady=4)
        
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # Config Panel Card
        p1 = ctk.CTkFrame(left, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p1.pack(fill="x", pady=(0, 10))
        
        p1_title = ctk.CTkLabel(p1, text="CONFIGURATION", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p1_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        p1_controls = ctk.CTkFrame(p1, fg_color="transparent")
        p1_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        lbl_budget = ctk.CTkLabel(p1_controls, text="Budget ($):", font=('Segoe UI', 13))
        lbl_budget.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.budget_entry = ctk.CTkEntry(p1_controls, textvariable=self.budget_var, width=140)
        self.budget_entry.grid(row=0, column=1, padx=5)
        
        btn_load = ctk.CTkButton(p1_controls, text="Load Demo", fg_color="#333333", hover_color="#444444", text_color="white", width=90, font=('Segoe UI', 12, 'bold'), command=self.load_demo_data)
        btn_load.grid(row=0, column=2, padx=5)
        
        btn_clear = ctk.CTkButton(p1_controls, text="Clear", fg_color="#ff4b2b", hover_color="#d32f2f", text_color="white", width=90, font=('Segoe UI', 12, 'bold'), command=self.clear_assets)
        btn_clear.grid(row=0, column=3, padx=5)

        # Add Panel Card
        p2 = ctk.CTkFrame(left, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p2.pack(fill="x", pady=(0, 10))
        
        p2_title = ctk.CTkLabel(p2, text="ADD ASSET", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p2_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        p2_controls = ctk.CTkFrame(p2, fg_color="transparent")
        p2_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(p2_controls, text="Name:", font=('Segoe UI', 13)).grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.name_entry = ctk.CTkEntry(p2_controls, textvariable=self.name_var, width=140)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(p2_controls, text="Cost ($):", font=('Segoe UI', 13)).grid(row=0, column=2, padx=5, sticky="w")
        self.cost_entry = ctk.CTkEntry(p2_controls, textvariable=self.cost_var, width=120)
        self.cost_entry.grid(row=0, column=3, padx=5)
        
        ctk.CTkLabel(p2_controls, text="Return ($):", font=('Segoe UI', 13)).grid(row=0, column=4, padx=5, sticky="w")
        self.return_entry = ctk.CTkEntry(p2_controls, textvariable=self.return_var, width=120)
        self.return_entry.grid(row=0, column=5, padx=5)
        
        btn_add = ctk.CTkButton(p2_controls, text="+ Add", fg_color=self.accent_color, hover_color="#008080", text_color="white", width=90, font=('Segoe UI', 12, 'bold'), command=self.add_asset)
        btn_add.grid(row=0, column=6, padx=5)

        # Inventory Table Card
        p3 = ctk.CTkFrame(left, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p3.pack(fill="both", expand=True)
        
        p3_title = ctk.CTkLabel(p3, text="ASSET INVENTORY", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p3_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        tree_frame = ctk.CTkFrame(p3, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree = ttk.Treeview(tree_frame, columns=("N", "C", "R", "E"), show="headings", height=6, yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)
        
        for c, h in zip(("N", "C", "R", "E"), ("Name", "Cost ($)", "Return ($)", "Efficiency (R/C)")):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=100, anchor="center")
            
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        # Portfolio Summary Frame
        self.summary = PortfolioSummaryFrame(left, self.bg_color, self.card_bg, self.accent_color, "#eeeeee")
        self.summary.pack(fill="x", pady=(10, 0))

        # Right Column
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))
        
        # Optimization Engine Card
        p4 = ctk.CTkFrame(right, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p4.pack(fill="x", pady=(0, 10))
        
        p4_title = ctk.CTkLabel(p4, text="OPTIMIZATION ENGINE", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p4_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        p4_body = ctk.CTkFrame(p4, fg_color="transparent")
        p4_body.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_run_all = ctk.CTkButton(
            p4_body, 
            text="Run Comprehensive Analysis", 
            fg_color=self.accent_color, 
            hover_color="#008080", 
            text_color="white", 
            font=('Segoe UI', 14, 'bold'),
            command=self.run_all
        )
        btn_run_all.pack(fill="x", pady=(0, 6))
        
        bg = ctk.CTkFrame(p4_body, fg_color="transparent")
        bg.pack(fill="x", pady=(0, 6))
        
        btn_dp = ctk.CTkButton(bg, text="DP", fg_color="#333333", hover_color="#444444", text_color="white", font=('Segoe UI', 13, 'bold'), command=self.run_dp)
        btn_dp.pack(side="left", expand=True, fill="x", padx=2)
        
        btn_greedy = ctk.CTkButton(bg, text="Greedy", fg_color="#333333", hover_color="#444444", text_color="white", font=('Segoe UI', 13, 'bold'), command=self.run_greedy)
        btn_greedy.pack(side="left", expand=True, fill="x", padx=2)
        
        btn_bb = ctk.CTkButton(bg, text="B&B", fg_color="#333333", hover_color="#444444", text_color="white", font=('Segoe UI', 13, 'bold'), command=self.run_bb)
        btn_bb.pack(side="left", expand=True, fill="x", padx=2)
        
        self.v_dp_btn = ctk.CTkButton(
            p4_body, 
            text="View DP Matrix Graph", 
            fg_color="#4b6584", 
            hover_color="#3b5998", 
            text_color="white", 
            font=('Segoe UI', 13, 'bold'),
            command=self.show_dp_table_window
        )
        self.v_dp_btn.pack(fill="x")

        # Result Matrix Card
        p5 = ctk.CTkFrame(right, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p5.pack(fill="x", pady=(0, 10))
        
        p5_title = ctk.CTkLabel(p5, text="COMPARISON MATRIX", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p5_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        comp_frame = ctk.CTkFrame(p5, fg_color="transparent")
        comp_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.comp = ttk.Treeview(comp_frame, columns=("S", "V", "T", "N"), show="headings", height=3)
        for c, h in zip(("S", "V", "T", "N"), ("Strategy", "Return ($)", "Time", "Note")):
            self.comp.heading(c, text=h)
            self.comp.column(c, width=100, anchor="center")
        self.comp.pack(fill="x")

        # CEX Panel Card
        p6 = ctk.CTkFrame(right, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p6.pack(fill="x", pady=(0, 10))
        
        p6_title = ctk.CTkLabel(p6, text="GREEDY FAILURE PROOF DEMO", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p6_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        p6_body = ctk.CTkFrame(p6, fg_color="transparent")
        p6_body.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_cex = ctk.CTkButton(
            p6_body, 
            text="Load 0/1 Greedy vs DP Demo", 
            fg_color="#333333", 
            hover_color="#444444", 
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command=self.load_counterexample
        )
        btn_cex.pack(anchor="w", pady=(0, 6))
        
        self.cex_t = tk.StringVar(value="Load demo...")
        lbl_cex_t = ctk.CTkLabel(p6_body, textvariable=self.cex_t, font=('Consolas', 13), anchor="w")
        lbl_cex_t.pack(fill="x", pady=2)
        
        self.cex_w = tk.StringVar()
        lbl_cex_w = ctk.CTkLabel(p6_body, textvariable=self.cex_w, font=('Segoe UI', 14, 'bold'), text_color="#00ff00", anchor="w")
        lbl_cex_w.pack(anchor="w", pady=2)
        
        lbl_cex_note = ctk.CTkLabel(
            p6_body, 
            text="Note: Greedy picks high ratio Q (2.0) but DP captures R+P combinatorially", 
            text_color="#888888", 
            font=('Segoe UI', 12, 'italic'),
            anchor="w"
        )
        lbl_cex_note.pack(anchor="w", pady=(3, 0))

        # Log Panel Card
        p7 = ctk.CTkFrame(right, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2d2d2d")
        p7.pack(fill="both", expand=True)
        
        p7_title = ctk.CTkLabel(p7, text="EXECUTION LOGS", font=('Segoe UI', 13, 'bold'), text_color=self.accent_color)
        p7_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        self.logs = ctk.CTkTextbox(
            p7, 
            fg_color="#1e1e1e", 
            text_color="white", 
            font=('Consolas', 13), 
            state='disabled', 
            border_width=0,
            corner_radius=8
        )
        self.logs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # TAB 2: ANALYSIS
        tab2_frm = ctk.CTkFrame(tab2, fg_color="transparent")
        tab2_frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.fig = Figure(figsize=(8, 4), facecolor='#121212')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=tab2_frm)
        self.canvas_chart.get_tk_widget().pack(fill='both', expand=True)
        self.update_chart()

    def update_chart(self):
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        algs = ['DP', 'Greedy (0/1)', 'B&B']
        vals = [self.chart_results["DP"], self.chart_results["Greedy"], self.chart_results["B&B"]]
        colors = ['#00adb5', '#FFB300', '#9c27b0']
        bars = self.ax.bar(algs, vals, color=colors, width=0.5)
        for b, v in zip(bars, vals):
            self.ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'${v:.1f}', ha='center', color='white', fontweight='bold')
        self.ax.set_title('Algorithm Performance Benchmark', color='white', pad=20)
        self.ax.set_ylabel('Max Return ($)', color='#00adb5')
        self.ax.tick_params(colors='white')
        
        # Grid and spine details
        for spine in self.ax.spines.values():
            spine.set_color('#333333')
        self.ax.grid(True, linestyle='--', alpha=0.1, color='white')
        
        self.fig.tight_layout()
        self.canvas_chart.draw()

    def run_all(self): 
        self.run_dp()
        self.run_greedy()
        self.run_bb()

    def load_demo_data(self):
        # Demo dataset chosen to provide 0/1 vs Fractional difference
        self.budget_var.set("600")
        self.assets = [Asset("Bitcoin (A)", 400, 1000), Asset("Ethereum (B)", 500, 1100), Asset("Solana (C)", 200, 400)]
        self.refresh()
        self._log("Demo dataset loaded (600 budget).")

    def load_counterexample(self):
        self.assets = [Asset("P", 1, 1), Asset("Q", 2, 4), Asset("R", 3, 5)]
        self.budget_var.set("4")
        self.refresh()
        opt = PortfolioOptimizer(4, self.assets)
        g_v, _, _ = opt.greedy_01()
        dp_v, _, _, _, _, _ = opt.dynamic_programming()
        self.cex_t.set(f"Greedy 0/1 Total: ${g_v} | DP Total: ${dp_v}")
        self.cex_w.set(f"DP Efficiency Win: +${dp_v - g_v}")
        self.run_all()

    def refresh(self):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        for a in self.assets: 
            self.tree.insert("", "end", values=(a.name, f"${a.cost:.1f}", f"${a.expected_return:.1f}", f"{a.ratio:.2f}"))

    def clear_assets(self): 
        self.assets = []
        self.refresh()
        self.chart_results = {"DP": 0, "Greedy": 0, "B&B": 0}
        self.update_chart()

    def add_asset(self):
        try:
            n = self.name_var.get()
            c = float(self.cost_var.get())
            r = float(self.return_var.get())
            if n and c > 0: 
                self.assets.append(Asset(n, c, r))
                self.refresh()
                self.name_var.set("")
                self.cost_var.set("")
                self.return_var.set("")
        except: 
            messagebox.showerror("Error", "Check Asset Inputs")

    def _log(self, m): 
        self.logs.configure(state='normal')
        self.logs.insert(tk.END, f"> {m}\n")
        self.logs.see(tk.END)
        self.logs.configure(state='disabled')

    def run_dp(self):
        try:
            b = float(self.budget_var.get())
            opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, ch, t, tbl, p, s = opt.dynamic_programming()
                self.last_dp_table = tbl
                self.last_dp_path = p
                self.last_dp_assets = opt.assets[:]
                self.last_dp_W = int(b * s)
                self.last_dp_scale = s
                self.last_dp_return = v
                self._update_matrix("DP (0/1)", v, t)
                self.summary.update_summary(ch, v, b)
                self.chart_results["DP"] = v
                self.update_chart()
                self._log(f"DP Result: ${v:.1f}")
        except Exception as e: 
            self._log(f"DP Error: {e}")

    def run_greedy(self):
        try:
            b = float(self.budget_var.get())
            opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, al, t = opt.greedy_fractional()
                self._update_matrix("Greedy (Frac)", v, t, "Approx")
                self.summary.update_summary(al, v, b)
                self._log(f"Greedy (Frac) Result: ${v:.1f}")
                # Use 0/1 Greedy version for chart to maintain apples-to-apples 0/1 comparison
                g01_v, _, _ = opt.greedy_01()
                self.chart_results["Greedy"] = g01_v
                self.update_chart()
        except Exception as e: 
            self._log(f"Greedy Error: {e}")

    def run_bb(self):
        try:
            b = float(self.budget_var.get())
            opt = PortfolioOptimizer(b, self.assets)
            if opt:
                v, ch, t = opt.branch_and_bound()
                self._update_matrix("B&B (0/1)", v, t)
                self.summary.update_summary(ch, v, b)
                self.chart_results["B&B"] = v
                self.update_chart()
                self._log(f"B&B Result: ${v:.1f}")
        except Exception as e: 
            self._log(f"B&B Error: {e}")

    def _update_matrix(self, s, v, t, n="Optimal"):
        for i in self.comp.get_children():
            if self.comp.item(i)['values'][0] == s: 
                self.comp.delete(i)
        self.comp.insert("", "end", values=(s, f"${v:.1f}", f"{t*1000:.1f}ms", n))

    def show_dp_table_window(self):
        if not self.last_dp_table:
            messagebox.showwarning("Incomplete", "Run DP algorithm first to generate matrix.")
            return
        tbl = self.last_dp_table
        p_set = set(self.last_dp_path)
        assets = self.last_dp_assets
        W = self.last_dp_W
        n = len(assets)
        v = self.last_dp_return
        
        win = ctk.CTkToplevel(self.root)
        win.title(f"DP State Transition Graph - Return: ${v:.1f}")
        win.geometry("1000x700")
        win.configure(fg_color=self.bg_color)
        
        # Focus management for Toplevel
        win.after(100, win.lift)
        win.after(200, win.focus_force)
        
        cols = list(range(0, W+1, max(1, W//100)))
        if W not in cols: 
            cols.append(W)
            
        c_p = ctk.CTkFrame(win, fg_color="transparent")
        c_p.pack(fill="both", expand=True, padx=10, pady=10)
        
        cnv = tk.Canvas(c_p, bg=self.bg_color, highlightthickness=0)
        
        # Style Toplevel scrollbars
        self.style.configure("Custom.Vertical.TScrollbar", troughcolor=self.bg_color, background="#333333")
        self.style.configure("Custom.Horizontal.TScrollbar", troughcolor=self.bg_color, background="#333333")
        
        vs = ttk.Scrollbar(c_p, orient="vertical", command=cnv.yview, style="Custom.Vertical.TScrollbar")
        hs = ttk.Scrollbar(win, orient="horizontal", command=cnv.xview, style="Custom.Horizontal.TScrollbar")
        
        frm = tk.Frame(cnv, bg=self.bg_color)
        frm.bind("<Configure>", lambda e: cnv.configure(scrollregion=cnv.bbox("all")))
        cnv.create_window((0,0), window=frm, anchor="nw")
        
        cnv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        cnv.bind_all("<MouseWheel>", lambda e: cnv.yview_scroll(int(-1*(e.delta/120)),"units"))
        
        # Header Row
        for idx, w in enumerate(cols): 
            tk.Label(frm, text=f"w={w}", bg=self.accent_color, fg="white", font=('Segoe UI', 11, 'bold'), width=8, relief="flat").grid(row=0, column=idx+1, padx=1, pady=1)
            
        # Data Rows
        for i in range(n+1):
            nm = assets[i-1].name if i>0 else "Base"
            tk.Label(frm, text=nm, bg="#2d2d2d", fg="white", font=('Segoe UI', 11, 'bold'), width=25, anchor="w", padx=10, relief="flat").grid(row=i+1, column=0, padx=1, pady=1)
            for idx, w in enumerate(cols):
                is_p = (i,w) in p_set
                bg = "#FFB300" if is_p else "#1e1e1e"
                fg = "black" if is_p else "white"
                tk.Label(frm, text=f"{tbl[i][w]:.0f}"+(" *" if is_p else ""), bg=bg, fg=fg, font=('Consolas', 11), width=8, relief="flat").grid(row=i+1, column=idx+1, padx=1, pady=1)
                
        cnv.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        hs.pack(fill="x", padx=10, pady=(0, 6))
        
        dismiss_btn = ctk.CTkButton(win, text="Dismiss Visualization", fg_color=self.accent_color, hover_color="#008080", text_color="white", command=win.destroy)
        dismiss_btn.pack(pady=10)

if __name__ == "__main__":
    app = ctk.CTk()
    gui = PortfolioGUI(app)
    app.mainloop()
