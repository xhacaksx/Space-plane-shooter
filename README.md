# Space Plane Shooter

A classic arcade-style shooting game built with Python and Pygame where you control a plane and shoot down enemies while collecting power-ups.

## Features

- Player-controlled plane with shooting capability
- Enemy planes that come from above
- Three different power-ups:
  - Triple Shot (Blue Diamond): Shoot three bullets at once
  - Rapid Fire (Purple Star): Increased firing rate
  - Big Shot (Orange Circle): Larger bullets for better hit chance
- Score tracking system
- Lives system (3 lives)
- 2-minute game duration
- Space background with stars
- Sound effects and background music

## Requirements

- Python 3.x
- Pygame 2.5.2

## Installation

1. Clone this repository:

```bash
git clone https://github.com/xhacaksx/space-plane-shooter.git
cd space-plane-shooter
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## How to Play

Run the game:

```bash
python plane_shooter.py
```

### Controls

- LEFT/RIGHT arrow keys to move the plane
- SPACE to shoot
- ESC to exit

### Power-ups

- Blue Diamond: Triple Shot - Shoots three bullets at once
- Purple Star: Rapid Fire - Shoots faster
- Orange Circle: Big Shot - Larger bullets

### Game Rules

- You start with 3 lives
- Each enemy hit gives you 1 point
- Survive for 2 minutes to win
- Losing all lives ends the game
- Power-ups last for 5 seconds

## Files

- `plane_shooter.py`: Main game file
- `create_images.py`: Script to generate game assets
- `requirements.txt`: Python dependencies
- `assets/`: Directory containing game images and sounds

## Credits

Created as a fun project to learn game development with Pygame.
