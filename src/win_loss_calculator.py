import random


class WinLossCalculator:

    def __init__(self, win_probability=0.5):
        self.win_probability = win_probability

        self.total_wins   = 0
        self.total_losses = 0
        self.total_won    = 0.0
        self.total_lost   = 0.0

        self.current_streak       = 0
        self.current_streak_type  = None
        self.longest_win_streak   = 0
        self.longest_loss_streak  = 0

        self.balance_history = []

    def determine_outcome(self):
        return random.random() < self.win_probability

    def calculate_winnings(self, bet_amount, odds=2.0):
        return round(bet_amount * (odds - 1), 2)

    def calculate_loss(self, bet_amount):
        return bet_amount

    def play(self, bet_amount, current_stake, odds=2.0):
        won = self.determine_outcome()

        if won:
            profit = self.calculate_winnings(bet_amount, odds)
            new_stake = current_stake + profit
            self.total_wins  += 1
            self.total_won   += profit

            if self.current_streak_type == "WIN":
                self.current_streak += 1
            else:
                self.current_streak      = 1
                self.current_streak_type = "WIN"
            self.longest_win_streak = max(self.longest_win_streak, self.current_streak)

            result_str = f"WIN   +{profit:.2f}"
        else:
            loss = self.calculate_loss(bet_amount)
            new_stake = current_stake - loss
            self.total_losses += 1
            self.total_lost   += loss

            if self.current_streak_type == "LOSS":
                self.current_streak += 1
            else:
                self.current_streak      = 1
                self.current_streak_type = "LOSS"
            self.longest_loss_streak = max(self.longest_loss_streak, self.current_streak)

            result_str = f"LOSS  -{loss:.2f}"

        self.balance_history.append(new_stake)
        return won, new_stake, result_str

    def win_loss_ratio(self):
        if self.total_losses == 0:
            return float("inf")
        return round(self.total_wins / self.total_losses, 2)

    def win_rate(self):
        total = self.total_wins + self.total_losses
        if total == 0:
            return 0.0
        return round(self.total_wins / total * 100, 1)

    def net_profit(self):
        return round(self.total_won - self.total_lost, 2)

    def print_stats(self):
        print(f"\n  Results after {self.total_wins + self.total_losses} games")
        print(f"  Wins: {self.total_wins}  |  Losses: {self.total_losses}  |  Win Rate: {self.win_rate()}%")
        print(f"  Total Won: {self.total_won:.2f}  |  Total Lost: {self.total_lost:.2f}")
        print(f"  Net Profit/Loss: {self.net_profit():+.2f}")
        print(f"  Win/Loss Ratio: {self.win_loss_ratio()}")
        print(f"  Longest Win Streak: {self.longest_win_streak}  |  Longest Loss Streak: {self.longest_loss_streak}")
        streak_label = f"{self.current_streak_type} x{self.current_streak}" if self.current_streak_type else "none"
        print(f"  Current Streak: {streak_label}")

    def print_balance_history(self, initial_stake):
        print(f"\n  Balance history (starting at {initial_stake:.2f})")
        prev = initial_stake
        for i, bal in enumerate(self.balance_history, 1):
            change = bal - prev
            arrow  = "+" if change >= 0 else ""
            print(f"  Game {i:>3}  {arrow}{change:.2f}  ->  {bal:.2f}")
            prev = bal
