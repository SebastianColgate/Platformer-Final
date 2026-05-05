# Amphibi-Man  
## Game Design Document

**Sebastian Cole**  
**Final Project**  
**Python with raylib**
**Single-Player Puzzle Platformer**
---

# Introduction

## Game Summary
**Amphibi-Man** is a simple puzzle platformer about a man who can move between land and water, switching into an amphibious form. The goal in each level is to clear every enemy before reaching the exit.

The main mechanic is the liquid system. If poison touches a body of water, all connected water becomes poisoned. This kills enemies in the water, but it also makes that water unsafe for the player to swim in. If antidote touches poisoned water, that connected water becomes normal again.

The game is built around movement, enemy clearing, and changing the level itself in order to solve each room.

## Inspiration
The game itself is inspired by:
- **Celeste** for tight 2D platforming
- puzzle platformers that teach one mechanic at a time
- games where changing the environment is part of the puzzle
- **Where's My Water** for a bit of the posison water system

# Story

The accident starts in the HO science building. A campus science experiment explodes and releases chemicals across Colgate. The player survives, but is transformed into Amphibi-Man.

The first goal is to help clean up the campus. The larger goal is to work back toward the science building and find the chemical that can reverse the mutation.

The story is light, but it gives the mechanics a reason:
- poison represents chemical contamination
- antidote represents cleanup chemicals
- enemies are mutated by the explosion
- the clean score represents how well the player restores the water

---

## Player Experience
I want the game to feel simple, readable, and satisfying. The player should feel like they are using the water itself as the main tool for solving the level, although some enemies can be taken our by multiple routes.

# Concept

## Gameplay Overview
The player controls Amphibi-Man, who can run, jump, and swim. Each level contains enemies placed across land and water, and the player must elmimintae all of them to unlock or reach the exit.

The main puzzle comes from the fact that poisoning water can solve the enemy problem, but it can also block off a route the player still needs. Antidote lets the player reverse that and reopen paths.

The central idea of the game is:

**Use the environment to solve the level without ruining the level for yourself.**

---

# Mechanics

## Primary Mechanics
### Platforming
Standard platforming, as this is a platformer game by nature and final requirement

### Swimming
The player can move through clean water, as well as jump out

### Poisoning Water
If poison touches a connected body of water, all of that water becomes poisoned.
- kills any enemies that touch the water
- prevents safe swimming

### Cleaning Water
If antidote touches poisoned water, all connected poisoned water becomes normal again.
- restores safe swimming
- reopens movement routes
- improves the end-level clean score

### Enemy Clear Requirement
The player cannot finish the level until all enemies are removed. The doors are locked until this happens. 

### Clean Score
At the end of each level, the player gets a score based on how much water is still poisoned, which is a kind of optional challenge to see how clean they can make it, and increase difficulaty for those up for the challenge.

## Secondary Mechanics
- **Clean Score** 
- **Water enemies** that stay in water
- **Amphibious enemies** that move between both
- **Hazards** like spikes or pits
- **One-way platforms** for simple level layouts
-**Antidote**
- really its the classic platforming secondary mechanics. 

---

# Water System Rules

- Poison turns connected clean water into poison
- Antidote turns connected poisoned water back into clean water
- The water state must always be visually clear

For readability:
- clean water = blue
- poisoned water = purple

This mechanic is the core of the game, so it will be very obvious and consistent.

---

# Level Design

## Structure
The levels should be fairly small and focused. Each one should introduce or test one main idea. In general, for the scope of the class as more of a demo, I will create a more "tutorial" level, then in the second main level incorporate more of the secondary mechanics like antidote, etc, but the puzzle will be muich more complex.

## Progression
### Level 1
Tutorial level to get farmiliar with the platforming and controls, as well as posion mechanic. 

### Level 2
Using all the previous mechanics, as well as the antidote and much more advanced platforming mechanics, this puzle will be much harder, this level more dangerous. The first serves to teach the player, but this second level asks them to expand on what theyve learned and apply it in unique ways with new expansions of mechanics. 

## Design Goals
- keep mechanics clear
- make levels readable
- stay within a manageable final-project scope
- funnnnn is a requirement. I want it cohesive, but not to feel like a school project, just a passion project
---


## Level 1: Taylor Lake
The first level takes place at Taylor Lake on Colgate's campus. It should be a focused puzzle that teaches the core loop:
- push poison into water to clear enemies
- avoid swimming in poisoned water
- use antidote to clean the water again
- reach the exit after the enemies are cleared

## Level 2: Lebanon Reservoir
The second level takes place at the larger Lebanon Reservoir. It should feel like a bigger version of the same problem, with more water, more enemies, and more cleanup decisions.

## Final Goal
After cleaning the water areas, the player is trying to return to the science building and find a cure for the mutation.

---

# Art and Audio

## Art
The game will use simple pixel art, some generated, some found online, some hand created and edited. 

Amphibi-Man will have a look built for both land and water

