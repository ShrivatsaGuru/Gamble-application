from db import init_db
from gambler_profile_service import GamblerProfileService
from stake_management_service import StakeManagementService
from betting_service import BettingService, FixedAmountStrategy, PercentageStrategy, MartingaleStrategy
from game_session_service import GameSessionService
from win_loss_calculator import WinLossCalculator
from input_validator import InputValidator
from user_interface import UserInterface


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


def main():
    init_db()
    profile_svc = GamblerProfileService()
    stake_svc   = StakeManagementService()
    bet_svc     = BettingService()
    session_svc = GameSessionService()


    section("Use Case 1: Gambler Profile Management")

    print("\nCreate gambler")
    gid = profile_svc.create("Alice", "alice@example.com", 200.0, 400.0, 50.0)

    print("\nUpdate gambler")
    profile_svc.update(gid, name="Alice Smith", win_threshold=450.0)

    print("\nRetrieve statistics")
    profile_svc.retrieve(gid)

    print("\nValidate eligibility")
    profile_svc.validate(gid)


    section("Use Case 2: Stake Management Operations")

    print("\nInitialize stake")
    stake_svc.initialize(gid, 200.0)

    print("\nTrack current stake")
    stake_svc.track(gid)

    print("\nCalculate stake after bets")
    stake_svc.calculate(gid, 30.0, won=True)
    stake_svc.calculate(gid, 50.0, won=False)
    stake_svc.calculate(gid, 20.0, won=True)
    stake_svc.calculate(gid, 80.0, won=False)

    print("\nMonitor fluctuations")
    stake_svc.monitor(gid)

    print("\nValidate boundaries")
    stake_svc.validate_boundaries(gid)

    print("\nDeposit and withdraw")
    stake_svc.deposit(gid, 100.0)
    stake_svc.withdraw(gid, 40.0)

    print("\nStake history report")
    stake_svc.report(gid)

    print("\nReset gambler for new session")
    profile_svc.reset(gid, new_stake=300.0)
    stake_svc.initialize(gid, 300.0)


    section("Use Case 3: Betting Mechanism")

    print("\nPlace a single manual bet")
    bet_svc.place_bet(gid, 25.0, win_probability=0.5)

    print("\nFixed amount strategy (bet 30 each time)")
    fixed = FixedAmountStrategy(30.0)
    bet_svc.place_bet_with_strategy(gid, fixed, win_probability=0.5)

    print("\nPercentage strategy (bet 10% of stake)")
    pct = PercentageStrategy(10)
    bet_svc.place_bet_with_strategy(gid, pct, win_probability=0.5)

    print("\nMartingale strategy (5 consecutive bets)")
    martingale = MartingaleStrategy(base_amount=20.0)
    bet_svc.place_consecutive_bets(gid, martingale, count=5, win_probability=0.5)

    print("\nBet history")
    bet_svc.get_bet_history(gid)


    section("Use Case 4: Game Session Management")

    print("\nStart a new session")
    sid = session_svc.start(gid)

    print("\nPlay 5 games (bet 30 each, 50% win chance)")
    games, wins, losses, reason, final_stake = session_svc.play_games(
        gid, sid, count=5, bet_amount=30.0, win_probability=0.5
    )

    print("\nPause the session")
    session_svc.pause(sid)

    print("\nResume the session")
    session_svc.resume(sid)

    print("\nPlay 3 more games")
    g2, w2, l2, reason, final_stake = session_svc.play_games(
        gid, sid, count=3, bet_amount=30.0, win_probability=0.5
    )
    games += g2; wins += w2; losses += l2

    print("\nEnd the session")
    session_svc.end(sid, games, wins, losses, reason)

    print("\nSession summary")
    session_svc.get_session_summary(sid)


    section("Use Case 5: Win/Loss Calculation")

    initial_stake = 500.0
    stake = initial_stake
    calc = WinLossCalculator(win_probability=0.5)

    print("\nPlaying 10 games (bet 50 each, odds 2x)\n")
    for i in range(1, 11):
        won, stake, result = calc.play(bet_amount=50.0, current_stake=stake, odds=2.0)
        print(f"  Game {i:>2}  {result}  |  Balance: {stake:.2f}")
        if stake < 50:
            print("  Not enough stake to continue.")
            break

    print("\nRunning totals and statistics")
    calc.print_stats()

    print("\nBalance history")
    calc.print_balance_history(initial_stake)


    section("Use Case 6: Input Validation and Error Handling")

    v = InputValidator()

    print("\nValidate initial stake")
    print("  stake=300    ", end=""); v.check(v.validate_initial_stake(300.0))
    print("  stake=-50    ", end=""); v.check(v.validate_initial_stake(-50.0))
    print("  stake=10     ", end=""); v.check(v.validate_initial_stake(10.0))

    print("\nValidate bet amount (current stake = 200)")
    print("  bet=50       ", end=""); v.check(v.validate_bet_amount(50.0, 200.0))
    print("  bet=250      ", end=""); v.check(v.validate_bet_amount(250.0, 200.0))
    print("  bet=0        ", end=""); v.check(v.validate_bet_amount(0.0, 200.0))

    print("\nValidate win/loss limits (stake=200)")
    print("  upper=400, lower=50  ", end=""); v.check(v.validate_limits(200.0, 400.0, 50.0))
    print("  upper=100, lower=50  ", end=""); v.check(v.validate_limits(200.0, 100.0, 50.0))
    print("  upper=400, lower=-10 ", end=""); v.check(v.validate_limits(200.0, 400.0, -10.0))

    print("\nValidate probability")
    print("  prob=0.6     ", end=""); v.check(v.validate_probability(0.6))
    print("  prob=1.5     ", end=""); v.check(v.validate_probability(1.5))
    print("  prob=-0.1    ", end=""); v.check(v.validate_probability(-0.1))

    print("\nValidate non-negative stake")
    print("  stake=0      ", end=""); v.check(v.validate_stake_non_negative(0.0))
    print("  stake=-20    ", end=""); v.check(v.validate_stake_non_negative(-20.0))

    print("\nParse numeric input")
    for raw in ["  42.5 ", "abc", "", "inf"]:
        try:
            val = v.parse_number(raw)
            print(f"  '{raw.strip()}' -> {val}")
        except Exception as e:
            print(f"  '{raw.strip()}' -> Error: {e}")


    section("Use Case 7: User Interaction")

    ui = UserInterface()
    ui.run_demo()


if __name__ == "__main__":
    main()