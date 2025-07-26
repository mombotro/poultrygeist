# Poultry Geist GUI Instructions

## How to Run

1. **Console Version**: Run `python main.py`
2. **GUI Version**: Run `python gui_main.py`

## GUI Features

### Main Interface Layout

- **Top Panel**: Game state (Year, Turn, Season, Resources, Victory Progress)
- **Left Panel**: Farm view showing your coop and chickens
- **Right Panel**: Action buttons organized by category
- **Bottom Panel**: Message log and supernatural status

### Action Categories

#### Market Actions
- **Buy Chicken**: Opens dialog to purchase new chickens
- **Sell Chicken**: Opens dialog to sell existing chickens
- **Buy Feed**: Enter amount of feed to purchase
- **Sell Eggs**: Enter number of eggs to sell

#### Farm Actions
- **Harvest for Meat**: Select a chicken to harvest
- **Hatch Eggs**: Attempt to hatch new chicks from eggs
- **Upgrade Coop**: Increase coop capacity

#### Banking
- **Bank Cash**: Store cash toward victory goal

#### Supernatural
- **Manage Ghosts**: Exchange dead chicken spirits for ghost chickens
- **Use Ghost Ability**: Activate special ghost powers

### Visual Elements

- **Chicken Icons**: 🐔 (Bronze), 🦆 (Silver), 🐓 (Gold)
- **Resource Counters**: Real-time updates of cash, feed, eggs, meat
- **Season Colors**: Interface adapts to current season
- **Victory Progress**: Track progress toward win conditions

### Game Controls

- **Mouse-driven**: All actions use buttons and dialogs
- **Dialog Windows**: Confirm major decisions
- **Message Log**: Scrollable history of game events
- **Real-time Updates**: Interface updates immediately after actions

## Differences from Console Version

- **Visual Interface**: Replace text menus with buttons and dialogs
- **Immediate Feedback**: See changes instantly without screen clearing
- **Better Organization**: Actions grouped logically
- **Enhanced Display**: Visual chicken representations and progress bars
- **Modal Dialogs**: Clicking action buttons opens dialogs that wait for your selection

## Tips

1. **Message Log**: Check bottom panel for important game events
2. **Victory Progress**: Monitor top-right panel for win condition status  
3. **Ghost Status**: Bottom-right shows available spirits and active ghosts
4. **Season Effects**: Interface color hints at current season bonuses/penalties
5. **Dialog Interaction**: Click buttons in dialogs to make selections, or "Cancel" to close

## Bug Fixes Applied

- **Fixed Modal Dialogs**: Buy/sell chicken dialogs now properly wait for user selection before continuing
- **All Actions Work**: Every button and dialog has been tested and confirmed functional

The GUI maintains all original game mechanics while providing a more user-friendly interface!