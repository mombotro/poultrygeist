import random
import os
from collections import Counter

# --- Game Configuration ---
INITIAL_CASH = 15
INITIAL_FEED = 10
INITIAL_CHICKENS = [
    {"breed": "Pearl Leghorn", "tier": "Bronze"},
    {"breed": "Pearl Leghorn", "tier": "Bronze"},
]
TURNS_PER_SEASON = 5
EVENT_CHANCE = 0.4 # 40% chance of an event each turn
HATCHING_COST = 5 # eggs
HATCHING_SUCCESS_RATE = 0.5

# --- Coop Upgrade Definitions ---
COOP_UPGRADES = {
    1: {"name": "Basic Coop", "capacity": 5, "cost": 0},
    2: {"name": "Expanded Coop", "capacity": 8, "cost": 50},
    3: {"name": "Deluxe Coop", "capacity": 12, "cost": 150},
    4: {"name": "Automated Coop", "capacity": 15, "cost": 300},
}

# --- Victory Conditions ---
VICTORY_EGGS = 20
VICTORY_CASH = 50
VICTORY_MEAT = 30

# --- Ghost Exchange Rates ---
GHOST_EXCHANGE_RATES = {
    "Bronze": 5,
    "Silver": 3,
    "Gold": 1,
}

# --- Chicken Definitions ---
CHICKEN_STATS = {
    "Pearl Leghorn": {"eggs": 2, "meat": 1, "feed": 1, "health": 1, "cash": 2, "tier": "Bronze"},
    "Duck": {"eggs": 4, "meat": 4, "feed": 3, "health": 2, "cash": 10, "tier": "Silver"},
    "Buff Orpington": {"eggs": 8, "meat": 3, "feed": 3, "health": 2, "cash": 25, "tier": "Gold"},
}

# --- Season Definitions ---
SEASONS = {
    "Spring": {"hatching_bonus": 0.25, "new_chicken_discount": 0.25, "message": "Spring is here! It's a great time to hatch new chicks."},
    "Summer": {"egg_increase": 0.25, "feed_increase": 0.20, "message": "The summer sun is boosting egg production, but the chickens are eating more."},
    "Fall": {"meat_bonus": 0.25, "market_increase": 0.10, "message": "It's harvest season! Meat yields are up and market prices are high."},
    "Winter": {"feed_cost_increase": 0.30, "egg_reduction": 0.15, "illness_chance": 0.10, "message": "Winter has arrived. Feed is more expensive and egg production is down."}
}

# --- Event Definitions ---
EVENTS = {
    "Coldsnap": {"effect": "lose_chicken", "message": "A sudden coldsnap has hit! One of your chickens with the lowest health has died."},
    "Predation": {"effect": "lose_chicken", "message": "A predator got into the coop! One of your chickens with the lowest health was taken."},
    "Fertile Hatch": {"effect": "gain_chicken", "message": "One of your chickens laid a fertile egg! You have a new Bronze chicken."},
    "Market Boom": {"effect": "cash_bonus", "message": "The market is booming! You receive a bonus of 10 cash."},
    "Good Feed": {"effect": "feed_bonus", "message": "You found a great deal on feed! You receive 10 extra feed."},
    "Egg Shortage": {"effect": "double_egg_value", "message": "A local egg shortage has doubled the value of your eggs for this turn!"},
}


class Chicken:
    def __init__(self, breed, tier, purchase_price=None):
        stats = CHICKEN_STATS[breed]
        self.breed = breed
        self.tier = tier
        self.eggs_per_turn = stats["eggs"]
        self.meat_value = stats["meat"]
        self.feed_consumption = stats["feed"]
        self.base_health = stats["health"]
        self.current_health = self.base_health
        self.cash_value = stats["cash"]
        # Track what was actually paid for this chicken
        self.purchase_price = purchase_price if purchase_price is not None else stats["cash"]

    def get_sale_price(self, season):
        # Sell for 80% of purchase price, with potential seasonal bonus
        base_sale_price = int(self.purchase_price * 0.8)
        if season == "Fall":
            base_sale_price = int(base_sale_price * (1 + SEASONS["Fall"]["market_increase"]))
        return max(1, base_sale_price)  # Minimum 1 cash

    def __str__(self):
        return f'{self.tier} {self.breed} (Health: {self.current_health})'

class GhostChicken:
    def __init__(self, original_tier):
        self.original_tier = original_tier

    def __str__(self):
        return f"{self.original_tier} Ghost"

