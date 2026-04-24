from db import get_connection
class TxType:
    INITIAL   = "INITIAL_STAKE"
    BET_WIN   = "BET_WIN"
    BET_LOSS  = "BET_LOSS"
    DEPOSIT   = "DEPOSIT"
    WITHDRAWAL= "WITHDRAWAL"
    RESET     = "RESET"


class StakeManagementService:
    def _get_stake(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT stake, win_threshold, loss_threshold FROM gamblers WHERE id=%s", (gambler_id,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        if not row:
            raise ValueError(f"Gambler ID {gambler_id} not found.")
        return row
    def _apply(self, gambler_id, tx_type, amount):
        row = self._get_stake(gambler_id)
        before = float(row["stake"])
        after = before + amount
        if after < 0:
            raise ValueError("Stake cannot go negative.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE gamblers SET stake=%s WHERE id=%s", (after, gambler_id))
        cursor.execute("""
            INSERT INTO stake_transactions (gambler_id, transaction_type, amount, balance_before, balance_after)
            VALUES (%s, %s, %s, %s, %s)
        """, (gambler_id, tx_type, abs(amount), before, after))
        conn.commit()
        cursor.close(); conn.close()
        return before, after

    def initialize(self, gambler_id, stake):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stake_transactions (gambler_id, transaction_type, amount, balance_before, balance_after)
            VALUES (%s, %s, %s, %s, %s)
        """, (gambler_id, TxType.INITIAL, stake, 0, stake))
        conn.commit()
        cursor.close(); conn.close()
        print(f"Stake initialized: {stake}")
    def track(self, gambler_id):
        row = self._get_stake(gambler_id)
        stake = float(row["stake"])
        win_t = float(row["win_threshold"])
        loss_t = float(row["loss_threshold"])
        warn = ""
        if stake <= loss_t * 1.2:
            warn = " ⚠ Approaching LOSS threshold!"
        elif stake >= win_t * 0.8:
            warn = " ✓ Approaching WIN threshold!"
        print(f"Current Stake: {stake:.2f} | Win: {win_t:.2f} | Loss: {loss_t:.2f}{warn}")
        return stake
    def calculate(self, gambler_id, bet_amount, won):
        tx_type = TxType.BET_WIN if won else TxType.BET_LOSS
        change = bet_amount if won else -bet_amount
        before, after = self._apply(gambler_id, tx_type, change)
        result = "WON" if won else "LOST"
        print(f"Bet {result}: {bet_amount:.2f} | Stake: {before:.2f} → {after:.2f}")
        return after
    def monitor(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT MAX(balance_after) as peak, MIN(balance_after) as low,
                   COUNT(*) as total_tx
            FROM stake_transactions WHERE gambler_id=%s
        """, (gambler_id,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        peak = float(row["peak"] or 0)
        low  = float(row["low"] or 0)
        volatility = peak - low
        print(f"Peak: {peak:.2f} | Low: {low:.2f} | Volatility: {volatility:.2f} | Transactions: {row['total_tx']}")
        return {"peak": peak, "low": low, "volatility": volatility}
    def validate_boundaries(self, gambler_id):
        row = self._get_stake(gambler_id)
        stake = float(row["stake"])
        win_t = float(row["win_threshold"])
        loss_t = float(row["loss_threshold"])

        if stake >= win_t:
            print(f"WIN condition reached! Stake {stake:.2f} >= {win_t:.2f}"); return "WIN"
        if stake <= loss_t:
            print(f"LOSS condition reached! Stake {stake:.2f} <= {loss_t:.2f}"); return "LOSS"
        print(f"Stake {stake:.2f} is within boundaries ({loss_t:.2f} - {win_t:.2f}).")
        return "OK"
    def report(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT transaction_type, amount, balance_before, balance_after, created_at
            FROM stake_transactions WHERE gambler_id=%s ORDER BY id
        """, (gambler_id,))
        rows = cursor.fetchall()
        cursor.close(); conn.close()
        if not rows:
            print("No transactions found."); return
        print(f"\n  Stake History — Gambler ID {gambler_id}")
        print(f"  {'Type':<15} {'Amount':>8} {'Before':>9} {'After':>9}")
        print(f"  {'-'*45}")
        for r in rows:
            print(f"  {r['transaction_type']:<15} {float(r['amount']):>8.2f} {float(r['balance_before']):>9.2f} {float(r['balance_after']):>9.2f}")
        wins  = sum(float(r["amount"]) for r in rows if r["transaction_type"] == TxType.BET_WIN)
        losses= sum(float(r["amount"]) for r in rows if r["transaction_type"] == TxType.BET_LOSS)
        print(f"  {'-'*45}")
        print(f"  Total Won: {wins:.2f}  |  Total Lost: {losses:.2f}  |  Net: {wins - losses:+.2f}\n")

    def deposit(self, gambler_id, amount):
        _, after = self._apply(gambler_id, TxType.DEPOSIT, amount)
        print(f"Deposited {amount:.2f}. New stake: {after:.2f}")

    def withdraw(self, gambler_id, amount):
        _, after = self._apply(gambler_id, TxType.WITHDRAWAL, -amount)
        print(f"Withdrew {amount:.2f}. New stake: {after:.2f}")
