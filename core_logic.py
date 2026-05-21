import time
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

    def dynamic_programming(self) -> Tuple[float, List[Asset], float]:
        start_time = time.perf_counter()
        # Find maximum decimal places to determine scale (checking both assets and budget)
        max_decimals = 0
        for val in [a.cost for a in self.assets] + [self.budget]:
            s_val = str(float(val))
            if '.' in s_val:
                decimals = len(s_val.split('.')[1].rstrip('0'))
                max_decimals = max(max_decimals, decimals)
        
        scale = 10 ** min(max_decimals, 2) # Cap scale to 100 to prevent MemoryError
        W = int(self.budget * scale)
        
        # Safety net to prevent out-of-memory crash
        if W > 100000:
            raise ValueError("Budget and precision combination too high for DP memory limits.")
        n = len(self.assets)
        
        # Using 2D DP table (Asset i+1 vs Budget w)
        dp = [[0.0] * (W + 1) for _ in range(n + 1)]
        keep = [[False] * (W + 1) for _ in range(n)]

        for i in range(n):
            cost_i = int(self.assets[i].cost * scale)
            val_i = self.assets[i].expected_return
            for w in range(W + 1):
                if cost_i <= w:
                    if dp[i][w - cost_i] + val_i > dp[i][w]:
                        dp[i+1][w] = dp[i][w - cost_i] + val_i
                        keep[i][w] = True
                    else:
                        dp[i+1][w] = dp[i][w]
                else:
                    dp[i+1][w] = dp[i][w]
        
        chosen = []
        curr_w = W
        for i in range(n - 1, -1, -1):
            if keep[i][curr_w]:
                chosen.append(self.assets[i])
                cost_i = int(self.assets[i].cost * scale)
                curr_w -= cost_i
                
        execution_time = time.perf_counter() - start_time
        return dp[n][W], chosen[::-1], execution_time

    def greedy_fractional(self) -> Tuple[float, List[Tuple[Asset, float]], float]:
        start_time = time.perf_counter()
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        total_return = 0.0
        current_budget = self.budget
        allocation = [] # List of (Asset, weight)
        
        for asset in sorted_assets:
            if current_budget >= asset.cost:
                total_return += asset.expected_return
                current_budget -= asset.cost
                allocation.append((asset, 1.0))
            else:
                fraction = current_budget / asset.cost
                if fraction > 0:
                    total_return += asset.expected_return * fraction
                    allocation.append((asset, fraction))
                current_budget = 0
                break
        
        execution_time = time.perf_counter() - start_time
        return total_return, allocation, execution_time


    def branch_and_bound(self) -> Tuple[float, List[Asset], float]:
        start_time = time.perf_counter()
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        n = len(sorted_assets)
        
        if n == 0:
            return 0.0, [], 0.0
            
        class Node:
            def __init__(self, level, profit, weight, bound, items_included):
                self.level = level
                self.profit = profit
                self.weight = weight
                self.bound = bound
                self.items_included = items_included
                
        def bound(node: Node) -> float:
            if node.weight > self.budget:
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
        
        execution_time = time.perf_counter() - start_time
        return max_profit, best_items, execution_time
