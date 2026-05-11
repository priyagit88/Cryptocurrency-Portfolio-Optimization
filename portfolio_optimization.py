import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

class Asset:
    def __init__(self, name: str, cost: float, expected_return: float):
        self.name = name
        self.cost = cost
        self.expected_return = expected_return
        self.ratio = expected_return / cost if cost > 0 else 0

    def __repr__(self):
        return f"{self.name}(C:{self.cost}, R:{self.expected_return})"

class PortfolioOptimizer:
    def __init__(self, budget: float, assets: List[Asset]):
        self.budget = budget
        self.assets = assets

    def dynamic_programming(self) -> Tuple[float, List[Asset]]:
        scale = 100
        W = int(self.budget * scale)
        n = len(self.assets)
        
        dp = [0.0] * (W + 1)
        keep = [[False] * (W + 1) for _ in range(n)]

        for i in range(n):
            cost_i = int(self.assets[i].cost * scale)
            val_i = self.assets[i].expected_return
            for w in range(W, cost_i - 1, -1):
                if dp[w - cost_i] + val_i > dp[w]:
                    dp[w] = dp[w - cost_i] + val_i
                    keep[i][w] = True
        
        chosen = []
        w = W
        for i in range(n - 1, -1, -1):
            if keep[i][w]:
                chosen.append(self.assets[i])
                cost_i = int(self.assets[i].cost * scale)
                w -= cost_i
                
        return dp[W], chosen[::-1]

    def greedy_fractional(self) -> Tuple[float, str]:
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        total_return = 0.0
        current_budget = self.budget
        details = []
        
        for asset in sorted_assets:
            if current_budget >= asset.cost:
                total_return += asset.expected_return
                current_budget -= asset.cost
                details.append(f"100% of {asset.name}")
            else:
                fraction = current_budget / asset.cost
                if fraction > 0:
                    total_return += asset.expected_return * fraction
                    details.append(f"{fraction*100:.2f}% of {asset.name}")
                current_budget = 0
                break
                
        return total_return, ", ".join(details)

    def branch_and_bound(self) -> Tuple[float, List[Asset]]:
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        n = len(sorted_assets)
        
        if n == 0:
            return 0.0, []
            
        class Node:
            def __init__(self, level, profit, weight, bound, items_included):
                self.level = level
                self.profit = profit
                self.weight = weight
                self.bound = bound
                self.items_included = items_included
                
        def bound(node: Node) -> float:
            if node.weight >= self.budget:
                return 0
            
            profit_bound = node.profit
            j = node.level + 1
            totweight = node.weight
            
            while j < n and totweight + sorted_assets[j].cost <= self.budget:
                totweight += sorted_assets[j].cost
                profit_bound += sorted_assets[j].expected_return
                j += 1
                
            if j < n:
                profit_bound += (self.budget - totweight) * sorted_assets[j].ratio
                
            return profit_bound

        Q = []
        u = Node(-1, 0.0, 0.0, 0.0, [])
        Q.append(u)
        
        max_profit = 0.0
        best_items = []
        
        while Q:
            u = Q.pop(0)
            
            if u.level == -1:
                v_level = 0
            elif u.level == n - 1:
                continue
            else:
                v_level = u.level + 1
                
            v_include = Node(
                level=v_level,
                profit=u.profit + sorted_assets[v_level].expected_return,
                weight=u.weight + sorted_assets[v_level].cost,
                bound=0.0,
                items_included=u.items_included + [sorted_assets[v_level]]
            )
            
            if v_include.weight <= self.budget and v_include.profit > max_profit:
                max_profit = v_include.profit
                best_items = v_include.items_included
                
            v_include.bound = bound(v_include)
            if v_include.bound > max_profit:
                Q.append(v_include)
                
            v_exclude = Node(
                level=v_level,
                profit=u.profit,
                weight=u.weight,
                bound=0.0,
                items_included=u.items_included
            )
            v_exclude.bound = bound(v_exclude)
            
            if v_exclude.bound > max_profit:
                Q.append(v_exclude)
                
        return max_profit, best_items


class PortfolioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptocurrency Portfolio Optimization")
        self.root.geometry("600x600")
        
        self.assets = [
            Asset("Bitcoin", 50, 60),
            Asset("Ethereum", 20, 100),
            Asset("Solana", 30, 120),
            Asset("Cardano", 10, 40)
        ]
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- UI LAYOUT ---
        # 1. Budget Frame
        budget_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        budget_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(budget_frame, text="Total Budget:").pack(side="left")
        self.budget_var = tk.StringVar(value="50")
        ttk.Entry(budget_frame, textvariable=self.budget_var, width=15).pack(side="left", padx=5)
        
        # 2. Add Asset Frame
        add_frame = ttk.LabelFrame(self.root, text="Add New Asset", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.name_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Cost:").grid(row=0, column=2, padx=5, pady=5)
        self.cost_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.cost_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Return:").grid(row=0, column=4, padx=5, pady=5)
        self.return_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.return_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Add Asset", command=self.add_asset).grid(row=0, column=6, padx=5, pady=5)
        
        # 3. Assets List Frame
        list_frame = ttk.LabelFrame(self.root, text="Available Assets", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Name", "Cost", "Expected Return")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.heading("Name", text="Name")
        self.tree.heading("Cost", text="Cost")
        self.tree.heading("Expected Return", text="Expected Return")
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_list()
        
        # 4. Actions Frame
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(action_frame, text="Run DP (0/1 Knapsack)", command=self.run_dp).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Run Greedy (Fractional)", command=self.run_greedy).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Run Branch & Bound", command=self.run_bb).pack(side="left", padx=5)
        
        # 5. Results Frame
        result_frame = ttk.LabelFrame(self.root, text="Optimization Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = tk.Text(result_frame, height=8, state='disabled')
        self.result_text.pack(fill="both", expand=True)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for asset in self.assets:
            self.tree.insert("", "end", values=(asset.name, asset.cost, asset.expected_return))

    def add_asset(self):
        try:
            name = self.name_var.get()
            cost = float(self.cost_var.get())
            ret = float(self.return_var.get())
            if not name:
                messagebox.showerror("Error", "Asset name cannot be empty.")
                return
            self.assets.append(Asset(name, cost, ret))
            self.refresh_list()
            self.name_var.set("")
            self.cost_var.set("")
            self.return_var.set("")
        except ValueError:
            messagebox.showerror("Error", "Cost and Return must be valid numbers.")

    def get_optimizer(self):
        try:
            budget = float(self.budget_var.get())
            return PortfolioOptimizer(budget, self.assets)
        except ValueError:
            messagebox.showerror("Error", "Budget must be a valid number.")
            return None

    def display_result(self, title, result_str):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"=== {title} ===\n\n{result_str}\n")
        self.result_text.config(state='disabled')

    def run_dp(self):
        optimizer = self.get_optimizer()
        if optimizer:
            val, chosen = optimizer.dynamic_programming()
            chosen_names = ", ".join([a.name for a in chosen]) if chosen else "None"
            result = f"Maximum Return: {val}\n\nChosen Assets:\n{chosen_names}"
            self.display_result("Dynamic Programming", result)

    def run_greedy(self):
        optimizer = self.get_optimizer()
        if optimizer:
            val, details = optimizer.greedy_fractional()
            result = f"Maximum Return (Fractional allowed): {val:.2f}\n\nAllocations:\n{details}"
            self.display_result("Greedy Algorithm", result)

    def run_bb(self):
        optimizer = self.get_optimizer()
        if optimizer:
            val, chosen = optimizer.branch_and_bound()
            chosen_names = ", ".join([a.name for a in chosen]) if chosen else "None"
            result = f"Maximum Return: {val}\n\nChosen Assets:\n{chosen_names}"
            self.display_result("Branch and Bound", result)

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioGUI(root)
    root.mainloop()
