class BettingPreferences:
    def __init__(self, min_bet=10, max_bet=500, auto_play=False, session_limit=100):
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.auto_play = auto_play
        self.session_limit = session_limit

    def __str__(self):
        return f"MinBet={self.min_bet}, MaxBet={self.max_bet}, AutoPlay={self.auto_play}"


class GamblerStatistics:
    def __init__(self, gambler):
        self.name = gambler["name"]
        self.stake = gambler["stake"]
        self.win_threshold = gambler["win_threshold"]
        self.loss_threshold = gambler["loss_threshold"]
        self.total_bets = gambler["total_bets"]
        self.wins = gambler["wins"]
        self.losses = gambler["losses"]
        self.win_rate = (self.wins / self.total_bets * 100) if self.total_bets > 0 else 0
        self.net = self.stake - gambler["initial_stake"]

    def __str__(self):
        return (
            f"--- Statistics for {self.name} ---\n"
            f"Stake: {self.stake} | Net: {self.net:+.2f}\n"
            f"Bets: {self.total_bets} | Wins: {self.wins} | Losses: {self.losses}\n"
            f"Win Rate: {self.win_rate:.1f}%\n"
            f"Win Threshold: {self.win_threshold} | Loss Threshold: {self.loss_threshold}"
        )