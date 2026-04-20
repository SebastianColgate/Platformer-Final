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

