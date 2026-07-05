import tkinter as tk
import customtkinter as ctk

class PortfolioSummaryFrame(ctk.CTkFrame):
    def __init__(self, parent, bg_color, card_bg, accent_color, text_color):
        # We pass card_bg as the fg_color of the frame to act as a card container
        super().__init__(parent, fg_color=card_bg, corner_radius=12, border_width=1, border_color="#e5e7eb")
        
        self.accent_color = accent_color
        self.text_color = text_color
        
        # Header Label (replaces the old TLabelframe title)
        self.header_lbl = ctk.CTkLabel(
            self, 
            text="OPTIMIZED PORTFOLIO SUMMARY", 
            font=('Segoe UI', 14, 'bold'), 
            text_color=self.accent_color
        )
        self.header_lbl.pack(anchor="w", padx=10, pady=(8, 4))
        
        # 1. Badge Container
        self.badge_container = ctk.CTkFrame(self, fg_color="transparent")
        self.badge_container.pack(fill="x", padx=10, pady=(0, 8))
        
        # 2. Metrics Container
        self.metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_container.pack(fill="x", padx=10)
        
        self.cost_lbl = ctk.CTkLabel(
            self.metrics_container, 
            text="Total Cost: $0", 
            text_color="#dc2626", 
            font=('Segoe UI', 14, 'bold')
        )
        self.cost_lbl.pack(side="left", expand=True)
        
        self.return_lbl = ctk.CTkLabel(
            self.metrics_container, 
            text="Total Return: $0", 
            text_color="#059669", 
            font=('Segoe UI', 14, 'bold')
        )
        self.return_lbl.pack(side="left", expand=True)
        
        # Progress bar container
        pb_frame = ctk.CTkFrame(self.metrics_container, fg_color="transparent")
        pb_frame.pack(side="left", expand=True, fill="x", padx=10)
        
        self.pb_title = ctk.CTkLabel(
            pb_frame, 
            text="Budget Used:", 
            text_color=self.text_color, 
            font=('Segoe UI', 12)
        )
        self.pb_title.pack(side="top", anchor="w")
        
        self.pb = ctk.CTkProgressBar(
            pb_frame, 
            orientation="horizontal", 
            height=12,
            progress_color=self.accent_color,
            fg_color="#e5e7eb"
        )
        self.pb.pack(fill="x", pady=2)
        self.pb.set(0.0) # CTkProgressBar values must be between 0.0 and 1.0
        
        self.pb_val = ctk.CTkLabel(
            pb_frame, 
            text="0%", 
            text_color=self.accent_color, 
            font=('Segoe UI', 12, 'bold')
        )
        self.pb_val.pack(anchor="e")
        
        # 3. Remaining Budget
        self.rem_lbl = ctk.CTkLabel(
            self, 
            text="Remaining Budget: $0", 
            text_color="#4b5563", 
            font=('Segoe UI', 13, 'italic')
        )
        self.rem_lbl.pack(anchor="w", padx=10, pady=(4, 8))

    def update_summary(self, assets, total_return, budget):
        # Destroy previous badges
        for child in self.badge_container.winfo_children():
            child.destroy()
            
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
            else:
                txt = str(item)
            
            # Draw beautiful pill badge with CustomTkinter rounded corners
            badge = ctk.CTkLabel(
                self.badge_container, 
                text=txt, 
                fg_color=self.accent_color, 
                text_color="white", 
                font=('Segoe UI', 12, 'bold'), 
                corner_radius=8,
                padx=6, 
                pady=2
            )
            badge.pack(side="left", padx=3, pady=2)
        
        self.cost_lbl.configure(text=f"Total Cost: ${total_cost:.1f}")
        self.return_lbl.configure(text=f"Total Return: ${total_return:.1f}")
        
        used_pct = (total_cost / budget * 100) if budget > 0 else 0
        self.pb.set(used_pct / 100.0) # Set progress value (0.0 to 1.0)
        self.pb_val.configure(text=f"{used_pct:.1f}%")
        self.pb.update() # Force layout and visual update
        
        remaining = budget - total_cost
        self.rem_lbl.configure(text=f"Remaining Budget: ${max(0.0, remaining):.1f}")
