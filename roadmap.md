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



### Date: 04/19/2026, Prototype Feature 1
**Goal**
Replace the leftover coin-demo loop with the first actual Amphibi-Man mechanic pass.

**Implementation**
*Technical Plan/Credit*: Refactor the level into a small tutorial room with player spawn, enemy spawn, chemical pickups, and an exit state.
*Content Credit*: Self implemented using the existing raylib platformer base.

**Commit message** Build first Amphibi-Man gameplay loop

Next/TODO:
*Tune room layout around the real sketch
*Add more hazards and enemy variety



### Date: 04/19/2026, Prototype Feature 2
**Goal**
Add poison and antidote pickups that change connected water instead of treating poison like a static tile only.

**Implementation**
*Technical Plan/Credit*: Added a flood-fill liquid conversion system so poison converts connected clean water and antidote restores connected poisoned water.
*Content Credit*: Self implemented from the final project design document.

**Commit message** Add poison and antidote flood-fill pickups

Next/TODO:
*Support multiple water regions in one room more intentionally
*Add clearer VFX and sounds for chemical changes



### Date: 04/19/2026, Prototype Feature 3
**Goal**
Add the first version of the actual room-complete loop.

**Implementation**
*Technical Plan/Credit*: Lock the exit until all enemies are cleared, kill enemies when poison reaches them, and show a basic clean score plus pause/reset UI.
*Content Credit*: Self implemented from the GDD goals.

**Commit message** Add enemy-clear exit gate and prototype HUD

Next/TODO:
*Persist clean score between rooms
*Replace rectangle placeholders with sprites and better UI art



### Date: 04/19/2026, Prototype Feature 4
**Goal**
Turn the base scene into a mechanic showcase instead of treating it like the first real level.

**Implementation**
*Technical Plan/Credit*: Rebuilt the layout as a left-to-right sequence that introduces stomp combat, poison flood-fill, antidote cleanup, and a swim-to-exit finish one mechanic at a time.
*Content Credit*: Self implemented from the project goals and sketch direction.

**Commit message** Convert prototype room into mechanic showcase

Next/TODO:
*Break the showcase into separate authored levels later
*Add clearer signage, visuals, and level transitions



### Date: 04/19/2026, Prototype Feature 5
**Goal**
Simplify the presentation and switch chemicals from pickups to physical jars.

**Implementation**
*Technical Plan/Credit*: Removed the showcase text layer, rebuilt the mechanic beats around short ledges, and replaced poison/antidote pickups with pushable jars that fall, shatter on liquid contact, and trigger the flood-fill system.
*Content Credit*: Self implemented from the updated gameplay direction.

**Commit message** Replace chemical pickups with breakable jars

Next/TODO:
*Add jar break particles and sound
*Improve jar pushing so it feels more solid against the player body



### Date: 04/19/2026, Prototype Feature 6
**Goal**
Refactor the prototype into a few simple files without turning it into an overbuilt project.

**Implementation**
*Technical Plan/Credit*: Split the code into a main game loop file, a settings/layout file, a helpers file, an entities file, and a level parsing file while keeping the same basic student-level structure and behavior.
*Content Credit*: Self implemented refactor based on the current prototype.

**Commit message** Split prototype into simple modules

Next/TODO:
*Keep future features in the same simple structure
*Avoid overengineering unless the class project actually needs it



### Date: 04/19/2026, Prototype Feature 7
**Goal**
Simplify the chemical jar visuals into plain placeholder shapes.

**Implementation**
*Technical Plan/Credit*: Replaced the bottle-like placeholder art with simple square markers: poison is a square with a `P`, and antidote is a square with a green `+`.
*Content Credit*: Self implemented placeholder UI art.

**Commit message** Simplify chemical jar placeholder art

Next/TODO:
*Swap placeholder squares for real sprites later
*Add break feedback when jars shatter into liquid
