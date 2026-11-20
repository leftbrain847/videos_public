# Disk Football capture pool

Bot-played captures of Disk Football (RedZone repo, `games/disk-football/client`, capture mode from the Followable storyplay patch) made with video_generator's `vg capture` at 1080×1920, 30 fps. `engine/highlights.py` cuts each video's 60 s reel from these: touchdowns first, then yards, laterals counted only on plays of 20+ yards; non-TD plays under 15 yards never appear.

Bot settings for this pool (`--bot`): `{"openYds": 5, "throwByS": 2.8, "pressureYds": 3.5, "teammateOpenYds": 4, "maxLaterals": 3, "missChance": 0}`: waits for an open receiver, laterals only under real pressure to an open teammate. Recipes per seed are in `recipe_s*.json`.

| seed | seconds | plays | touchdowns |
| --- | --- | --- | --- |
| 7 | 180 | 18 | 6 |
| 23 | 180 | 17 | 6 |

Recaptured 2026-11-20 after J's UAT: the ball carrier now runs for the end zone (straight upfield unless a defender ahead closes the lane, then the open lane, never along the sideline), from the RedZone capture bot's `laneX` steering.
