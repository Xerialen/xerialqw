# ezQuake HUD & Tracking Expert - Claude Project Knowledge

**Purpose:** Complete reference for understanding and working with ezQuake's HUD and tracking systems.

**Source Analysis Date:** 2026-02-08
**Repository:** https://github.com/QW-Group/ezquake-source
**Exploration Agent ID:** a18523a

---

## Quick Navigation

- [Architecture Overview](#architecture-overview)
- [All 25 HUD Elements](#complete-hud-element-reference)
- [Console Commands Reference](#console-commands)
- [CVars Master List](#cvar-reference)
- [Tracking & Stats Systems](#tracking-systems)
- [Customization Guide](#customization)
- [Developer APIs](#developer-apis)

---

## Architecture Overview

ezQuake's HUD system is a modular, highly customizable heads-up display framework built in C. It consists of 25 individual HUD elements that can be independently positioned, styled, and configured.

### Core Concepts

**Element Registration:** Each HUD element registers with the core system (`hud.c`) providing:
- Name, description, and flags
- Drawing function callback
- Default placement and alignment
- Custom parameters (cvars)

**Placement System:** 9 placement areas (SCREEN, VIEW, SBAR, etc.) + parent/child relationships
**Alignment System:** 5 horizontal (LEFT, CENTER, RIGHT, BEFORE, AFTER) + 3 vertical alignments
**Z-Order:** Elements can be layered with configurable draw order

### File Organization

```
src/
├── hud.c / hud.h               # Core framework (1647 lines)
├── hud_common.c / hud_common.h # Utilities, initialization (1111 lines)
├── hud_editor.c                # Interactive visual editor
├── r_hud.c                     # Rendering integration
└── hud_*.c (25 files)          # Individual elements:
    ├── hud_health.c            # Health displays + damage tracking
    ├── hud_armor.c             # Armor displays + bars
    ├── hud_ammo.c              # Ammo counters (current + individual types)
    ├── hud_frags.c             # Frag displays (individual + team)
    ├── hud_speed.c             # Speedometers (bar + semicircle styles)
    ├── hud_weapon_stats.c      # Weapon accuracy tracking
    ├── vx_tracker.c            # Frag/death/flag tracker
    ├── fragstats.c             # Frag statistics parsing
    └── ... (17 more elements)
```

---

## Complete HUD Element Reference

### Health System (`hud_health.c`)

**Elements:** `health`, `healthdamage`, `bar_health`

**Purpose:** Display player health with damage indicators and visual bars.

**Key CVars:**
```
hud_health_show 1                    # 0=hide, 1=show, 2=SP, 3=MP
hud_health_style 0                   # 0=big nums, 1=text, 2=minus, 3=golden
hud_health_scale 1                   # Size multiplier
hud_health_digits 3                  # Number of digits to display
hud_healthdamage_duration 0.8        # Damage flash duration (seconds)
hud_bar_health_color_normal "32 64 128 128"   # RGBA for normal health
hud_bar_health_color_mega "64 96 128 128"     # RGBA for >100 health
```

**Functions:**
- `SCR_HUD_DrawHealth()` - Main rendering
- `HUD_HealthLow()` - Check if health is low (threshold: 25 or tp_need_health)

**Features:**
- Multiple display styles (big numbers, text, golden)
- Damage tracking with configurable flash duration
- Color-coded health bars (normal, mega >100, two-mega >200, unnatural >250)
- Integrates with teamplay need system

---

### Armor System (`hud_armor.c`)

**Elements:** `armor`, `iarmor`, `armordamage`, `bar_armor`

**Purpose:** Display armor value, type icon, and visual bars.

**Key CVars:**
```
hud_armor_show 1
hud_armor_style 0                    # 0=big nums, 1=text
hud_armor_pent_666 1                 # Show 666 when pentagram active
hud_armor_hidezero 0                 # Hide display when armor is 0
hud_iarmor_style 0                   # 0=graphic, 1=text (r/y/g/@)
hud_bar_armor_color_ga "32 128 0 128"        # Green Armor color
hud_bar_armor_color_ya "192 128 0 128"       # Yellow Armor color
hud_bar_armor_color_ra "128 0 0 128"         # Red Armor color
```

**Armor Types:**
- GA (Green Armor) - 30% absorption
- YA (Yellow Armor) - 60% absorption
- RA (Red Armor) - 80% absorption
- Invulnerability - 99% absorption

**Features:**
- Icon display shows current armor type
- Bar colors change based on armor type
- Special display (666) when pentagram powerup active
- Supports armor > 100 with different coloring

---

### Ammo System (`hud_ammo.c`)

**Elements:** `ammo`, `ammo1`, `ammo2`, `ammo3`, `ammo4`, `iammo1-4`

**Purpose:** Display current weapon ammo and all ammo types (shells, nails, rockets, cells).

**Key CVars:**
```
hud_ammo_show 1
hud_ammo_style 0                     # 0/2=big nums, 1/3=text
hud_ammo_show_always 0               # Show even without weapon selected
hud_ammo_text_color_low ""           # Color when ammo is low
hud_ammo_text_color_normal ""        # Normal ammo color
```

**Ammo Types:**
- `ammo1` - Shells (SG, SSG)
- `ammo2` - Nails (NG, SNG)
- `ammo3` - Rockets (RL, GL)
- `ammo4` - Cells (LG)

**Functions:**
- `HUD_AmmoLowByWeapon(weapon)` - Check if ammo is low for weapon
- `State_AmmoForWeapon(weapon)` - Get ammo count for weapon
- Low threshold: 10 or tp_need_* value

---

### Frags Display (`hud_frags.c`)

**Elements:** `frags`, `teamfrags`

**Purpose:** Show player frags/scores with extensive customization for spectating.

**Key CVars:**
```
hud_frags_show 0
hud_frags_cell_width 32              # Width per player cell
hud_frags_cell_height 8              # Height per player cell
hud_frags_rows 1                     # Number of rows
hud_frags_cols 4                     # Number of columns
hud_frags_vertical 0                 # 0=horizontal, 1=vertical, 2=by team
hud_frags_extra_spec_info "ALL"     # RL|LG|ARMOR|HEALTH|POWERUP|TEXT|HMETER|PMETER
hud_frags_style 0                    # 0-8: bracket/background styles
hud_frags_wipeout 1                  # Support wipeout mode (spawn timers)
hud_teamfrags_extra_spec_info 1      # 0-4: team display options
```

**Extra Spec Info Options:**
- RL - Rocket launcher icon/count
- LG - Lightning gun icon/count
- ARMOR - Armor value
- HEALTH - Health value
- POWERUP - Q/P/R indicators
- HMETER - Health bar
- PMETER - Armor bar (Power meter)

**Special Features:**
- Wipeout mode: Shows spawn timers and death indicators
- Flexible layout (horizontal, vertical, by-team)
- Health/armor bars for each player
- Weapon indicators (RL/LG counts)
- Powerup display (Quad, Pent, Ring)

---

### Speed Display (`hud_speed.c`)

**Elements:** `speed`, `speed2`

**Purpose:** Display player movement speed in various visual styles.

**Speed (Bar Style):**
```
hud_speed_show 0
hud_speed_xyz 0                      # 0=XY only, 1=include Z axis
hud_speed_width 160
hud_speed_height 15
hud_speed_style 0                    # 0=bar+text, 1=text, 2/3=split XYZ
hud_speed_color_stopped "52"         # Speed <100
hud_speed_color_normal "100"         # Speed 100-299
hud_speed_color_fast "72"            # Speed 300-499
hud_speed_color_fastest "216"        # Speed 500-699
hud_speed_color_insane "229"         # Speed 700+
```

**Speed2 (Semicircle Gauge):**
```
hud_speed2_show 0
hud_speed2_radius 50.0
hud_speed2_wrapspeed 500             # Speed at which needle wraps around
hud_speed2_orientation 0             # 0=up, 1=down, 2=right, 3=left
```

**Calculation:**
- XY speed: `sqrt(velocity.x² + velocity.y²)`
- XYZ speed: `sqrt(velocity.x² + velocity.y² + velocity.z²)`
- Units are QuakeWorld units per second

---

### Weapon Stats (`hud_weapon_stats.c`)

**Element:** `weaponstats`

**Purpose:** Display weapon accuracy percentages and hit counts.

**CVars:**
```
hud_weaponstats_show 0
hud_weaponstats_format "&c990sg&r:%2 &c099ssg&r:%3 &c900rl&r:#7 &c009lg&r:%8"
hud_weaponstats_textalign "center"   # left/right/center
```

**Format Codes:**
- `%N` - Accuracy percentage for weapon N (e.g., %2 = sg accuracy)
- `#N` - Hit count for weapon N (e.g., #7 = rl hits)

**Weapons:**
1. Axe, 2. SG (Shotgun), 3. SSG (Super Shotgun), 4. NG (Nailgun)
5. SNG (Super Nailgun), 6. GL (Grenade Launcher), 7. RL (Rocket Launcher), 8. LG (Lightning Gun)

**Commands:**
```
+cl_wp_stats  # Show weapon stats
-cl_wp_stats  # Hide weapon stats
```

**Data Source:** Server must send weapon stats (modern servers with `sv_weaponstats 1`)

---

### Tracker System (`vx_tracker.c`, `fragstats.c`)

**Element:** `tracker`

**Purpose:** Display frag/death/flag events in real-time with customizable messages.

**Core CVars:**
```
r_tracker 1                          # Enable tracker
r_tracker_frags 1                    # Show frag events
r_tracker_flags 0                    # Show flag events (CTF)
r_tracker_streaks 0                  # Show killing streaks
r_tracker_time 4                     # Display duration (seconds)
r_tracker_messages 20                # Max simultaneous messages
r_tracker_pickups 0                  # Show item pickups
r_tracker_align_right 1              # Align to right side
r_tracker_inconsole 0                # 0=HUD, 1=console, 2=both, 3=both+nonotify
```

**Colors:**
```
r_tracker_color_good "090"           # Good news (green)
r_tracker_color_bad "900"            # Bad news (red)
r_tracker_color_tkgood "990"         # Teamkill not on your team (yellow)
r_tracker_color_tkbad "009"          # Teamkill on your team (blue)
r_tracker_color_myfrag "090"         # Your frags
r_tracker_color_fragonme "900"       # You got fragged
r_tracker_color_suicide "900"        # Suicides
```

**Killing Streaks:**
```
5 kills:   "on a killing spree"  (spree)
10 kills:  "on a rampage"        (rampage)
15 kills:  "unstoppable"         (unstoppable)
20 kills:  "godlike"             (godlike)
50 kills:  "the master now"      (master)
100 kills: "teh chet"            (0wnhack)
```

**Fragfile System:**
- Loads from `fragfile.dat`
- Defines weapon obituary messages
- Customizable frag text
- Supports images for weapons

**Format:** `#FRAGFILE VERSION ezquake-1.00`

**Commands:**
```
loadFragfile <filename>  # Load custom fragfile
```

---

### Performance HUD (`hud_performance.c`)

**Elements:** `fps`, `ping`, `clock`, `frametime`

**FPS Counter:**
```
hud_fps_show 0
hud_fps_min_reset_interval 5.0      # Reset min FPS counter interval
```

**Commands:**
```
hud_fps_min_reset  # Reset minimum FPS tracking
```

**Features:**
- Current FPS
- Minimum FPS tracking
- Frame time display
- Average performance metrics

---

### Network Stats (`hud_net.c`)

**Elements:** `netgraph`, `netstats`

**Netgraph:**
```
hud_netgraph_show 0
hud_netgraph_width 256
hud_netgraph_height 64
hud_netgraph_ploss 1                 # Show packet loss
```

**Features:**
- Real-time network performance graph
- Packet loss visualization
- Latency spikes
- Connection quality indicators

---

### Items Clock (`hud_items.c`)

**Element:** `itemsclock`

**Purpose:** Display upcoming item respawn times.

**CVars:**
```
hud_itemsclock_show 0
hud_itemsclock_timelimit 5           # Show items respawning within N seconds
hud_itemsclock_style 0               # Display style
hud_itemsclock_filter ""             # Filter: RL|QUAD|RING|PENT|SUIT|LG|GL|SNG|MH|RA|YA|GA
hud_itemsclock_backpacks 0           # Include backpack respawns
```

**Features:**
- Countdown timers for major items
- Customizable filter (only show specific items)
- Helps with item timing strategy

---

### Team Info (`hud_teaminfo.c`)

**Element:** `teaminfo`

**Purpose:** Display teammate status (health, armor, items, location).

**Features:**
- Team member health/armor values
- Powerup status (Q/P/R)
- Location tracking
- Item pickup notifications
- Essential for team coordination

---

### Radar/Minimap (`hud_radar.c`)

**Element:** `radar`

**Purpose:** Top-down minimap showing player positions.

**Requirements:**
- Requires map radar images in textures directory
- Server must support player position data

**Functions:**
- `HUD_NewRadarMap()` - Load radar image for current map
- `Radar_HudInit()` - Initialize radar system

---

### Additional Elements (Brief)

**Face** (`hud_face.c`) - Player face with pain animations
**Guns** (`hud_guns.c`) - Current weapon display
**Clock** (`hud_clock.c`) - Real-time clock and match timer
**Scores** (`hud_scores.c`) - Scoreboard displays
**Tracking** (`hud_tracking.c`) - Spectator tracking info
**Center Print** (`hud_centerprint.c`) - Centered messages
**Auto ID** (`hud_autoid.c`) - Crosshair player identification
**QTV** (`hud_qtv.c`) - QTV stream information
**Game Summary** (`hud_gamesummary.c`) - Post-match stats
**Groups** (`hud_groups.c`) - HUD element grouping
**Notify** (`hud_common.c`) - Notification messages
**Static Text** (`hud_common.c`) - Custom text display
**Team Stack Bar** (`hud_common.c`) - Team damage capacity bar

---

## Console Commands

### HUD Management

```
show <element|all>           # Show HUD element(s)
hide <element|all>           # Hide HUD element(s)
togglehud <element|variable> # Toggle element or cvar
move <element> [x] [y]       # Set element position offset
place <element> [area]       # Set placement area
align <element> [ax] [ay]    # Set alignment
order <element> [option]     # Set draw order (forward/backward/front/back/#)
reset <element>              # Reset to center screen
hud_recalculate              # Recalculate all positions
hud_export                   # Export HUD config
hud_editor                   # Toggle visual HUD editor
```

### Element Shortcuts

For elements with `HUD_PLUSMINUS` flag:
```
+hud_<element>  # Show
-hud_<element>  # Hide
```

Example:
```
+hud_fps        # Show FPS counter
-hud_fps        # Hide FPS counter
```

---

## CVAR Reference

### Global HUD Settings

```
scr_newHud 1                 # Enable new HUD system (vs legacy)
cl_hud ""                    # HUD preset name to load
r_drawhud 1                  # Master HUD enable/disable
cl_hudswap 0                 # Swap left/right element sides
hud_planmode 0               # Planning mode (use test values)
hud_tp_need 0                # Use teamplay need thresholds for "low" checks
hud_digits_trim 1            # 0=999, 1=030, 2=100 (leading zero behavior)
hud_name_remove_prefixes ""  # Remove clan prefixes from names
```

### Universal Element CVars

Every element automatically gets:
```
hud_<element>_show <0-3>     # 0=hide, 1=show, 2=SP, 3=MP
hud_<element>_draw <0-3>     # Same as show
hud_<element>_place <area>   # Placement: screen/view/sbar/element_name/@element_name
hud_<element>_align_x <alignment>  # left/center/right/before/after
hud_<element>_align_y <alignment>  # top/center/bottom/console
hud_<element>_pos_x <offset> # X offset in pixels
hud_<element>_pos_y <offset> # Y offset in pixels
hud_<element>_order <num>    # Z-order (higher draws on top)
hud_<element>_frame <style>  # 0=none, 0.0-1.0=alpha box, 2=textbox
hud_<element>_frame_color <r g b>  # Frame RGB color
hud_<element>_item_opacity <0.0-1.0>  # Element opacity
```

Plus element-specific parameters.

### MVD Auto-HUD

```
mvd_autohud 0                # 0=off, 1=auto(1on1/4on4), 2=custom
```

Automatically loads HUD configs during MVD/demo playback:
- `cfg/mvdhud_1on1.cfg` - 1v1 matches
- `cfg/mvdhud_4on4.cfg` - 4v4 matches
- `cfg/mvdhud_custom.cfg` - Custom mode

---

## Tracking Systems

### Fragstats System (`fragstats.c`)

**Purpose:** Parse server messages to track kills, deaths, teamkills, and flag events.

**CVars:**
```
cl_parseFrags 1              # Parse frag messages
con_fragmessages 1           # Show in console
cl_loadFragfiles 1           # Load fragfile.dat
cl_useimagesinfraglog 0      # Use weapon images
```

**Functions:**
- `Stats_ParsePrint(s, level, cff)` - Parse print message for stats
- `Stats_Reset()` - Clear all stats
- `Stats_NewMap()` - Called on map change
- `Stats_GetBasicStats(num, playerstats)` - Get kills/deaths/TKs/suicides
- `Stats_GetFlagStats(num, playerstats)` - Get flag touches/fumbles/captures
- `Stats_IsActive()` - Check if fragstats enabled

**Fragfile Format:**
```
#FRAGFILE VERSION ezquake-1.00
#FRAGFILE GAMEDIR <dir|ANY>
#META TITLE <title>
#META AUTHOR <author>
#DEFINE WEAPON_CLASS <keyword> <name> <shortname> [imagename]
#DEFINE OBITUARY <type> <weapon> <msg1> [msg2]
#DEFINE FLAG_ALERT <type> <msg>
```

**Obituary Types:**
- PLAYER_DEATH - Player died (environmental)
- PLAYER_SUICIDE - Player killed self
- X_FRAGS_Y - Player X fragged player Y
- X_FRAGGED_BY_Y - Player X was fragged by player Y
- X_TEAMKILLS_Y - Player X teamkilled player Y
- X_TEAMKILLED_BY_Y - Player X was teamkilled by player Y
- X_FRAGS_UNKNOWN / X_TEAMKILLS_UNKNOWN - Unknown opponent

**Flag Alert Types:**
- X_TOUCHES_FLAG / X_GETS_FLAG / X_TAKES_FLAG
- X_DROPS_FLAG / X_FUMBLES_FLAG / X_LOSES_FLAG
- X_CAPTURES_FLAG / X_CAPS_FLAG / X_SCORES

**Weapon Helpers:**
```c
char *GetWeaponName(int num);              // "Rocket Launcher"
char *GetColoredWeaponName(int num, byte *color);  // Colored version
char *GetWeaponImageName(int num);         // "textures/wad/rl.png"
char *GetWeaponTextName(int num);          // "rl"
```

---

## Customization

### Visual HUD Editor

**Activate:**
```
hud_editor  # Toggle editor mode
```

**Features:**
- Click to select elements
- Drag to move (if `hud_editor_allowmove 1`)
- Resize handles (if `hud_editor_allowresize 1`)
- Alignment guides
- Real-time preview
- Mouse-based manipulation

**Editor CVars:**
```
hud_editor_allowresize 1
hud_editor_allowmove 1
hud_editor_allowplace 1
hud_editor_allowalign 1
```

### Element Relationships

**Snap to Another Element:**
```
place health face          # Place health outside face element
place health @face         # Place health inside face element
```

**Z-Order:**
- Higher numbers draw on top
- Children inherit parent's order + 1
- Use `order` command to adjust

### Config Files

**Locations:**
```
configs/*.cfg              # User HUD configs
cfg/mvdhud_*.cfg          # MVD auto-load configs
```

**Export Current HUD:**
```
hud_export  # Saves to configs directory
```

**Load HUD:**
```
exec configs/myhud.cfg
```

---

## Rendering Pipeline

### Draw Sequence

1. **HUD_BeforeDraw()** - Pre-draw setup (sort scoreboard, prepare data)
2. **For each element** (sorted by order):
   - **HUD_ShouldShow()** - Check visibility flags
   - Check minimum client state (ca_disconnected/connected/active)
   - Check event flags (intermission, scores, dialog, finale)
   - **Draw parent first** if element is attached to another
   - **Call element's draw_func()**
   - Update last_draw_sequence
3. **HUD_AfterDraw()** - Post-draw cleanup

### Positioning Calculation

**HUD_PrepareDraw(hud, width, height, &x, &y):**

1. Calculate frame thickness from `frame` cvar
2. Determine placement bounds:
   - If `place_hud` != NULL → use parent element bounds
   - Otherwise → use placement area (SCREEN/VIEW/SBAR/etc.)
3. Calculate X position:
   - LEFT: area_x
   - CENTER: area_x + (area_width - width) / 2
   - RIGHT: area_x + area_width - width
   - BEFORE: area_x - width
   - AFTER: area_x + area_width
4. Add `pos_x` offset
5. Calculate Y position (same logic with align_y)
6. Add `pos_y` offset
7. Draw frame if `frame` cvar set
8. Store position in lx, ly, lw, lh (for children)
9. Check HUD editor confirmation
10. Return whether to draw content

### Common Drawing Functions

**Draw Numbers:**
```c
void SCR_HUD_DrawNum(hud_t *hud, int num, qbool low,
    float scale, int style, int digits, char *s_align, qbool proportional)
```
Styles: 0=big (24x24), 1=small text (8x8), 2=big+minus, 3=golden

**Draw Bars:**
```c
void SCR_HUD_DrawBar(int direction, int value, float max_value,
    color_t color, int x, int y, int width, int height)
```
Direction: 0=horizontal, 1=vertical

**Draw Multiline Text:**
```c
void SCR_HUD_MultiLineString(hud_t* hud, const char* in,
    qbool large_font, int alignment, float scale, qbool proportional)
```
Alignment: 0=left, 1=right, 2=center

---

## Developer APIs

### Registering New Elements

```c
hud_t *HUD_Register(
    char *name,              // Element name
    char *var_alias,         // Alias (can be NULL)
    char *description,       // Help text
    int flags,               // HUD_* flags
    cactive_t min_state,     // Minimum client state
    int draw_order,          // Initial z-order
    hud_func_type draw_func, // void (*)(hud_t *)
    char *show,              // Default show value
    char *place,             // Default placement
    char *align_x,           // Default X alignment
    char *align_y,           // Default Y alignment
    char *pos_x,             // Default X offset
    char *pos_y,             // Default Y offset
    char *frame,             // Default frame
    char *frame_color,       // Default frame color
    char *item_opacity,      // Default opacity
    char *params, ...        // NULL-terminated pairs
)
```

**Example:**
```c
HUD_Register(
    "myelem", NULL, "My custom element.",
    HUD_PLUSMINUS | HUD_OPACITY, ca_active, 0,
    SCR_HUD_DrawMyElem,
    "0", "screen", "center", "center", "0", "0",
    "0", "255 255 255", "1",
    "myparam", "defaultvalue",
    NULL
);
```

### Drawing Function Template

```c
static void SCR_HUD_DrawMyElem(hud_t *hud)
{
    int x, y, width, height;
    static cvar_t *myparam = NULL;

    // Cache cvar lookup
    if (myparam == NULL) {
        myparam = HUD_FindVar(hud, "myparam");
    }

    // Calculate size
    width = 100;
    height = 20;

    // Prepare to draw (handles positioning, frame, visibility)
    if (HUD_PrepareDraw(hud, width, height, &x, &y)) {
        // Draw content at (x, y)
        Draw_String(x, y, "Hello!");
    }
}
```

### Finding Elements/CVars

```c
hud_t *HUD_Find(char *name);               // Find element by name
cvar_t *HUD_FindVar(hud_t *hud, char *subvar);  // Find element's cvar
cvar_t *Cvar_Find(char *name);             // Global cvar lookup
```

### Common Patterns

**Cvar Caching:**
```c
static cvar_t *my_cvar = NULL;
if (my_cvar == NULL) {
    my_cvar = HUD_FindVar(hud, "mycvar");
}
```

**Color Cvars:**
```c
cvar_t *color = HUD_FindInitTextColorVar(hud, "text_color");
// Auto-applies CVAR_COLOR flag
```

**Opacity:**
```c
Draw_SetOverallAlpha(hud->opacity->value);
// ... draw calls ...
Draw_SetOverallAlpha(1.0);
```

**Stat Access:**
```c
int hp = HUD_Stats(STAT_HEALTH);  // Respects hud_planmode
int armor = cl.stats[STAT_ARMOR];  // Direct access
```

---

## Teamplay Integration

### TP Need System

When `hud_tp_need 1`, HUD elements use these thresholds for "low" indicators:

```
tp_need_health <value>       # Health threshold (default: 25)
tp_need_ra <value>           # Red Armor threshold
tp_need_ya <value>           # Yellow Armor threshold
tp_need_ga <value>           # Green Armor threshold
tp_need_weapon <8-char>      # Weapon need string
tp_need_shells <value>       # Shells threshold
tp_need_nails <value>        # Nails threshold
tp_need_rockets <value>      # Rockets threshold (default: 10)
tp_need_cells <value>        # Cells threshold (default: 10)
```

**Usage:**
- Health/armor bars change color when below threshold
- Ammo displays show "low" color
- Team chat messages can reference these values

### Player Sorting

**Global Arrays (after HUD_Sort_Scoreboard):**
```c
extern sort_players_info_t sorted_players[MAX_CLIENTS];
extern sort_players_info_t sorted_players_by_frags[MAX_CLIENTS];
extern sort_teams_info_t sorted_teams[MAX_CLIENTS];
extern int n_teams, n_players, n_spectators;
```

**Sort Function:**
```c
void HUD_Sort_Scoreboard(int flags);
// Flags: HUD_SCOREBOARD_ALL, HUD_SCOREBOARD_SORT_TEAMS,
//        HUD_SCOREBOARD_SORT_PLAYERS, HUD_SCOREBOARD_UPDATE
```

**Team Info Structure:**
```c
typedef struct sort_teams_info_s {
    char *name;
    int frags, min_ping, avg_ping, max_ping, nplayers;
    int top, bottom;           // Team colors
    int rlcount, lgcount;      // Weapon counts
    int ra_taken, ya_taken, ga_taken, mh_taken;  // Item pickups
    int quads_taken, pents_taken, rings_taken;   // Powerups
    int stack;                 // Total damage team can take
    float ra_lasttime, ya_lasttime, ...;  // Last pickup times
} sort_teams_info_t;
```

**Stack Calculation:**
```c
float SCR_HUD_TotalStrength(float health, float armor, float armorType)
// Returns total damage player can sustain
// Formula: health + (armor * armorType) where armorType is absorption %
```

---

## Advanced Topics

### Text Rendering

**Proportional Fonts:**
- Most elements support `proportional` cvar
- 0 = Fixed-width (classic Quake, 8x8 chars)
- 1 = Proportional spacing (modern, variable width)

**Color Codes:**
- `&cRGB` - Set color (R/G/B hex digits 0-F)
  - Example: `&cf00` = red, `&c0f0` = green
- `&r` - Reset to default color
- Quake color codes: High-bit characters (0x80-0xFF)

**Example:**
```
"&cf00RED&r &c0f0GREEN&r &c00fBLUE&r"
```

### Conditional Display

**Show/Draw Values:**
- 0 = Never show
- 1 = Always show
- 2 = Single-player only
- 3 = Multiplayer only

**Event Flags:**
```c
HUD_ON_INTERMISSION  // Show during intermission
HUD_ON_FINALE        // Show during finale screen
HUD_ON_SCORES        // Show when scoreboard visible
HUD_ON_DIALOG        // Show during dialogs
HUD_NO_DRAW          // Only draw when specified flags match
```

### Frame Styles

**Frame Cvar Values:**
- `0` - No frame
- `0.0-1.0` - Semi-transparent box (alpha value)
- `2` - Textbox style (classic Quake border)

**Frame Growth:**
- Frames grow around content by default
- `HUD_NO_GROW` flag disables growth (fixed size)

---

## File Locations

**Core System:**
- `src/hud.h` (133 lines) - Main header
- `src/hud.c` (1647 lines) - Core implementation
- `src/hud_common.h` (107 lines) - Common utilities header
- `src/hud_common.c` (1111 lines) - Common utilities
- `src/hud_editor.c` - Visual editor
- `src/r_hud.c` - Rendering integration

**Elements (25 files):**
```
src/hud_262.c              src/hud_autoid.c          src/hud_face.c
src/hud_ammo.c             src/hud_centerprint.c     src/hud_frags.c
src/hud_armor.c            src/hud_clock.c           src/hud_gamesummary.c
src/hud_groups.c           src/hud_items.c           src/hud_qtv.c
src/hud_guns.c             src/hud_net.c             src/hud_radar.c
src/hud_health.c           src/hud_performance.c     src/hud_scores.c
src/hud_speed.c            src/hud_teaminfo.c        src/hud_tracking.c
src/hud_weapon_stats.c
```

**Tracking/Stats:**
- `src/vx_tracker.c` - Frag tracker
- `src/vx_tracker.h` - Tracker header
- `src/fragstats.c` - Stats parsing
- `src/stats_grid.c` - Stats grid

**Related:**
- `src/sbar.c` - Status bar (legacy HUD)
- `src/teamplay.c` - Teamplay mechanics
- `src/mvd_utils.c` - MVD utilities
- `src/mvd_autotrack.c` - MVD auto-tracking

---

## Additional Resources

**JSON Documentation:**
- `help_variables.json` (22,935 lines) - All cvars with metadata
- `help_commands.json` (2,105 lines) - All commands with descriptions

**Exploration Session:**
- Agent ID: `a18523a` - Resume for deeper investigation

**Repository:**
- https://github.com/QW-Group/ezquake-source
- Local clone: `/home/quakeuser/ezquake-source`

---

## Common Use Cases

### Creating a Minimal HUD

```
hide all                    # Hide everything
show health                 # Show health
show armor                  # Show armor
show ammo                   # Show ammo
show teamfrags              # Show team scores
```

### Creating a Spectator HUD

```
show frags                  # Show all players
show teamfrags              # Show team scores
show tracking               # Show who you're tracking
hud_frags_extra_spec_info "ALL"  # Show RL/LG/health/armor
```

### Positioning Elements

```
place health screen         # Place health relative to screen
align health left top       # Align to top-left
move health 10 10           # Offset 10 pixels from corner
```

### Creating Element Groups

```
place armor @health         # Place armor inside health bounds
align armor left center     # Align to left-center of health
pos armor 32 0              # 32 pixels to the right
```

---

## Troubleshooting

**Element not showing:**
1. Check `hud_<element>_show 1`
2. Check `r_drawhud 1`
3. Check `scr_newHud 1`
4. Check minimum state requirement (might need ca_active)

**Element in wrong position:**
1. Try `reset <element>`
2. Check `place`, `align_x`, `align_y`, `pos_x`, `pos_y` cvars
3. Use `hud_recalculate` to refresh

**Colors not working:**
1. Check `hud_<element>_frame_color` format (should be "R G B")
2. Check opacity settings
3. Check color cvar format for text elements

**Tracker not working:**
1. Ensure `r_tracker 1`
2. Check `cl_parseFrags 1`
3. Verify `con_fragmessages 1`
4. Load fragfile: `loadFragfile fragfile.dat`

---

## FAQ

**Q: How do I make elements transparent?**
A: Use `hud_<element>_item_opacity 0.5` (0.0-1.0 scale)

**Q: Can I show element only during spectating?**
A: Not directly, but you can script with `togglehud` bound to spec mode

**Q: How do I export my HUD?**
A: Type `hud_export`, then find it in `configs/` directory

**Q: Can I use multiple HUD configs?**
A: Yes! Create different .cfg files and `exec` them

**Q: What's the difference between show and draw?**
A: They're aliases - both control visibility. Use whichever you prefer.

**Q: How do I position an element relative to another?**
A: Use `place <element> <target>` for outside, or `place <element> @<target>` for inside

**Q: Can I change draw order?**
A: Yes! Use `order <element> forward/backward/front/back/#`

**Q: How do I reset a messed-up element?**
A: Type `reset <element>` to reset to center screen

---

*End of ezQuake HUD Expert Knowledge Base*
