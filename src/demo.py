from db import init_db
from gambler_profile_service import GamblerProfileService
from stake_management_service import StakeManagementService

def main():
    init_db()
    profile_svc = GamblerProfileService()
    stake_svc   = StakeManagementService()

    print("\n========== USE CASE 1: Gambler Profile Management ==========\n")

    # 1. Create
    print("-- 1. Create Gambler --")
    gid = profile_svc.create("Alice", "alice@example.com", 200.0, 400.0, 50.0)

    # 2. Update
    print("\n-- 2. Update Gambler --")
    profile_svc.update(gid, name="Alice Smith", win_threshold=450.0)

    # 3. Retrieve
    print("\n-- 3. Retrieve Statistics --")
    profile_svc.retrieve(gid)

    # 4. Validate
    print("\n-- 4. Validate Eligibility --")
    profile_svc.validate(gid)

    print("\n========== USE CASE 2: Stake Management Operations ==========\n")

    # 1. Initialize stake record
    print("-- 1. Initialize Stake --")
    stake_svc.initialize(gid, 200.0)

    # 2. Track current stake
    print("\n-- 2. Track Stake --")
    stake_svc.track(gid)

    # 3. Simulate some bet outcomes
    print("\n-- 3. Calculate Stake After Bets --")
    stake_svc.calculate(gid, 30.0, won=True)
    stake_svc.calculate(gid, 50.0, won=False)
    stake_svc.calculate(gid, 20.0, won=True)
    stake_svc.calculate(gid, 80.0, won=False)

    # 4. Monitor fluctuations
    print("\n-- 4. Monitor Fluctuations --")
    stake_svc.monitor(gid)

    # 5. Validate boundaries
    print("\n-- 5. Validate Boundaries --")
    stake_svc.validate_boundaries(gid)

    # Deposit & Withdraw
    print("\n-- Deposit & Withdraw --")
    stake_svc.deposit(gid, 100.0)
    stake_svc.withdraw(gid, 40.0)

    # 6. Full report
    print("\n-- 6. Stake History Report --")
    stake_svc.report(gid)

    # UC1 Reset
    print("\n-- UC1: Reset for New Session --")
    profile_svc.reset(gid, new_stake=300.0)
    stake_svc.initialize(gid, 300.0)

if __name__ == "__main__":
    main()