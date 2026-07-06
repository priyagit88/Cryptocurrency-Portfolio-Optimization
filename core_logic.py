import time
import math
from typing import List, Tuple, Dict, Any

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

    def dynamic_programming(self) -> Tuple[float, List[Asset], float, List[List[float]], List[List[bool]], int, int, int, List[Dict[str, Any]]]:
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
        
        # Using 2D DP table for visualization purposes (Asset i+1 vs Budget w)
        dp = [[0.0] * (W + 1) for _ in range(n + 1)]
        keep = [[False] * (W + 1) for _ in range(n)]

        comparisons = 0
        cell_fills = 0
        history = []
        for i in range(n):
            asset_start_time = time.perf_counter()
            cost_i = int(self.assets[i].cost * scale)
            val_i = self.assets[i].expected_return
            for w in range(W + 1):
                comparisons += 1
                if cost_i <= w:
                    if dp[i][w - cost_i] + val_i > dp[i][w]:
                        dp[i+1][w] = dp[i][w - cost_i] + val_i
                        cell_fills += 1
                        keep[i][w] = True
                    else:
                        dp[i+1][w] = dp[i][w]
                        cell_fills += 1
                else:
                    dp[i+1][w] = dp[i][w]
                    cell_fills += 1
            asset_time = (time.perf_counter() - asset_start_time) * 1000
            
            # Calculate chosen subset at row i+1 for budget W
            temp_chosen_cost = 0.0
            temp_w = W
            temp_count = 0
            for r in range(i, -1, -1):
                if keep[r][temp_w]:
                    temp_chosen_cost += self.assets[r].cost
                    cost_r = int(self.assets[r].cost * scale)
                    temp_w -= cost_r
                    temp_count += 1
            rem_budget_at_step = self.budget - temp_chosen_cost
            
            history.append({
                "step": i + 1,
                "asset": self.assets[i],
                "action": f"Row {i+1}: {self.assets[i].name}",
                "remaining_budget": rem_budget_at_step,
                "current_return": dp[i+1][W],
                "assets_count": temp_count,
                "comparisons": comparisons,
                "cell_fills": cell_fills,
                "time_ms": asset_time
            })
        
        # Step 1: Deep copy and snapshot for visualization
        self.last_dp_table = [row[:] for row in dp]
        self.last_dp_assets = [a for a in self.assets]
        self.last_dp_W = W
        self.last_dp_path = []
        
        # Backtrack to find path as requested (tracking every visited cell)
        curr_i, curr_w = n, W
        while curr_i > 0 and curr_w >= 0:
            self.last_dp_path.append((curr_i, curr_w))
            if dp[curr_i][curr_w] != dp[curr_i-1][curr_w]:
                cost_i = int(self.assets[curr_i-1].cost * scale)
                curr_w -= cost_i
            curr_i -= 1
        if curr_w >= 0:
            self.last_dp_path.append((0, curr_w))
        if (0, 0) not in self.last_dp_path:
            self.last_dp_path.append((0, 0))

        chosen = []
        curr_w = W
        for i in range(n - 1, -1, -1):
            if keep[i][curr_w]:
                chosen.append(self.assets[i])
                cost_i = int(self.assets[i].cost * scale)
                curr_w -= cost_i
                
        execution_time = time.perf_counter() - start_time
        return dp[n][W], chosen[::-1], execution_time, self.last_dp_table, self.last_dp_path, scale, comparisons, cell_fills, history

    def greedy_fractional(self) -> Tuple[float, List[Tuple[Asset, float]], float, int, float, List[Dict[str, Any]]]:
        start_time = time.perf_counter()
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        total_return = 0.0
        current_budget = self.budget
        allocation = [] # List of (Asset, weight)
        
        n = len(self.assets)
        sort_operations = n * math.log2(n) if n > 1 else 0.0
        comparisons = 0
        history = []
        
        for idx, asset in enumerate(sorted_assets):
            asset_start_time = time.perf_counter()
            comparisons += 1
            if current_budget >= asset.cost:
                total_return += asset.expected_return
                current_budget -= asset.cost
                fraction = 1.0
                allocation.append((asset, 1.0))
            else:
                fraction = current_budget / asset.cost if asset.cost > 0 else 0.0
                if fraction > 0:
                    total_return += asset.expected_return * fraction
                    allocation.append((asset, fraction))
                current_budget = 0
            asset_time = (time.perf_counter() - asset_start_time) * 1000
            
            history.append({
                "step": idx + 1,
                "asset": asset,
                "action": f"{asset.name} ({fraction*100:.0f}%)",
                "remaining_budget": current_budget,
                "current_return": total_return,
                "assets_count": len(allocation),
                "comparisons": comparisons,
                "sort_ops": sort_operations,
                "time_ms": asset_time
            })
        
        execution_time = time.perf_counter() - start_time
        return total_return, allocation, execution_time, comparisons, sort_operations, history

    def branch_and_bound(self) -> Tuple[float, List[Asset], float, int, int, List[Dict[str, Any]]]:
        start_time = time.perf_counter()
        sorted_assets = sorted(self.assets, key=lambda x: x.ratio, reverse=True)
        n = len(sorted_assets)
        
        if n == 0:
            return 0.0, [], 0.0, 0, 0, []
            
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
        
        nodes_explored = 0
        nodes_pruned = 0
        history = []
        logged_items_count = 0
        level_start_time = time.perf_counter()
        
        while Q:
            u = Q.pop(0)
            nodes_explored += 1
            
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
            else:
                nodes_pruned += 1
                
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
            else:
                nodes_pruned += 1
                
            if not Q or Q[0].level > u.level:
                if u.level + 1 < n and u.level + 1 == logged_items_count:
                    asset_time = (time.perf_counter() - level_start_time) * 1000
                    asset_k = sorted_assets[logged_items_count]
                    rem_b = self.budget - sum(a.cost for a in best_items)
                    history.append({
                        "step": logged_items_count + 1,
                        "asset": asset_k,
                        "action": f"L{logged_items_count+1}: {asset_k.name}",
                        "remaining_budget": rem_b,
                        "current_return": max_profit,
                        "assets_count": len(best_items),
                        "nodes_explored": nodes_explored,
                        "nodes_pruned": nodes_pruned,
                        "time_ms": asset_time
                    })
                    logged_items_count += 1
                    level_start_time = time.perf_counter()
        
        while logged_items_count < n:
            asset_time = (time.perf_counter() - level_start_time) * 1000
            asset_k = sorted_assets[logged_items_count]
            rem_b = self.budget - sum(a.cost for a in best_items)
            history.append({
                "step": logged_items_count + 1,
                "asset": asset_k,
                "action": f"L{logged_items_count+1}: {asset_k.name} (Pruned)",
                "remaining_budget": rem_b,
                "current_return": max_profit,
                "assets_count": len(best_items),
                "nodes_explored": nodes_explored,
                "nodes_pruned": nodes_pruned,
                "time_ms": asset_time
            })
            logged_items_count += 1
            level_start_time = time.perf_counter()
        
        execution_time = time.perf_counter() - start_time
        return max_profit, best_items, execution_time, nodes_explored, nodes_pruned, history
