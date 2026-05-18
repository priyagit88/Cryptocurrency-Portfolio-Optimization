import tkinter as tk
from tkinter import ttk

class PortfolioSummaryFrame(ttk.LabelFrame):
    def __init__(self, parent, bg_color, card_bg, accent_color, text_color):
        super().__init__(parent, text=" Optimized Portfolio Summary ", padding=15)
        self.bg_color = bg_color
        self.card_bg = card_bg
        self.accent_color = accent_color
        self.text_color = text_color
        
        self.configure(style="Card.TLabelframe")
        
        # 1. Badge Container
        self.badge_container = tk.Frame(self, bg=self.card_bg)
        self.badge_container.pack(fill="x", pady=(0, 15))
        
        # 2. Metrics Container
        self.metrics_container = tk.Frame(self, bg=self.card_bg)
        self.metrics_container.pack(fill="x")
        
        self.cost_lbl = tk.Label(self.metrics_container, text="Total Cost: $0", bg=self.card_bg, fg="#ff4b2b", font=('Segoe UI', 10, 'bold'))
        self.cost_lbl.pack(side="left", expand=True)
        
        self.return_lbl = tk.Label(self.metrics_container, text="Total Return: $0", bg=self.card_bg, fg="#00ff00", font=('Segoe UI', 10, 'bold'))
        self.return_lbl.pack(side="left", expand=True)
        
        # Style Progress Bar as requested
        s = ttk.Style()
        s.configure("Teal.Horizontal.TProgressbar", thickness=15, troughcolor='#1a1a2e', background='#00bcd4', bordercolor='#1a1a2e', lightcolor='#00bcd4', darkcolor='#00bcd4')
        
        pb_frame = tk.Frame(self.metrics_container, bg=self.card_bg)
        pb_frame.pack(side="left", expand=True, fill="x", padx=10)
        tk.Label(pb_frame, text="Budget Used:", bg=self.card_bg, fg=self.text_color, font=('Segoe UI', 9)).pack(side="top", anchor="w")
        self.pb = ttk.Progressbar(pb_frame, orient="horizontal", length=100, mode="determinate", maximum=100, style="Teal.Horizontal.TProgressbar")
        self.pb.pack(fill="x")
        self.pb_val = tk.Label(pb_frame, text="0%", bg=self.card_bg, fg="#00bcd4", font=('Segoe UI', 8, 'bold'))
        self.pb_val.pack(anchor="e")
        
        # 3. Remaining Budget
        self.rem_lbl = tk.Label(self, text="Remaining Budget: $0", bg=self.card_bg, fg="#999999", font=('Segoe UI', 9, 'italic'))
        self.rem_lbl.pack(anchor="w", pady=(10, 0))

    def update_summary(self, assets, total_return, budget):
        for child in self.badge_container.winfo_children(): child.destroy()
            
        total_cost = 0
        for item in assets:
            if isinstance(item, tuple) and len(item) == 2:
                asset, weight = item
                cost = asset.cost * weight
                name = asset.name
                ret = asset.expected_return * weight
                total_cost += cost
                txt = f"{weight*100:.0f}% {name} (${ret:.1f})"
            elif hasattr(item, 'cost'):
                asset = item
                cost = asset.cost
                name = asset.name
                ret = asset.expected_return
                total_cost += cost
                txt = f"{name} (${ret:.1f})"
            else: txt = str(item)
            
            badge = tk.Label(self.badge_container, text=txt, bg="#008080", fg="white", 
                            font=('Segoe UI', 8, 'bold'), padx=8, pady=3)
            badge.pack(side="left", padx=3, pady=3)
        
        self.cost_lbl.config(text=f"Total Cost: ${total_cost:.1f}")
        self.return_lbl.config(text=f"Total Return: ${total_return:.1f}")
        
        used_pct = (total_cost / budget * 100) if budget > 0 else 0
        self.pb['value'] = used_pct
        self.pb_val.config(text=f"{used_pct:.1f}%")
        self.pb.update() # Force refresh as requested
        
        remaining = budget - total_cost
        self.rem_lbl.config(text=f"Remaining Budget: ${max(0.0, remaining):.1f}")