class GameState:
    def __init__(self):
        self.cash = INITIAL_CASH
        self.banked_cash = 0
        self.feed = INITIAL_FEED
        self.eggs = 0
        self.meat = 0
        # Initial chickens get their base cash value as purchase price
        self.chickens = [Chicken(c["breed"], c["tier"], CHICKEN_STATS[c["breed"]]["cash"]) for c in INITIAL_CHICKENS]
        self.graveyard = [] # Stores fallen Chicken objects
        self.ghost_chickens = [] # Stores GhostChicken objects
        self.turn = 1
        self.year = 1
        self.season = "Spring"
        self.meat_harvested_this_year = 0
        self.double_eggs_active = False
        self.egg_price_multiplier = 1.0
        self.coop_level = 1

    def get_coop_capacity(self):
        return COOP_UPGRADES[self.coop_level]["capacity"]

    def add_chicken(self, breed, tier, purchase_price=None):
        if len(self.chickens) < self.get_coop_capacity():
            self.chickens.append(Chicken(breed, tier, purchase_price))
            return True
        return False

    def next_turn(self):
        self.turn += 1
        if (self.turn - 1) % TURNS_PER_SEASON == 0:
            current_season_index = list(SEASONS.keys()).index(self.season)
            if current_season_index == 3:
                self.season = "Spring"
                self.year += 1
                self.meat_harvested_this_year = 0
            else:
                self.season = list(SEASONS.keys())[current_season_index + 1]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_intro():
    clear_screen()
    print("""
          ,~.
       ,-'__ `-, 
      {,-'  `. `.         .---.
     ,( o )   `-}__     /     \\
    <=.) (         `-.__|  () |
      (   )                .__/
       `-'|     \\     \\    |
          \\     (    _)    |
           \\_    \\___)     /
             \\____      __/
                  \\\\```\\\\\
                  ((   ((
                __//_ _//_
""")
    print("--- Welcome to Poultry Geist! ---")
    print("Build a thriving poultry farm by managing your flock and resources.")
    print("\nYour goal is to achieve the following in a single year:")
    print(f"- Produce {VICTORY_EGGS} eggs in a single turn")
    print(f"- Bank {VICTORY_CASH} cash")
    print(f"- Harvest {VICTORY_MEAT} meat")
    print("\nWhen your chickens die, their spirits linger. Collect enough spirits")
    print("to summon powerful Ghost Chickens with unique abilities.")
    print("\nGood luck, farmer!")
    input("\nPress Enter to begin...")

def display_game_state(state, messages):
    clear_screen()
    print("--- Poultry Geist ---")
    print(f"Year: {state.year} | Turn: {state.turn} | Season: {state.season}")
    print("--- Resources ---")
    print(f"Cash: ${state.cash} | Banked: ${state.banked_cash}/{VICTORY_CASH} | Feed: {state.feed} | Eggs: {state.eggs} | Meat: {state.meat}")
    print(f"Meat This Year: {state.meat_harvested_this_year}/{VICTORY_MEAT}")
    print("--- Farm ---")
    coop_name = COOP_UPGRADES[state.coop_level]["name"]
    print(f"{coop_name}: {len(state.chickens)}/{state.get_coop_capacity()}")
    print("Chickens:")
    if state.chickens:
        for chicken in state.chickens:
            print(f"  - {chicken}")
    else:
        print("  - No chickens.")
    graveyard_counts = Counter(c.tier for c in state.graveyard)
    print("Graveyard:")
    print(f"  - Bronze: {graveyard_counts['Bronze']}, Silver: {graveyard_counts['Silver']}, Gold: {graveyard_counts['Gold']}")
    print("Ghosts:")
    if state.ghost_chickens:
        for ghost in state.ghost_chickens:
            print(f"  - {ghost}")
    else:
        print("  - No ghosts.")
    print("-" * 20)
    for msg in messages:
        print(msg)
    print("-" * 20)

def check_victory_conditions(state, eggs_this_turn):
    if eggs_this_turn >= VICTORY_EGGS and state.banked_cash >= VICTORY_CASH and state.meat_harvested_this_year >= VICTORY_MEAT:
        print("\nCongratulations! You have built a thriving poultry farm and won the game!")
        return True
    return False

def check_game_over(state):
    min_price = min(stats['cash'] for stats in CHICKEN_STATS.values())
    if not state.chickens and state.cash < min_price:
        print("\n--- GAME OVER ---")
        print("You have no chickens and not enough cash to buy a new one.")
        print("Your farm has gone bankrupt.")
        return True
    return False

