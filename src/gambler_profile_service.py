from db import get_connection
from gambler_profile import GamblerStatistics

MIN_STAKE = 50.0

class GamblerProfileService:

    
    def create(self, name, email, stake, win_threshold, loss_threshold):
        if stake < MIN_STAKE:
            raise ValueError(f"Initial stake must be at least {MIN_STAKE}")
        if win_threshold <= stake:
            raise ValueError("Win threshold must be greater than initial stake")
        if loss_threshold >= stake:
            raise ValueError("Loss threshold must be less than initial stake")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gamblers (name, email, stake, initial_stake, win_threshold, loss_threshold)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, stake, stake, win_threshold, loss_threshold))
        conn.commit()
        gambler_id = cursor.lastrowid
        cursor.close()
        conn.close()
        print(f"Gambler '{name}' created with ID {gambler_id}.")
        return gambler_id

 
    def update(self, gambler_id, name=None, email=None, win_threshold=None, loss_threshold=None):
        fields, values = [], []
        if name:
            fields.append("name=%s"); values.append(name)
        if email:
            fields.append("email=%s"); values.append(email)
        if win_threshold:
            fields.append("win_threshold=%s"); values.append(win_threshold)
        if loss_threshold:
            fields.append("loss_threshold=%s"); values.append(loss_threshold)
        if not fields:
            print("Nothing to update."); return

        values.append(gambler_id)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE gamblers SET {', '.join(fields)} WHERE id=%s", values)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Gambler ID {gambler_id} updated. Here are the new details:")
        self.retrieve(gambler_id)


    def retrieve(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            print("Gambler not found."); return None
        stats = GamblerStatistics(row)
        print(stats)
        return stats


    def validate(self, gambler_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            print("Gambler not found."); return False
        if not row["active"]:
            print("Account is inactive."); return False
        if row["stake"] < MIN_STAKE:
            print(f"Stake too low (min {MIN_STAKE})."); return False
        print("Gambler is eligible to play.")
        return True

   
    def reset(self, gambler_id, new_stake):
        if new_stake < MIN_STAKE:
            raise ValueError(f"New stake must be at least {MIN_STAKE}")
        win_threshold = new_stake * 2
        loss_threshold = new_stake * 0.5
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE gamblers
            SET stake=%s, initial_stake=%s, win_threshold=%s, loss_threshold=%s,
                total_bets=0, wins=0, losses=0, active=TRUE
            WHERE id=%s
        """, (new_stake, new_stake, win_threshold, loss_threshold, gambler_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Gambler ID {gambler_id} reset. New stake={new_stake}, Win={win_threshold}, Loss={loss_threshold}")
