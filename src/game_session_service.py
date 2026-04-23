import random
import time
from datetime import datetime
from db import get_connection


class GameSessionService:

    def _get_gambler(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        if not row:
            raise ValueError(f"Gambler {gambler_id} not found.")
        return row

    def _update_stake(self, gambler_id, new_stake, won):
        conn = get_connection()
        cursor = conn.cursor()
        col = "wins" if won else "losses"
        cursor.execute(
            f"UPDATE gamblers SET stake=%s, total_bets=total_bets+1, {col}={col}+1 WHERE id=%s",
            (new_stake, gambler_id)
        )
        conn.commit()
        cursor.close(); conn.close()

    def _save_session(self, gambler_id, status, games, wins, losses, started_at, ended_at=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (gambler_id, status, games_played, wins, losses, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (gambler_id, status, games, wins, losses, started_at, ended_at))
        conn.commit()
        session_id = cursor.lastrowid
        cursor.close(); conn.close()
        return session_id

    def _update_session(self, session_id, status, games, wins, losses, ended_at):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions SET status=%s, games_played=%s, wins=%s, losses=%s, ended_at=%s
            WHERE id=%s
        """, (status, games, wins, losses, ended_at, session_id))
        conn.commit()
        cursor.close(); conn.close()

    def start(self, gambler_id):
        row = self._get_gambler(gambler_id)
        session_id = self._save_session(
            gambler_id, "ACTIVE", 0, 0, 0, datetime.now()
        )
        print(f"  Session #{session_id} started  |  Stake: {float(row['stake']):.2f}  |  Win: {float(row['win_threshold']):.2f}  |  Loss: {float(row['loss_threshold']):.2f}")
        return session_id

    def play_games(self, gambler_id, session_id, count, bet_amount, win_probability=0.5):
        print(f"\n  Playing {count} games (bet: {bet_amount:.2f} each)...\n")
        row = self._get_gambler(gambler_id)
        stake     = float(row["stake"])
        win_t     = float(row["win_threshold"])
        loss_t    = float(row["loss_threshold"])
        games = wins = losses = 0
        end_reason = "MANUAL"

        for i in range(1, count + 1):
            won = random.random() < win_probability
            stake = stake + bet_amount if won else stake - bet_amount
            self._update_stake(gambler_id, stake, won)
            games += 1
            if won:
                wins += 1
            else:
                losses += 1

            result = "WIN " if won else "LOSS"
            print(f"  Game {i:>2}  {result}  |  Stake: {stake:.2f}")

            if stake >= win_t:
                end_reason = "WIN_LIMIT"
                print(f"\n  Win threshold reached! ({stake:.2f} >= {win_t:.2f})")
                break
            if stake <= loss_t:
                end_reason = "LOSS_LIMIT"
                print(f"\n  Loss threshold reached! ({stake:.2f} <= {loss_t:.2f})")
                break

        return games, wins, losses, end_reason, stake

    def pause(self, session_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET status='PAUSED' WHERE id=%s", (session_id,))
        conn.commit()
        cursor.close(); conn.close()
        print(f"  Session #{session_id} paused.")

    def resume(self, session_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET status='ACTIVE' WHERE id=%s", (session_id,))
        conn.commit()
        cursor.close(); conn.close()
        print(f"  Session #{session_id} resumed.")

    def end(self, session_id, games, wins, losses, end_reason):
        status_map = {
            "WIN_LIMIT":  "ENDED_WIN",
            "LOSS_LIMIT": "ENDED_LOSS",
            "MANUAL":     "ENDED_MANUAL",
        }
        status = status_map.get(end_reason, "ENDED_MANUAL")
        self._update_session(session_id, status, games, wins, losses, datetime.now())
        win_rate = (wins / games * 100) if games > 0 else 0
        print(f"\n  Session #{session_id} ended  |  Reason: {end_reason}")
        print(f"  Games: {games}  |  Wins: {wins}  |  Losses: {losses}  |  Win Rate: {win_rate:.1f}%")

    def get_session_summary(self, session_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sessions WHERE id=%s", (session_id,))
        row = cursor.fetchone()
        cursor.close(); conn.close()
        if not row:
            print("  Session not found."); return
        duration = ""
        if row["ended_at"] and row["started_at"]:
            secs = int((row["ended_at"] - row["started_at"]).total_seconds())
            duration = f"{secs}s"
        print(f"\n  Summary for Session #{session_id}")
        print(f"  Status: {row['status']}  |  Duration: {duration or 'ongoing'}")
        print(f"  Games: {row['games_played']}  |  Wins: {row['wins']}  |  Losses: {row['losses']}")