def lose_chicken(game_state, messages):
    if not game_state.chickens:
        return

    for ghost in game_state.ghost_chickens:
        if ghost.original_tier == "Bronze":
            messages.append("A Bronze Ghost sacrificed itself to protect a chicken from dying!")
            game_state.ghost_chickens.remove(ghost)
            return

    weakest_chicken = min(game_state.chickens, key=lambda c: c.current_health)
    game_state.chickens.remove(weakest_chicken)
    game_state.graveyard.append(weakest_chicken)
    messages.append(f"A {weakest_chicken} has died!")

def process_turn_start(game_state):
    messages = []
    game_state.egg_price_multiplier = 1.0

    gold_ghost_count = sum(1 for g in game_state.ghost_chickens if g.original_tier == "Gold")
    if gold_ghost_count > 0:
        messages.append(f"Your {gold_ghost_count} Gold Ghost(s) grant +{2*gold_ghost_count} health to all chickens.")
    for chicken in game_state.chickens:
        chicken.current_health = chicken.base_health + (2 * gold_ghost_count)

    if (game_state.turn - 1) % TURNS_PER_SEASON == 0 and game_state.turn > 1:
        messages.append(f"--- {game_state.season.upper()} ---")
        messages.append(SEASONS[game_state.season]["message"])

    if random.random() < EVENT_CHANCE:
        event, event_data = random.choice(list(EVENTS.items()))
        messages.append(f"EVENT: {event} - {event_data['message']}")
        effect = event_data['effect']
        if effect == 'lose_chicken':
            lose_chicken(game_state, messages)
        elif effect == 'gain_chicken':
            if game_state.add_chicken("Pearl Leghorn", "Bronze", CHICKEN_STATS["Pearl Leghorn"]["cash"]):
                messages.append("A new Pearl Leghorn appeared!")
            else:
                messages.append("A new chicken appeared but your coop is full!")
        elif effect == 'cash_bonus':
            game_state.cash += 10
        elif effect == 'feed_bonus':
            game_state.feed += 10
        elif effect == 'double_egg_value':
            game_state.egg_price_multiplier = 2.0

    egg_multiplier = 2.0 if game_state.double_eggs_active else 1.0
    if game_state.season == "Summer":
        egg_multiplier += SEASONS["Summer"]["egg_increase"]
    if game_state.season == "Winter":
        egg_multiplier -= SEASONS["Winter"]["egg_reduction"]

    bronze_ghost_count = sum(1 for g in game_state.ghost_chickens if g.original_tier == "Bronze")
    base_eggs = 0
    for chicken in game_state.chickens:
        bonus = 0
        if chicken.tier == "Bronze" and bronze_ghost_count > 0:
            bonus = bronze_ghost_count
        base_eggs += chicken.eggs_per_turn + bonus

    new_eggs = int(base_eggs * egg_multiplier)
    game_state.eggs += new_eggs
    messages.append(f"Your chickens produced {new_eggs} eggs.")
    if game_state.double_eggs_active:
        messages.append("The Silver Ghost's power was consumed to double your egg production!")
        game_state.double_eggs_active = False

    return messages, new_eggs

