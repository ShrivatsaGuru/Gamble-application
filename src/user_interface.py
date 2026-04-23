import random
from input_validator import InputValidator


class UserInterface:

    def __init__(self):
        self.validator = InputValidator()

    def display_status(self, name, stake, win_threshold, loss_threshold, games, wins, losses):
        win_rate = f"{wins / games * 100:.1f}%" if games > 0 else "N/A"
        print(f"\n  Player   : {name}")
        print(f"  Stake    : {stake:.2f}  (Win: {win_threshold:.2f} | Loss: {loss_threshold:.2f})")
        print(f"  Games    : {games}  |  Wins: {wins}  |  Losses: {losses}  |  Win Rate: {win_rate}")

    def prompt_bet(self, current_stake):
        while True:
            raw = input(f"\n  Enter bet amount (stake: {current_stake:.2f}): ").strip()
            try:
                amount = self.validator.parse_number(raw)
            except Exception as e:
                print(f"  {e}")
                continue
            errors = self.validator.validate_bet_amount(amount, current_stake)
            if errors:
                for e in errors:
                    print(f"  {e}")
            else:
                return amount

    def display_outcome(self, won, bet, stake_before, stake_after):
        result = "You won!" if won else "You lost."
        change = stake_after - stake_before
        arrow  = f"+{change:.2f}" if change >= 0 else f"{change:.2f}"
        print(f"\n  {result}  Bet: {bet:.2f}  |  {stake_before:.2f} -> {stake_after:.2f}  ({arrow})")

    def display_summary(self, name, initial_stake, final_stake, games, wins, losses):
        net = final_stake - initial_stake
        win_rate = f"{wins / games * 100:.1f}%" if games > 0 else "N/A"
        print(f"\n  Session Summary for {name}")
        print(f"  {'─' * 35}")
        print(f"  Games played : {games}")
        print(f"  Wins / Losses: {wins} / {losses}  ({win_rate} win rate)")
        print(f"  Started with : {initial_stake:.2f}")
        print(f"  Ended with   : {final_stake:.2f}")
        print(f"  Net result   : {net:+.2f}")

    def main_menu(self):
        print("\n  What would you like to do?")
        print("  1. View status")
        print("  2. Place a bet")
        print("  3. Auto-play (5 games)")
        print("  4. End session")
        return input("  Choice: ").strip()

    def run_demo(self):
        name          = "Alice"
        initial_stake = 300.0
        stake         = initial_stake
        win_threshold = 600.0
        loss_threshold = 100.0
        games = wins = losses = 0
        bet_amount = 30.0
        active = True

        print(f"\n  Starting interactive session for {name}")
        print(f"  Stake: {stake:.2f}  |  Win at: {win_threshold:.2f}  |  Lose at: {loss_threshold:.2f}")

        while active:
            choice = self.main_menu()

            if choice == "1":
                self.display_status(name, stake, win_threshold, loss_threshold, games, wins, losses)

            elif choice == "2":
                amount = self.prompt_bet(stake)
                won = random.random() < 0.5
                stake_after = stake + amount if won else stake - amount
                self.display_outcome(won, amount, stake, stake_after)
                stake = stake_after
                games += 1
                if won: wins += 1
                else:   losses += 1

                if stake >= win_threshold:
                    print("\n  Win threshold reached! Great job.")
                    active = False
                elif stake <= loss_threshold:
                    print("\n  Loss threshold reached. Session over.")
                    active = False

            elif choice == "3":
                print("\n  Auto-playing 5 games...\n")
                for i in range(1, 6):
                    if stake < 10:
                        print("  Stake too low to continue."); break
                    won = random.random() < 0.5
                    stake_after = stake + bet_amount if won else stake - bet_amount
                    result = "WIN " if won else "LOSS"
                    print(f"  Game {i}  {result}  {stake:.2f} -> {stake_after:.2f}")
                    stake = stake_after
                    games += 1
                    if won: wins += 1
                    else:   losses += 1

                    if stake >= win_threshold:
                        print("\n  Win threshold reached!"); active = False; break
                    if stake <= loss_threshold:
                        print("\n  Loss threshold reached!"); active = False; break

            elif choice == "4":
                print("\n  Ending session...")
                active = False

            else:
                print("  Invalid choice, try again.")

        self.display_summary(name, initial_stake, stake, games, wins, losses)
