import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import os
from collections import Counter
from main import (
    GameState, Chicken, GhostChicken, CHICKEN_STATS, COOP_UPGRADES, 
    SEASONS, EVENTS, VICTORY_EGGS, VICTORY_CASH, VICTORY_MEAT,
    GHOST_EXCHANGE_RATES, HATCHING_COST, HATCHING_SUCCESS_RATE,
    EVENT_CHANCE, process_turn_start, lose_chicken, check_victory_conditions,
    check_game_over
)

class PoultryGeistGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poultry Geist - Digital Farm Management Simulator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2E5C3E')
        
        self.game_state = GameState()
        self.turn_messages = []
        
        self.setup_ui()
        self.show_intro()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2E5C3E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for game state
        self.top_frame = tk.Frame(main_frame, bg='#4A7C59', relief=tk.RAISED, bd=2)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Middle frame - split into left (farm view) and right (actions)
        middle_frame = tk.Frame(main_frame, bg='#2E5C3E')
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Farm view
        self.farm_frame = tk.Frame(middle_frame, bg='#8FBC8F', relief=tk.SUNKEN, bd=2)
        self.farm_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right side - Actions
        self.actions_frame = tk.Frame(middle_frame, bg='#4A7C59', relief=tk.RAISED, bd=2)
        self.actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        
        # Bottom frame for messages and ghosts
        self.bottom_frame = tk.Frame(main_frame, bg='#4A7C59', relief=tk.RAISED, bd=2)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.create_game_state_display()
        self.create_farm_view()
        self.create_actions_panel()
        self.create_message_area()
        
    def create_game_state_display(self):
        # Game info
        info_frame = tk.Frame(self.top_frame, bg='#4A7C59')
        info_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.year_label = tk.Label(info_frame, text="Year: 1", font=('Arial', 12, 'bold'), bg='#4A7C59', fg='white')
        self.year_label.pack(anchor=tk.W)
        
        self.turn_label = tk.Label(info_frame, text="Turn: 1", font=('Arial', 10), bg='#4A7C59', fg='white')
        self.turn_label.pack(anchor=tk.W)
        
        self.season_label = tk.Label(info_frame, text="Season: Spring", font=('Arial', 10), bg='#4A7C59', fg='white')
        self.season_label.pack(anchor=tk.W)
        
        # Resources
        resources_frame = tk.Frame(self.top_frame, bg='#4A7C59')
        resources_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        self.cash_label = tk.Label(resources_frame, text="Cash: $15", font=('Arial', 10), bg='#4A7C59', fg='white')
        self.cash_label.pack(anchor=tk.W)
        
        self.banked_label = tk.Label(resources_frame, text="Banked: $0/50", font=('Arial', 10), bg='#4A7C59', fg='white')
        self.banked_label.pack(anchor=tk.W)
        
        self.feed_label = tk.Label(resources_frame, text="Feed: 10", font=('Arial', 10), bg='#4A7C59', fg='white')
        self.feed_label.pack(anchor=tk.W)
        
        # Victory progress
        victory_frame = tk.Frame(self.top_frame, bg='#4A7C59')
        victory_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Label(victory_frame, text="Victory Goals:", font=('Arial', 10, 'bold'), bg='#4A7C59', fg='white').pack(anchor=tk.W)
        self.eggs_progress = tk.Label(victory_frame, text=f"Eggs: 0/{VICTORY_EGGS}", font=('Arial', 9), bg='#4A7C59', fg='white')
        self.eggs_progress.pack(anchor=tk.W)
        
        self.meat_progress = tk.Label(victory_frame, text=f"Meat: 0/{VICTORY_MEAT}", font=('Arial', 9), bg='#4A7C59', fg='white')
        self.meat_progress.pack(anchor=tk.W)
        
    def create_farm_view(self):
        tk.Label(self.farm_frame, text="🐔 FARM VIEW 🐔", font=('Arial', 14, 'bold'), bg='#8FBC8F').pack(pady=10)
        
        # Coop info
        self.coop_label = tk.Label(self.farm_frame, text="", font=('Arial', 12), bg='#8FBC8F')
        self.coop_label.pack(pady=5)
        
        # Chickens display
        self.chickens_frame = tk.Frame(self.farm_frame, bg='#8FBC8F')
        self.chickens_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Resources display
        resources_display = tk.Frame(self.farm_frame, bg='#8FBC8F')
        resources_display.pack(fill=tk.X, padx=10, pady=10)
        
        self.eggs_display = tk.Label(resources_display, text="🥚 Eggs: 0", font=('Arial', 12), bg='#8FBC8F')
        self.eggs_display.pack(side=tk.LEFT, padx=10)
        
        self.meat_display = tk.Label(resources_display, text="🥩 Meat: 0", font=('Arial', 12), bg='#8FBC8F')
        self.meat_display.pack(side=tk.LEFT, padx=10)
        
    def create_actions_panel(self):
        tk.Label(self.actions_frame, text="ACTIONS", font=('Arial', 14, 'bold'), bg='#4A7C59', fg='white').pack(pady=10)
        
        # Market actions
        market_frame = tk.LabelFrame(self.actions_frame, text="Market", bg='#4A7C59', fg='white', font=('Arial', 10, 'bold'))
        market_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(market_frame, text="Buy Chicken", command=self.buy_chicken, width=15).pack(pady=2)
        tk.Button(market_frame, text="Sell Chicken", command=self.sell_chicken, width=15).pack(pady=2)
        tk.Button(market_frame, text="Buy Feed", command=self.buy_feed, width=15).pack(pady=2)
        tk.Button(market_frame, text="Sell Eggs", command=self.sell_eggs, width=15).pack(pady=2)
        
        # Farm actions
        farm_frame = tk.LabelFrame(self.actions_frame, text="Farm", bg='#4A7C59', fg='white', font=('Arial', 10, 'bold'))
        farm_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(farm_frame, text="Harvest for Meat", command=self.harvest_chicken, width=15).pack(pady=2)
        tk.Button(farm_frame, text="Hatch Eggs", command=self.hatch_eggs, width=15).pack(pady=2)
        tk.Button(farm_frame, text="Upgrade Coop", command=self.upgrade_coop, width=15).pack(pady=2)
        
        # Financial actions
        financial_frame = tk.LabelFrame(self.actions_frame, text="Banking", bg='#4A7C59', fg='white', font=('Arial', 10, 'bold'))
        financial_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(financial_frame, text="Bank Cash", command=self.bank_cash, width=15).pack(pady=2)
        
        # Ghost actions
        ghost_frame = tk.LabelFrame(self.actions_frame, text="Supernatural", bg='#4A7C59', fg='white', font=('Arial', 10, 'bold'))
        ghost_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(ghost_frame, text="Manage Ghosts", command=self.manage_ghosts, width=15).pack(pady=2)
        tk.Button(ghost_frame, text="Use Ghost Ability", command=self.use_ghost_ability, width=15).pack(pady=2)
        
        # Turn control
        turn_frame = tk.Frame(self.actions_frame, bg='#4A7C59')
        turn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(turn_frame, text="NEXT TURN", command=self.next_turn, 
                 bg='#228B22', fg='white', font=('Arial', 12, 'bold'), width=15).pack(pady=5)
        
    def create_message_area(self):
        # Messages
        messages_frame = tk.Frame(self.bottom_frame, bg='#4A7C59')
        messages_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(messages_frame, text="Messages", font=('Arial', 10, 'bold'), bg='#4A7C59', fg='white').pack(anchor=tk.W)
        
        self.message_text = tk.Text(messages_frame, height=6, bg='white', fg='black', wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(messages_frame, orient=tk.VERTICAL, command=self.message_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_text.config(yscrollcommand=scrollbar.set)
        
        # Graveyard and ghosts
        spirit_frame = tk.Frame(self.bottom_frame, bg='#4A7C59')
        spirit_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(spirit_frame, text="👻 Supernatural", font=('Arial', 10, 'bold'), bg='#4A7C59', fg='white').pack()
        
        self.graveyard_label = tk.Label(spirit_frame, text="", font=('Arial', 9), bg='#4A7C59', fg='white', justify=tk.LEFT)
        self.graveyard_label.pack(pady=5)
        
        self.ghosts_label = tk.Label(spirit_frame, text="", font=('Arial', 9), bg='#4A7C59', fg='white', justify=tk.LEFT)
        self.ghosts_label.pack(pady=5)
        
    def show_intro(self):
        intro_text = """Welcome to Poultry Geist!

Build a thriving poultry farm by managing your flock and resources.

Your goal is to achieve the following in a single year:
• Produce 20 eggs in a single turn
• Bank $50 cash
• Harvest 30 meat

When your chickens die, their spirits linger. Collect enough spirits
to summon powerful Ghost Chickens with unique abilities.

Good luck, farmer!"""
        
        messagebox.showinfo("Poultry Geist", intro_text)
        self.update_display()
        
    def update_display(self):
        # Update game state labels
        self.year_label.config(text=f"Year: {self.game_state.year}")
        self.turn_label.config(text=f"Turn: {self.game_state.turn}")
        self.season_label.config(text=f"Season: {self.game_state.season}")
        
        self.cash_label.config(text=f"Cash: ${self.game_state.cash}")
        self.banked_label.config(text=f"Banked: ${self.game_state.banked_cash}/{VICTORY_CASH}")
        self.feed_label.config(text=f"Feed: {self.game_state.feed}")
        
        self.eggs_display.config(text=f"🥚 Eggs: {self.game_state.eggs}")
        self.meat_display.config(text=f"🥩 Meat: {self.game_state.meat}")
        
        # Update victory progress
        self.meat_progress.config(text=f"Meat: {self.game_state.meat_harvested_this_year}/{VICTORY_MEAT}")
        
        # Update coop info
        coop_name = COOP_UPGRADES[self.game_state.coop_level]["name"]
        self.coop_label.config(text=f"{coop_name}: {len(self.game_state.chickens)}/{self.game_state.get_coop_capacity()}")
        
        # Update chickens display
        for widget in self.chickens_frame.winfo_children():
            widget.destroy()
            
        if self.game_state.chickens:
            for i, chicken in enumerate(self.game_state.chickens):
                chicken_frame = tk.Frame(self.chickens_frame, bg='#8FBC8F', relief=tk.RIDGE, bd=1)
                chicken_frame.pack(fill=tk.X, pady=2, padx=5)
                
                emoji = "🐔" if chicken.tier == "Bronze" else "🦆" if chicken.tier == "Silver" else "🐓"
                text = f"{emoji} {chicken.tier} {chicken.breed} (Health: {chicken.current_health})"
                tk.Label(chicken_frame, text=text, bg='#8FBC8F', font=('Arial', 10)).pack(anchor=tk.W, padx=5)
        else:
            tk.Label(self.chickens_frame, text="No chickens in coop", bg='#8FBC8F', font=('Arial', 10), fg='gray').pack(pady=20)
            
        # Update graveyard and ghosts
        graveyard_counts = Counter(c.tier for c in self.game_state.graveyard)
        graveyard_text = f"Graveyard:\nBronze: {graveyard_counts['Bronze']}\nSilver: {graveyard_counts['Silver']}\nGold: {graveyard_counts['Gold']}"
        self.graveyard_label.config(text=graveyard_text)
        
        if self.game_state.ghost_chickens:
            ghost_text = "Ghosts:\n" + "\n".join([f"👻 {ghost}" for ghost in self.game_state.ghost_chickens])
        else:
            ghost_text = "Ghosts:\nNone"
        self.ghosts_label.config(text=ghost_text)
        
    def add_message(self, message):
        self.message_text.insert(tk.END, message + "\n")
        self.message_text.see(tk.END)
        
    def buy_chicken(self):
        dialog = ChickenBuyDialog(self.root, self.game_state)
        if dialog.result:
            breed, cost = dialog.result
            if self.game_state.cash >= cost:
                if self.game_state.add_chicken(breed, CHICKEN_STATS[breed]["tier"], cost):
                    self.game_state.cash -= cost
                    self.add_message(f"You bought a {breed} for ${cost}.")
                else:
                    self.add_message("Your coop is full!")
            else:
                self.add_message("Not enough cash.")
            self.update_display()
            
    def sell_chicken(self):
        if not self.game_state.chickens:
            self.add_message("You have no chickens to sell.")
            return
            
        dialog = ChickenSellDialog(self.root, self.game_state)
        if dialog.result is not None:
            chicken_index = dialog.result
            sold_chicken = self.game_state.chickens.pop(chicken_index)
            sale_price = sold_chicken.get_sale_price(self.game_state.season)
            self.game_state.cash += sale_price
            self.add_message(f"You sold a {sold_chicken} for ${sale_price}.")
            self.update_display()
            
    def buy_feed(self):
        feed_price = 1.0
        if self.game_state.season == "Winter":
            feed_price += SEASONS["Winter"]["feed_cost_increase"]
            
        amount = simpledialog.askinteger("Buy Feed", f"How much feed to buy? (${feed_price:.2f} per unit)")
        if amount and amount > 0:
            cost = amount * feed_price
            if self.game_state.cash >= cost:
                self.game_state.feed += amount
                self.game_state.cash -= cost
                self.add_message(f"You bought {amount} units of feed.")
            else:
                self.add_message("Not enough cash.")
            self.update_display()
            
    def sell_eggs(self):
        if self.game_state.eggs <= 0:
            self.add_message("You have no eggs to sell.")
            return
            
        egg_price = int(1 * self.game_state.egg_price_multiplier)
        amount = simpledialog.askinteger("Sell Eggs", 
                                       f"You have {self.game_state.eggs} eggs. Current price: ${egg_price} per egg.\nHow many to sell?")
        if amount and 0 < amount <= self.game_state.eggs:
            earnings = amount * egg_price
            self.game_state.eggs -= amount
            self.game_state.cash += earnings
            self.add_message(f"You sold {amount} eggs for ${earnings}.")
            self.update_display()
        elif amount and amount > self.game_state.eggs:
            self.add_message("You don't have that many eggs.")
            
    def harvest_chicken(self):
        if not self.game_state.chickens:
            self.add_message("You have no chickens to harvest.")
            return
            
        dialog = ChickenHarvestDialog(self.root, self.game_state)
        if dialog.result is not None:
            chicken_index = dialog.result
            harvested_chicken = self.game_state.chickens.pop(chicken_index)
            self.game_state.graveyard.append(harvested_chicken)
            meat_yield = harvested_chicken.meat_value
            if self.game_state.season == "Fall":
                meat_yield = int(meat_yield * (1 + SEASONS["Fall"]["meat_bonus"]))
            self.game_state.meat += meat_yield
            self.game_state.meat_harvested_this_year += meat_yield
            self.add_message(f"You harvested a {harvested_chicken} for {meat_yield} meat.")
            self.update_display()
            
    def hatch_eggs(self):
        hatch_rate = HATCHING_SUCCESS_RATE
        if self.game_state.season == "Spring":
            hatch_rate += SEASONS["Spring"]["hatching_bonus"]
            
        if self.game_state.eggs < HATCHING_COST:
            self.add_message("You don't have enough eggs to attempt hatching.")
            return
            
        result = messagebox.askyesno("Hatch Eggs", 
                                   f"It costs {HATCHING_COST} eggs to attempt to hatch a new chick.\nCurrent success rate: {hatch_rate:.0%}\nAttempt to hatch?")
        if result:
            self.game_state.eggs -= HATCHING_COST
            if random.random() < hatch_rate:
                if self.game_state.add_chicken("Pearl Leghorn", "Bronze", CHICKEN_STATS["Pearl Leghorn"]["cash"]):
                    self.add_message("Success! A new Pearl Leghorn chick has hatched!")
                else:
                    self.add_message("The egg hatched, but your coop is full! The chick ran away.")
            else:
                self.add_message("The egg didn't hatch.")
            self.update_display()
            
    def bank_cash(self):
        amount = simpledialog.askinteger("Bank Cash", f"You have ${self.game_state.cash} to bank.\nHow much to bank?")
        if amount and 0 < amount <= self.game_state.cash:
            self.game_state.cash -= amount
            self.game_state.banked_cash += amount
            self.add_message(f"You banked ${amount}.")
            self.update_display()
        elif amount and amount > self.game_state.cash:
            self.add_message("You don't have that much cash.")
            
    def upgrade_coop(self):
        next_level = self.game_state.coop_level + 1
        if next_level not in COOP_UPGRADES:
            self.add_message("Your coop is already max level!")
            return
            
        upgrade_cost = COOP_UPGRADES[next_level]["cost"]
        upgrade_name = COOP_UPGRADES[next_level]["name"]
        
        if self.game_state.cash < upgrade_cost:
            self.add_message(f"You don't have enough cash. The {upgrade_name} costs ${upgrade_cost}.")
            return
            
        result = messagebox.askyesno("Upgrade Coop", f"Upgrade to {upgrade_name} for ${upgrade_cost}?")
        if result:
            self.game_state.cash -= upgrade_cost
            self.game_state.coop_level = next_level
            self.add_message(f"Congratulations! You've upgraded to the {upgrade_name}.")
            self.update_display()
            
    def manage_ghosts(self):
        dialog = GhostManagementDialog(self.root, self.game_state)
        if dialog.result:
            ghost_type = dialog.result
            graveyard_counts = Counter(c.tier for c in self.game_state.graveyard)
            
            if graveyard_counts[ghost_type] >= GHOST_EXCHANGE_RATES[ghost_type]:
                # Remove spirits from graveyard
                removed_count = 0
                new_graveyard = []
                for chicken in self.game_state.graveyard:
                    if chicken.tier == ghost_type and removed_count < GHOST_EXCHANGE_RATES[ghost_type]:
                        removed_count += 1
                    else:
                        new_graveyard.append(chicken)
                self.game_state.graveyard = new_graveyard
                self.game_state.ghost_chickens.append(GhostChicken(ghost_type))
                self.add_message(f"You have created a {ghost_type} Ghost!")
                self.update_display()
            else:
                self.add_message(f"Not enough {ghost_type} spirits.")
                
    def use_ghost_ability(self):
        usable_ghosts = [g for g in self.game_state.ghost_chickens if g.original_tier != "Bronze"]
        if not usable_ghosts:
            self.add_message("No active ghost abilities available.")
            return
            
        dialog = GhostAbilityDialog(self.root, self.game_state, usable_ghosts)
        if dialog.result:
            ghost, action = dialog.result
            
            if ghost.original_tier == "Silver":
                self.game_state.double_eggs_active = True
                self.game_state.ghost_chickens.remove(ghost)
                self.add_message("The Silver Ghost is consumed to double your egg production next turn.")
                
            elif ghost.original_tier == "Gold" and action:
                chicken_to_convert = action
                self.game_state.chickens.remove(chicken_to_convert)
                self.game_state.add_chicken("Duck", "Silver", CHICKEN_STATS["Duck"]["cash"])
                self.game_state.ghost_chickens.remove(ghost)
                self.add_message(f"The Gold Ghost is consumed to transform your {chicken_to_convert.breed} into a Silver Duck!")
                
            self.update_display()
            
    def next_turn(self):
        # Calculate feed consumption
        feed_consumption_multiplier = 1.0
        if self.game_state.season == "Summer":
            feed_consumption_multiplier += SEASONS["Summer"]["feed_increase"]
            
        silver_ghost_count = sum(1 for g in self.game_state.ghost_chickens if g.original_tier == "Silver")
        feed_needed = 0
        for chicken in self.game_state.chickens:
            reduction = 0
            if chicken.tier == "Silver" and silver_ghost_count > 0:
                reduction = silver_ghost_count
            consumption = max(0, chicken.feed_consumption - reduction)
            feed_needed += int(consumption * feed_consumption_multiplier)
            
        if self.game_state.feed >= feed_needed:
            self.game_state.feed -= feed_needed
            self.add_message(f"Your chickens consumed {feed_needed} feed.")
        else:
            self.add_message("Not enough feed! Your chickens are starving.")
            lose_chicken(self.game_state, self.turn_messages)
            
        if self.game_state.season == "Winter" and random.random() < SEASONS["Winter"]["illness_chance"]:
            self.add_message("A winter illness is spreading...")
            lose_chicken(self.game_state, self.turn_messages)
            
        self.game_state.next_turn()
        
        # Process turn start for next turn
        turn_messages, eggs_this_turn = process_turn_start(self.game_state)
        for msg in turn_messages:
            self.add_message(msg)
            
        # Update eggs progress with current turn's production
        self.eggs_progress.config(text=f"Eggs: {eggs_this_turn}/{VICTORY_EGGS}")
        
        # Check victory
        if check_victory_conditions(self.game_state, eggs_this_turn):
            messagebox.showinfo("Victory!", "Congratulations! You have built a thriving poultry farm and won the game!")
            self.root.quit()
            return
            
        # Check game over
        if check_game_over(self.game_state):
            messagebox.showinfo("Game Over", "You have no chickens and not enough cash to buy a new one.\nYour farm has gone bankrupt.")
            self.root.quit()
            return
            
        self.update_display()

class ChickenBuyDialog:
    def __init__(self, parent, game_state):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Buy Chicken")
        dialog.geometry("400x300")
        dialog.configure(bg='#4A7C59')
        dialog.transient(parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Market - Choose a chicken to buy:", font=('Arial', 12, 'bold'), 
                bg='#4A7C59', fg='white').pack(pady=10)
        
        for breed, stats in CHICKEN_STATS.items():
            price = stats['cash']
            if game_state.season == "Spring":
                price = int(price * (1 - SEASONS["Spring"]["new_chicken_discount"]))
            price = max(1, price)
            
            frame = tk.Frame(dialog, bg='#4A7C59')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            text = f"{stats['tier']} {breed} - ${price}"
            btn = tk.Button(frame, text=text, command=lambda b=breed, p=price: self.select(dialog, b, p))
            btn.pack(fill=tk.X)
            
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
        
        # Wait for dialog to be closed
        dialog.wait_window()
        
    def select(self, dialog, breed, price):
        self.result = (breed, price)
        dialog.destroy()

class ChickenSellDialog:
    def __init__(self, parent, game_state):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Sell Chicken")
        dialog.geometry("400x300")
        dialog.configure(bg='#4A7C59')
        dialog.transient(parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Your Chickens - Choose one to sell:", font=('Arial', 12, 'bold'), 
                bg='#4A7C59', fg='white').pack(pady=10)
        
        for i, chicken in enumerate(game_state.chickens):
            sale_price = chicken.get_sale_price(game_state.season)
            
            frame = tk.Frame(dialog, bg='#4A7C59')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            text = f"{chicken} - ${sale_price} (bought for ${chicken.purchase_price})"
            btn = tk.Button(frame, text=text, command=lambda idx=i: self.select(dialog, idx))
            btn.pack(fill=tk.X)
            
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
        
        # Wait for dialog to be closed
        dialog.wait_window()
        
    def select(self, dialog, index):
        self.result = index
        dialog.destroy()

class ChickenHarvestDialog:
    def __init__(self, parent, game_state):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Harvest Chicken")
        dialog.geometry("400x300")
        dialog.configure(bg='#4A7C59')
        dialog.transient(parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Choose a chicken to harvest for meat:", font=('Arial', 12, 'bold'), 
                bg='#4A7C59', fg='white').pack(pady=10)
        
        for i, chicken in enumerate(game_state.chickens):
            frame = tk.Frame(dialog, bg='#4A7C59')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            btn = tk.Button(frame, text=str(chicken), command=lambda idx=i: self.select(dialog, idx))
            btn.pack(fill=tk.X)
            
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
        
        # Wait for dialog to be closed
        dialog.wait_window()
        
    def select(self, dialog, index):
        self.result = index
        dialog.destroy()

class GhostManagementDialog:
    def __init__(self, parent, game_state):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Manage Ghosts")
        dialog.geometry("500x400")
        dialog.configure(bg='#4A7C59')
        dialog.transient(parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Exchange spirits of fallen chickens for Ghost Chickens:", 
                font=('Arial', 12, 'bold'), bg='#4A7C59', fg='white').pack(pady=10)
        
        graveyard_counts = Counter(c.tier for c in game_state.graveyard)
        
        for tier in ["Bronze", "Silver", "Gold"]:
            frame = tk.Frame(dialog, bg='#4A7C59')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            required = GHOST_EXCHANGE_RATES[tier]
            available = graveyard_counts[tier]
            
            text = f"Exchange {required} {tier} spirits for 1 {tier} Ghost (You have: {available})"
            btn = tk.Button(frame, text=text, 
                           command=lambda t=tier: self.select(dialog, t),
                           state=tk.NORMAL if available >= required else tk.DISABLED)
            btn.pack(fill=tk.X)
            
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
        
        # Wait for dialog to be closed
        dialog.wait_window()
        
    def select(self, dialog, tier):
        self.result = tier
        dialog.destroy()

class GhostAbilityDialog:
    def __init__(self, parent, game_state, usable_ghosts):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Use Ghost Ability")
        dialog.geometry("500x400")
        dialog.configure(bg='#4A7C59')
        dialog.transient(parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Choose a ghost ability to use:", font=('Arial', 12, 'bold'), 
                bg='#4A7C59', fg='white').pack(pady=10)
        
        for ghost in usable_ghosts:
            frame = tk.Frame(dialog, bg='#4A7C59')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            if ghost.original_tier == "Silver":
                text = f"{ghost.original_tier} Ghost - Sacrifice to double egg production next turn"
                btn = tk.Button(frame, text=text, command=lambda g=ghost: self.select_silver(dialog, g))
                btn.pack(fill=tk.X)
            elif ghost.original_tier == "Gold":
                text = f"{ghost.original_tier} Ghost - Sacrifice to convert a Bronze chicken to Silver"
                btn = tk.Button(frame, text=text, command=lambda g=ghost: self.select_gold(dialog, g, game_state))
                btn.pack(fill=tk.X)
                
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
        
        # Wait for dialog to be closed
        dialog.wait_window()
        
    def select_silver(self, dialog, ghost):
        self.result = (ghost, None)
        dialog.destroy()
        
    def select_gold(self, dialog, ghost, game_state):
        bronze_chickens = [c for c in game_state.chickens if c.tier == "Bronze"]
        if not bronze_chickens:
            messagebox.showwarning("No Bronze Chickens", "You have no Bronze chickens to convert.")
            return
            
        # Create sub-dialog to choose which bronze chicken
        subdialog = tk.Toplevel(dialog)
        subdialog.title("Choose Chicken to Convert")
        subdialog.geometry("400x300")
        subdialog.configure(bg='#4A7C59')
        subdialog.transient(dialog)
        subdialog.grab_set()
        
        tk.Label(subdialog, text="Choose a Bronze chicken to convert:", 
                font=('Arial', 12, 'bold'), bg='#4A7C59', fg='white').pack(pady=10)
        
        for chicken in bronze_chickens:
            btn = tk.Button(subdialog, text=str(chicken), 
                           command=lambda c=chicken: self.select_conversion(dialog, subdialog, ghost, c))
            btn.pack(fill=tk.X, padx=20, pady=5)
            
        tk.Button(subdialog, text="Cancel", command=subdialog.destroy).pack(pady=10)
        
        # Wait for subdialog to be closed
        subdialog.wait_window()
        
    def select_conversion(self, dialog, subdialog, ghost, chicken):
        self.result = (ghost, chicken)
        subdialog.destroy()
        dialog.destroy()

def main():
    root = tk.Tk()
    app = PoultryGeistGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()