def play_game():
    game_state = GameState()

    while True:
        turn_messages, eggs_this_turn = process_turn_start(game_state)

        if check_victory_conditions(game_state, eggs_this_turn):
            display_game_state(game_state, turn_messages)
            break

        while True:
            display_game_state(game_state, turn_messages)
            turn_messages = [] # Clear messages after displaying them once

            if check_game_over(game_state):
                return

            print("\n--- Actions ---")
            print("1. Buy Chicken")
            print("2. Sell Chicken")
            print("3. Harvest Chicken for Meat")
            print("4. Buy Feed")
            print("5. Sell Eggs")
            print("6. Hatch Eggs")
            print("7. Bank Cash")
            print("8. Upgrade Coop")
            print("9. Manage Ghosts")
            print("10. Use Ghost Ability")
            print("11. Next Turn")
            action = input("Choose an action: ")

            if action == "1":
                print("\n--- Market ---")
                for i, (breed, stats) in enumerate(CHICKEN_STATS.items()):
                    price = stats['cash']
                    if game_state.season == "Spring":
                        price = int(price * (1 - SEASONS["Spring"]["new_chicken_discount"]))
                    price = max(1, price)
                    print(f"{i+1}. {stats['tier']} {breed} - ${price}")
                print("0. Go Back")
                try:
                    choice = int(input("Choose a chicken to buy: "))
                    if choice == 0:
                        continue
                    breed_to_buy = list(CHICKEN_STATS.keys())[choice - 1]
                    cost = CHICKEN_STATS[breed_to_buy]["cash"]
                    if game_state.season == "Spring":
                        cost = int(cost * (1 - SEASONS["Spring"]["new_chicken_discount"]))
                    cost = max(1, cost)

                    if game_state.cash >= cost:
                        if game_state.add_chicken(breed_to_buy, CHICKEN_STATS[breed_to_buy]["tier"], cost):
                            game_state.cash -= cost
                            turn_messages.append(f"You bought a {breed_to_buy} for ${cost}.")
                        else:
                            turn_messages.append("Your coop is full!")
                    else:
                        turn_messages.append("Not enough cash.")
                except (ValueError, IndexError):
                    turn_messages.append("Invalid choice.")

            elif action == "2":
                if not game_state.chickens:
                    turn_messages.append("You have no chickens to sell.")
                else:
                    print("\n--- Your Chickens ---")
                    for i, chicken in enumerate(game_state.chickens):
                        sale_price = chicken.get_sale_price(game_state.season)
                        print(f"{i+1}. {chicken} - ${sale_price} (bought for ${chicken.purchase_price})")
                    print("0. Go Back")
                    try:
                        choice = int(input("Choose a chicken to sell: "))
                        if choice == 0:
                            continue
                        sold_chicken = game_state.chickens.pop(choice - 1)
                        sale_price = sold_chicken.get_sale_price(game_state.season)
                        game_state.cash += sale_price
                        turn_messages.append(f"You sold a {sold_chicken} for ${sale_price}.")
                    except (ValueError, IndexError):
                        turn_messages.append("Invalid choice.")

            elif action == "3":
                if not game_state.chickens:
                    turn_messages.append("You have no chickens to harvest.")
                else:
                    print("\n--- Harvest a Chicken ---")
                    for i, chicken in enumerate(game_state.chickens):
                        print(f"{i+1}. {chicken}")
                    print("0. Go Back")
                    try:
                        choice = int(input("Choose a chicken to harvest: "))
                        if choice == 0:
                            continue
                        harvested_chicken = game_state.chickens.pop(choice - 1)
                        game_state.graveyard.append(harvested_chicken)
                        meat_yield = harvested_chicken.meat_value
                        if game_state.season == "Fall":
                            meat_yield = int(meat_yield * (1 + SEASONS["Fall"]["meat_bonus"]))
                        game_state.meat += meat_yield
                        game_state.meat_harvested_this_year += meat_yield
                        turn_messages.append(f"You harvested a {harvested_chicken} for {meat_yield} meat.")
                    except (ValueError, IndexError):
                        turn_messages.append("Invalid choice.")

            elif action == "4":
                feed_price = 1.0
                if game_state.season == "Winter":
                    feed_price += SEASONS["Winter"]["feed_cost_increase"]
                try:
                    amount = int(input(f"How much feed to buy? (${feed_price:.2f} per unit): "))
                    cost = amount * feed_price
                    if amount > 0 and game_state.cash >= cost:
                        game_state.feed += amount
                        game_state.cash -= cost
                        turn_messages.append(f"You bought {amount} units of feed.")
                    else:
                        turn_messages.append("Invalid amount or not enough cash.")
                except ValueError:
                    turn_messages.append("Invalid input.")

            elif action == "5":
                if game_state.eggs <= 0:
                    turn_messages.append("You have no eggs to sell.")
                else:
                    egg_price = int(1 * game_state.egg_price_multiplier)
                    print(f"\nYou have {game_state.eggs} eggs. Current price: ${egg_price} per egg.")
                    try:
                        amount_to_sell = int(input(f"How many eggs to sell? (0 to cancel): "))
                        if 0 < amount_to_sell <= game_state.eggs:
                            earnings = amount_to_sell * egg_price
                            game_state.eggs -= amount_to_sell
                            game_state.cash += earnings
                            turn_messages.append(f"You sold {amount_to_sell} eggs for ${earnings}.")
                        elif amount_to_sell > game_state.eggs:
                            turn_messages.append("You don't have that many eggs.")
                    except ValueError:
                        turn_messages.append("Invalid amount.")

            elif action == "6":
                hatch_rate = HATCHING_SUCCESS_RATE
                if game_state.season == "Spring":
                    hatch_rate += SEASONS["Spring"]["hatching_bonus"]
                print(f"\nIt costs {HATCHING_COST} eggs to attempt to hatch a new chick.")
                print(f"Current success rate: {hatch_rate:.0%}")
                if game_state.eggs < HATCHING_COST:
                    turn_messages.append("You don't have enough eggs to attempt hatching.")
                else:
                    confirm = input("Attempt to hatch? (y/n): ").lower()
                    if confirm == 'y':
                        game_state.eggs -= HATCHING_COST
                        if random.random() < hatch_rate:
                            # Hatched chickens get base cash value as purchase price
                            if game_state.add_chicken("Pearl Leghorn", "Bronze", CHICKEN_STATS["Pearl Leghorn"]["cash"]):
                                turn_messages.append("Success! A new Pearl Leghorn chick has hatched!")
                            else:
                                turn_messages.append("The egg hatched, but your coop is full! The chick ran away.")
                        else:
                            turn_messages.append("The egg didn't hatch.")

            elif action == "7":
                print(f"\nYou have ${game_state.cash} to bank.")
                try:
                    amount_to_bank = int(input("How much to bank? (0 to cancel): "))
                    if 0 < amount_to_bank <= game_state.cash:
                        game_state.cash -= amount_to_bank
                        game_state.banked_cash += amount_to_bank
                        turn_messages.append(f"You banked ${amount_to_bank}.")
                    elif amount_to_bank > game_state.cash:
                        turn_messages.append("You don't have that much cash.")
                except ValueError:
                    turn_messages.append("Invalid amount.")

            elif action == "8":
                next_level = game_state.coop_level + 1
                if next_level not in COOP_UPGRADES:
                    turn_messages.append("Your coop is already max level!")
                else:
                    upgrade_cost = COOP_UPGRADES[next_level]["cost"]
                    upgrade_name = COOP_UPGRADES[next_level]["name"]
                    print(f"\nUpgrade to {upgrade_name} for ${upgrade_cost}?")
                    if game_state.cash < upgrade_cost:
                        turn_messages.append(f"You don't have enough cash. The {upgrade_name} costs ${upgrade_cost}.")
                    else:
                        confirm = input("Confirm upgrade? (y/n): ").lower()
                        if confirm == 'y':
                            game_state.cash -= upgrade_cost
                            game_state.coop_level = next_level
                            turn_messages.append(f"Congratulations! You've upgraded to the {upgrade_name}.")

            elif action == "9":
                graveyard_counts = Counter(c.tier for c in game_state.graveyard)
                print("\n--- Manage Ghosts ---")
                print("Exchange spirits of fallen chickens for Ghost Chickens.")
                print(f"1. Exchange {GHOST_EXCHANGE_RATES['Bronze']} Bronze spirits for 1 Bronze Ghost (You have: {graveyard_counts['Bronze']})")
                print(f"2. Exchange {GHOST_EXCHANGE_RATES['Silver']} Silver spirits for 1 Silver Ghost (You have: {graveyard_counts['Silver']})")
                print(f"3. Exchange {GHOST_EXCHANGE_RATES['Gold']} Gold spirit for 1 Gold Ghost (You have: {graveyard_counts['Gold']})")
                print("0. Go Back")
                choice = input("Choose an option: ")

                if choice == "1":
                    if graveyard_counts['Bronze'] >= GHOST_EXCHANGE_RATES['Bronze']:
                        removed_count = 0
                        new_graveyard = []
                        for chicken in game_state.graveyard:
                            if chicken.tier == 'Bronze' and removed_count < GHOST_EXCHANGE_RATES['Bronze']:
                                removed_count += 1
                            else:
                                new_graveyard.append(chicken)
                        game_state.graveyard = new_graveyard
                        game_state.ghost_chickens.append(GhostChicken("Bronze"))
                        turn_messages.append("You have created a Bronze Ghost!")
                    else:
                        turn_messages.append("Not enough Bronze spirits.")
                elif choice == "2":
                    if graveyard_counts['Silver'] >= GHOST_EXCHANGE_RATES['Silver']:
                        removed_count = 0
                        new_graveyard = []
                        for chicken in game_state.graveyard:
                            if chicken.tier == 'Silver' and removed_count < GHOST_EXCHANGE_RATES['Silver']:
                                removed_count += 1
                            else:
                                new_graveyard.append(chicken)
                        game_state.graveyard = new_graveyard
                        game_state.ghost_chickens.append(GhostChicken("Silver"))
                        turn_messages.append("You have created a Silver Ghost!")
                    else:
                        turn_messages.append("Not enough Silver spirits.")
                elif choice == "3":
                    if graveyard_counts['Gold'] >= GHOST_EXCHANGE_RATES['Gold']:
                        removed_count = 0
                        new_graveyard = []
                        for chicken in game_state.graveyard:
                            if chicken.tier == 'Gold' and removed_count < GHOST_EXCHANGE_RATES['Gold']:
                                removed_count += 1
                            else:
                                new_graveyard.append(chicken)
                        game_state.graveyard = new_graveyard
                        game_state.ghost_chickens.append(GhostChicken("Gold"))
                        turn_messages.append("You have created a Gold Ghost!")
                    else:
                        turn_messages.append("Not enough Gold spirits.")

            elif action == "10":
                print("\n--- Use Ghost Ability ---")
                usable_ghosts = [g for g in game_state.ghost_chickens if g.original_tier != "Bronze"]
                if not usable_ghosts:
                    turn_messages.append("No active ghost abilities available.")
                else:
                    for i, ghost in enumerate(usable_ghosts):
                        if ghost.original_tier == "Silver":
                            print(f"{i+1}. {ghost.original_tier} Ghost - Sacrifice to double egg production next turn.")
                        elif ghost.original_tier == "Gold":
                            print(f"{i+1}. {ghost.original_tier} Ghost - Sacrifice to convert a Bronze chicken to a Silver chicken.")
                    print("0. Go Back")
                    try:
                        choice = int(input("Choose an ability to use: "))
                        if choice == 0:
                            continue
                        selected_ghost = usable_ghosts[choice - 1]

                        if selected_ghost.original_tier == "Silver":
                            game_state.double_eggs_active = True
                            game_state.ghost_chickens.remove(selected_ghost)
                            turn_messages.append("The Silver Ghost is consumed to double your egg production next turn.")

                        elif selected_ghost.original_tier == "Gold":
                            bronze_chickens = [c for c in game_state.chickens if c.tier == "Bronze"]
                            if not bronze_chickens:
                                turn_messages.append("You have no Bronze chickens to convert.")
                            else:
                                print("\n--- Convert a Chicken ---")
                                for i, chicken in enumerate(bronze_chickens):
                                    print(f"{i+1}. {chicken}")
                                print("0. Go Back")
                                convert_choice = int(input("Choose a Bronze chicken to convert: "))
                                if convert_choice != 0:
                                    chicken_to_convert = bronze_chickens[convert_choice - 1]
                                    game_state.chickens.remove(chicken_to_convert)
                                    # Converted chickens get base cash value as purchase price
                                    game_state.add_chicken("Duck", "Silver", CHICKEN_STATS["Duck"]["cash"])
                                    game_state.ghost_chickens.remove(selected_ghost)
                                    turn_messages.append(f"The Gold Ghost is consumed to transform your {chicken_to_convert.breed} into a Silver Duck!")

                    except (ValueError, IndexError):
                        turn_messages.append("Invalid choice.")

            elif action == "11":
                feed_consumption_multiplier = 1.0
                if game_state.season == "Summer":
                    feed_consumption_multiplier += SEASONS["Summer"]["feed_increase"]

                silver_ghost_count = sum(1 for g in game_state.ghost_chickens if g.original_tier == "Silver")
                feed_needed = 0
                for chicken in game_state.chickens:
                    reduction = 0
                    if chicken.tier == "Silver" and silver_ghost_count > 0:
                        reduction = silver_ghost_count
                    consumption = max(0, chicken.feed_consumption - reduction)
                    feed_needed += int(consumption * feed_consumption_multiplier)

                if game_state.feed >= feed_needed:
                    game_state.feed -= feed_needed
                    turn_messages.append(f"Your chickens consumed {feed_needed} feed.")
                else:
                    turn_messages.append("Not enough feed! Your chickens are starving.")
                    lose_chicken(game_state, turn_messages)

                if game_state.season == "Winter" and random.random() < SEASONS["Winter"]["illness_chance"]:
                    turn_messages.append("A winter illness is spreading...")
                    lose_chicken(game_state, turn_messages)

                game_state.next_turn()
                break
            else:
                turn_messages.append("Invalid action.")

def main():
    show_intro()
    while True:
        play_game()
        while True:
            play_again = input("\nPlay again? (y/n): ").lower()
            if play_again in ["y", "n"]:
                break
        if play_again == "n":
            break
    print("\nThank you for playing Poultry Geist!")

if __name__ == "__main__":
    main()
