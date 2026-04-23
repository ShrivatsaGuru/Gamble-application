class ValidationError(Exception):
    pass


class InputValidator:

    def __init__(self, min_stake=50.0, max_stake=100000.0, min_bet=1.0, max_bet=10000.0):
        self.min_stake = min_stake
        self.max_stake = max_stake
        self.min_bet   = min_bet
        self.max_bet   = max_bet

    def validate_initial_stake(self, stake):
        errors = []
        if stake is None:
            errors.append("Stake cannot be None.")
        elif not isinstance(stake, (int, float)) or stake != stake:
            errors.append("Stake must be a valid number.")
        elif stake <= 0:
            errors.append("Stake must be positive.")
        elif stake < self.min_stake:
            errors.append(f"Stake {stake} is below minimum ({self.min_stake}).")
        elif stake > self.max_stake:
            errors.append(f"Stake {stake} exceeds maximum ({self.max_stake}).")
        return errors

    def validate_bet_amount(self, bet, current_stake):
        errors = []
        if bet is None or not isinstance(bet, (int, float)):
            errors.append("Bet must be a valid number.")
        elif bet <= 0:
            errors.append("Bet must be positive.")
        elif bet < self.min_bet:
            errors.append(f"Bet {bet} is below minimum ({self.min_bet}).")
        elif bet > self.max_bet:
            errors.append(f"Bet {bet} exceeds maximum allowed bet ({self.max_bet}).")
        elif bet > current_stake:
            errors.append(f"Bet {bet} exceeds current stake ({current_stake}).")
        return errors

    def validate_limits(self, stake, upper, lower):
        errors = []
        if lower < 0:
            errors.append("Loss threshold cannot be negative.")
        if upper <= lower:
            errors.append(f"Win threshold ({upper}) must be greater than loss threshold ({lower}).")
        if not (lower < stake < upper):
            errors.append(f"Initial stake ({stake}) must be between loss ({lower}) and win ({upper}) thresholds.")
        return errors

    def validate_probability(self, prob):
        errors = []
        if prob is None or not isinstance(prob, (int, float)) or prob != prob:
            errors.append("Probability must be a valid number.")
        elif prob < 0.0 or prob > 1.0:
            errors.append(f"Probability {prob} must be between 0.0 and 1.0.")
        return errors

    def validate_stake_non_negative(self, stake):
        errors = []
        if stake < 0:
            errors.append(f"Stake cannot be negative (got {stake}).")
        return errors

    def parse_number(self, text):
        try:
            value = float(text.strip())
            if value != value:
                raise ValidationError("Value is NaN.")
            if value == float("inf") or value == float("-inf"):
                raise ValidationError("Value cannot be infinite.")
            return value
        except (ValueError, AttributeError):
            raise ValidationError(f"'{text}' is not a valid number.")

    def check(self, errors):
        if errors:
            for e in errors:
                print(f"  Validation Error: {e}")
            return False
        print("  OK")
        return True
