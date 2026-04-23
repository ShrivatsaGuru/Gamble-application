import random
from db import get_connection


class FixedAmountStrategy:
    def __init__(self, amount):
        self.amount = amount

    def get_bet(self, current_stake):
        return self.amount


class PercentageStrategy:
    def __init__(self, percent):
        self.percent = percent

    def get_bet(self, current_stake):
        return round(current_stake * (self.percent / 100), 2)


class MartingaleStrategy:
    def __init__(self, base_amount):
        self.base = base_amount
        self.current = base_amount

    def get_bet(self, current_stake):
        return self.current

    def on_win(self):
        self.current = self.base

    def on_loss(self):
        self.current = self.current * 2


class BettingService:

    def _get_gambler(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            raise ValueError(f"Gambler {gambler_id} not found.")
        return row

    def _save_bet(self, gambler_id, amount, won, stake_before, stake_after, strategy_name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bets (gambler_id, amount, won, stake_before, stake_after, strategy)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (gambler_id, amount, won, stake_before, stake_after, strategy_name))
        outcome_col = "wins" if won else "losses"
        cursor.execute(f"UPDATE gamblers SET total_bets=total_bets+1, {outcome_col}={outcome_col}+1 WHERE id=%s", (gambler_id,))
        new_stake = stake_after
        cursor.execute("UPDATE gamblers SET stake=%s WHERE id=%s", (new_stake, gambler_id))
        conn.commit()
        cursor.close()
        conn.close()

    def place_bet(self, gambler_id, amount, win_probability=0.5):
        row = self._get_gambler(gambler_id)
        stake = float(row["stake"])
        min_bet = float(row.get("min_bet") or 1)
        max_bet = float(row.get("max_bet") or stake)

        if amount <= 0:
            raise ValueError("Bet amount must be positive.")
        if amount > stake:
            raise ValueError(f"Bet ({amount}) exceeds current stake ({stake:.2f}).")
        if amount < min_bet:
            raise ValueError(f"Bet ({amount}) is below minimum ({min_bet}).")
        if amount > max_bet:
            raise ValueError(f"Bet ({amount}) exceeds maximum ({max_bet}).")

        won = self.determine_outcome(win_probability)
        stake_after = stake + amount if won else stake - amount
        self._save_bet(gambler_id, amount, won, stake, stake_after, "MANUAL")

        result = "WON" if won else "LOST"
        print(f"  Bet {result}  |  Amount: {amount:.2f}  |  Stake: {stake:.2f} -> {stake_after:.2f}")
        return won, stake_after

    def determine_outcome(self, win_probability=0.5):
        return random.random() < win_probability

    def place_bet_with_strategy(self, gambler_id, strategy, win_probability=0.5):
        row = self._get_gambler(gambler_id)
        stake = float(row["stake"])
        amount = strategy.get_bet(stake)

        if amount <= 0 or amount > stake:
            print(f"  Skipping bet — invalid amount ({amount:.2f}) for stake ({stake:.2f})")
            return None, stake

        won = self.determine_outcome(win_probability)
        stake_after = stake + amount if won else stake - amount
        strategy_name = type(strategy).__name__

        self._save_bet(gambler_id, amount, won, stake, stake_after, strategy_name)

        if hasattr(strategy, "on_win") and hasattr(strategy, "on_loss"):
            strategy.on_win() if won else strategy.on_loss()

        result = "WON" if won else "LOST"
        print(f"  [{strategy_name}] Bet {result}  |  Amount: {amount:.2f}  |  Stake: {stake:.2f} -> {stake_after:.2f}")
        return won, stake_after

    def place_consecutive_bets(self, gambler_id, strategy, count, win_probability=0.5):
        print(f"\n  Running {count} consecutive bets...\n")
        wins = 0
        losses = 0
        for i in range(1, count + 1):
            row = self._get_gambler(gambler_id)
            stake = float(row["stake"])
            win_t = float(row["win_threshold"])
            loss_t = float(row["loss_threshold"])

            if stake >= win_t:
                print(f"  Win threshold reached at bet #{i}. Stopping.")
                break
            if stake <= loss_t:
                print(f"  Loss threshold reached at bet #{i}. Stopping.")
                break

            print(f"  Bet #{i}", end="  ")
            won, _ = self.place_bet_with_strategy(gambler_id, strategy, win_probability)
            if won is None:
                break
            if won:
                wins += 1
            else:
                losses += 1

        print(f"\n  Session result: {wins} wins, {losses} losses")

    def get_bet_history(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bets WHERE gambler_id=%s ORDER BY id", (gambler_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            print("  No bets placed yet.")
            return

        print(f"\n  {'#':<4} {'Strategy':<20} {'Amount':>8} {'Result':<6} {'Before':>9} {'After':>9}")
        print(f"  {'-'*60}")
        for i, r in enumerate(rows, 1):
            result = "WIN" if r["won"] else "LOSS"
            print(f"  {i:<4} {r['strategy']:<20} {float(r['amount']):>8.2f} {result:<6} {float(r['stake_before']):>9.2f} {float(r['stake_after']):>9.2f}")
