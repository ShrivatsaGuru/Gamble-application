from db import init_db
from gambler_profile_service import GamblerProfileService

def main():
    # Setup DB
    init_db()
    service = GamblerProfileService()

    print("\n=== USE CASE 1: Gambler Profile Management ===\n")

    # 1. Create
    print("-- 1. Creating Gambler --")
    gid = service.create(
        name="Alice",
        email="alice@example.com",
        stake=200.0,
        win_threshold=400.0,
        loss_threshold=50.0
    )

    # 2. Update
    print("\n-- 2. Updating Gambler --")
    service.update(gid, name="Alice Smith", win_threshold=450.0)

    # 3. Retrieve
    print("\n-- 3. Retrieving Statistics --")
    service.retrieve(gid)

    # 4. Validate
    print("\n-- 4. Validating Eligibility --")
    service.validate(gid)

    # 5. Reset
    print("\n-- 5. Resetting for New Session --")
    service.reset(gid, new_stake=300.0)

    print("\n-- Final Status After Reset --")
    service.retrieve(gid)

if __name__ == "__main__":
    main()