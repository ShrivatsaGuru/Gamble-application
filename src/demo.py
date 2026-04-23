from db import init_db
from gambler_profile_service import GamblerProfileService
from stake_management_service import StakeManagementService
from betting_service import BettingService, FixedAmountStrategy, PercentageStrategy, MartingaleStrategy
from game_session_service import GameSessionService


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


if __name__ == "__main__":
    main()