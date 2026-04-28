### Date: 04/08/2026, Start of Lab
**Goal**
changing the cross texture to use a coin texture png

**implementation**
*Technical Plan/Credit*: Use previous lab sprite references
*Content Credit*: https://opengameart.org/content/coin-animation 

**Commit message** Added coin sprite to collect

Next/TODO: 
*Coin Class
*Animation



### Date: 04/08/2026, End of Lab
**Goal**
Add a simple coin pickup sound to learn about sounds in this library

**implementation**
*Technical Plan/Credit*: Use online references
*Content Credit*: Self Generated

**Commit message** Added sound to coin pickup

Next/TODO: 
*Sound Manager
*Sounds for other events



### Date: 04/15/2026, Start of lab
**Goal**
Add a liquid system, with water you can swim through and poison that hurts you.

**implementation**
*Technical Plan/Credit*: Extend the current tile map with a water and posions tile and simple swimming physics. Update player color on water 
*Content Credit*: Self Implemented by doing gravity change

**Commit message** Added basic liquid tiles and swimming area

Next/TODO: 
*Actual water level design
*Other Liquids
*Flood Fill Algorithm on poison that touches water



### Date: 04/19/2026, 7pm-11
**Goal**
Add poison and antidote interactables that change connected water instead of treating poison like a static tile only.

**Implementation**
*Technical Plan/Credit*: Added a flood-fill liquid conversion system so poison converts connected clean water and antidote restores connected poisoned water.

Next/TODO:
*Add clearer water change effects, not just near instant



### Date: 04/19/2026, 7pm-11
**Goal**
Add basic room-complete loop and end point

**Implementation**
*Technical Plan/Credit*: Lock the exit until all enemies are cleared, kill enemies when poison reaches them, and show a basic clean score plus pause/reset UI.
*Content Credit*: Self implemented from the GDD goals.

Next/TODO:
*Replace rectangle placeholders with sprites and better UI art



### Date: 04/19/2026, 7-11
**Goal**
Refactored the project into multiple files for readability and scaling

**Implementation**
*Technical Plan/Credit*: Split the code into a main game loop file, a settings/layout file, helpers file, entities file, and a level parsing file
*Content Credit*: Self implemented

**Commit message** Committed base game loop prototype

Next/TODO:
*Sprites
*Sounds
*Assets




### Date: 04/26/2026
**Goal**  
Updated game lore and story

**Implementation**  
*Technical Plan/Credit*: Updated gdd to gddv2, with story tie in to colgate



### Date: 04/27/2026
**Goal**  
Resize the game window and add a parallax background.

**Implementation**  
*Technical Plan/Credit*: Increased the game window to a larger 1280 by 720 view and added a scrolling background layer. The background now follows the camera at a slower speed using parallax, which makes the level feel larger and less flat while the player moves through the world.  
*Content Credit*: https://craftpix.net/freebies/free-nature-backgrounds-pixel-art/


### Date: 04/27/2026
**Goal**  
Add base sprites for the main game entities.

**Implementation**  
*Technical Plan/Credit*: Added base sprites to most of game
*Content Credit*: Generated

Next/TODO:  
* Animation for each necessary aniomation, not just static



### Date: 04/28/2026
**Goal**  
Change flood fill so liquid spreads visibly instead of instantly.

**Implementation**  
*Technical Plan/Credit*: Reworked the poison and antidote flood fill system so it no longer changes the entire connected liquid area in one frame. The game now creates an active liquid spread effect that stores a frontier of tiles and updates over time, causing poison or antidote to move tile-by-tile through connected water.  
*Content Credit*: Self implemented with technical planning support.

Next/TODO:  
* Adjust speeds




### Date: 04/28/2026
**Goal**  
Replace the mechanic test room with a real demo level layout.

**Implementation**  
*Technical Plan/Credit*: Changed the level design from a basic mechanic testing area into a more complete demo puzzle. The new layout includes land movement, swimming sections, enemies, chemical jars, water/poison interactions, and an exit that only becomes useful after clearing the enemies.  
*Content Credit*: Self implemented level design.

Next/TODO:  
* Playtest jumps, jar pushes, and enemy placement for difficulty  
* Make main level 2