## Audio
The music should be light and energetic, fitting a puzzle platformer. There will be light sound effects for basic player-envioroment interactions as well, such as:
- jump
- splash
- poison
- antidote
- enemy death
- level complete

---

# UI and Controls

## UI
The in-level UI should stay simple:
- enemy count
- level number
- pause menu
- reset button


## Controls
- **A / D** or **Left / Right** – Move
- **Space** – Jump
- **S / Down** – Dive / drop down
- **R** – Restart level
- **Esc** – Pause
- more as needed for debug or discovery when programming
---

# Scope and Technical Plan

## Must-Have Features
- player movement
- swimming
- poison and antidote mechanic
- enemy clear condition
- clean score
- basic UI

## Technical Notes
The water system will be tile based, using a flood-fill algorithm. When poison or antidote hits a water tile, the game can use connected-tile logic or flood fill to update the whole region.

This is the most important technical system in the game, aside from basic collisions and engine details we have already covered in previous classes to actually display the game. 

---


# Why This Game Works
**Amphibi-Man** works as a final project because it has one clear mechanic at the center of everything, adn several smaller, expansionary secondary mechanics to expand from the core gameplay loop off of. It is small enough to finish, but still feels like a real game idea, even withing the context of two levels. 

The main appeal is that the player is not just moving through the level — they are changing the level, and then dealing with the consequences of those changes, as well as changing themselves based on their platforming being on water or land. 

#Story (If implemented)
There wont be too much world building, but in general, you are a player who was tranformed by chemicals to have the ability to be amphibious. You want to cure yourself, and to do so you must traverse the castle that is overrun with different chemicals, posions, antidotes, and enemies that have over run it in search of the cure serum. To progress, however, you need to take care of all the enemies in your way, and find the keys they hold to the next level. At the end, you can cure your amphibious transformation. 



# Final Project Addendum and submission

## Screenshot
![Gameplay screenshot](<Screenshot 2026-05-04 221036.png>)

The repo also includes a `screenshots` folder with four representative screenshots:


## Technical Section
The two most important technical parts of the game are the liquid system and the collision / movement system.

The liquid system is tile based. Water, poison water, and solid blocks are stored inside the level grid. When a poison jar or antidote jar breaks in water, the game starts a flood-fill style spread. Instead of changing every connected tile instantly, the spread moves tile by tile over time, which was trickier to implement, as initially it did at near frame perfect speed. This change made the poison and antidote feel more visible and satisfying, and gives the player a clearer sense that the level is changing.

The other major technical part is the player and object collision system. The player can switch between a land hitbox and a swimming hitbox, which both changes how the player moves (such as walking and jumping, or swimming) as well as how they are positioned, so the code has to check that the new shape is "safe" before changing modes. Moving platforms also carry jars, the player can stand on jars, and the player can be pushed by platforms from the side. This ended up taking a bunch of extra collision checks because the game has stacked interactions, not just simple player-versus-wall collision. I suspect in a game engine, this would not be as complicated, such as adding a list of riders to each platform, and actually just using basic physics of the engine. 

## Art / AI Sprite Generation
Most of the art is simple pixel art. Most sprites were originally AI generated, but took EXTENSIVE retouching and reformatting, and just straight up editing from myself, especially when it came to formatting. All generated sprites were unable to have transparent backgrounds, as well as any kind of continutity between them, so I had to manually change color shemes, remove edges and backgrounds, and many other details. I am worried that on a projector wall, things I couldnt see on my computer screen may be visible, but for the scope of play that isnt in the vault, I am very happy with the final result. 

Tools used for art cleanup included Photopea, and Aseprite for resizing and transparency cleanup. The game uses individual image files instead of sprite sheets because the generated frames were not all the exact same size, making a consistent sprite sheet quite a hassel. 

An example AI sprite prompt used for this kind of asset was:
`Create a small pixel art amphibious mutant player character for a 2D platformer, transparent background, facing right, in an idle pose.`

AI image generation was used as a starting point for several sprites, but the final versions were manually selected, resized, cleaned up, and adjusted for this project.

## Credits / References
- Raylib / pyray documentation and class examples were used for window setup, drawing, input, rectangles, textures, and collision.
- The base platformer structure came from class platformer work and was expanded into this final project.
- The main menu structure was based on a similar state-screen technique from my midterm project.
- Background art reference / source: CraftPix free pixel art nature backgrounds, linked earlier. 
- reference of floodfill algorith, also linked earlier in doc


## AI Intervention
AI assistance was primarily used for asset generation, as I am not a great artist, and finding consistent sprites across the web for free is supriningly difficult. This was the main contrivution from AI. Another aspect it did help me with was doing a player simulation/animation for the menu screens, but I make a point to still self implement my code, even if referenced from other materials, be it stack over flow, AI, class linked tutorials or whatever else. And this case is no different, even if consulted. 

## Demo Video Link
Google Drive demo video link: **https://drive.google.com/file/d/1IUtEQIP1fcqS641QPDAlXT2NBnrCh2GL/view?usp=drive_link**

