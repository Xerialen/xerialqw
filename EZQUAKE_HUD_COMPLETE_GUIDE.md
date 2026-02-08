# ezQuake HUD & Tracking Systems - Complete Documentation

**Generated:** 2026-02-08
**Source:** ezQuake source code analysis
**Agent ID:** a18523a (for continued exploration)

---

## Table of Contents

1. [HUD Architecture & Core System](#1-hud-architecture--core-system)
2. [All HUD Elements Documented](#2-all-hud-elements-documented)
3. [Console Commands](#3-console-commands)
4. [Global HUD CVars](#4-global-hud-cvars)
5. [Damage & Stat Tracking](#5-damage--stat-tracking)
6. [Rendering Pipeline](#6-rendering-pipeline)
7. [Customization System](#7-customization-system)
8. [Advanced Features](#8-advanced-features)
9. [Developer Reference](#9-developer-reference)
10. [File Locations Summary](#10-file-locations-summary)

---

## 1. HUD ARCHITECTURE & CORE SYSTEM

### 1.1 Core Files

**Primary HUD System:**
- `hud.h` / `hud.c` - Core HUD framework and registration system
- `hud_common.h` / `hud_common.c` - Common HUD utilities and initialization
- `hud_editor.h` / `hud_editor.c` - Interactive HUD editor
- `r_hud.c` - Rendering-specific HUD code

**Total HUD Element Files: 25**
```
hud_262.c           - Legacy HUD system compatibility
hud_ammo.c          - Ammo displays (current + all 4 types)
hud_armor.c         - Armor value & icon displays
hud_autoid.c        - Auto-identification system
hud_centerprint.c   - Centerprint messages
hud_clock.c         - Clock/time displays
hud_face.c          - Player face icon
hud_frags.c         - Frag counters (player & team)
hud_gamesummary.c   - Game summary/stats
hud_groups.c        - HUD grouping system
hud_guns.c          - Weapon models/displays
hud_health.c        - Health displays
hud_items.c         - Item pickups/status
hud_net.c           - Network statistics
hud_performance.c   - FPS/performance metrics
hud_qtv.c           - QTV-specific elements
hud_radar.c         - Radar/minimap
hud_scores.c        - Scoreboard displays
hud_speed.c         - Speedometer displays
hud_teaminfo.c      - Team information
hud_tracking.c      - Spectator tracking display
hud_weapon_stats.c  - Weapon accuracy statistics
```

### 1.2 HUD Element Structure (`hud_t`)

Located in `hud.h` (lines 67-118):

```c
typedef struct hud_s {
    char *name;              // Element name
    char *description;       // Help text
    void (*draw_func)(struct hud_s *);  // Drawing function

    cvar_t *order;           // Z-order (draw priority)
    cvar_t *show;            // Visibility cvar
    cvar_t *draw;            // Content draw cvar
    cvar_t *frame;           // Frame style
    cvar_t *frame_color;     // Frame color
    byte frame_color_cache[4];
    qbool frame_hide;
    cvar_t *opacity;         // Overall opacity

    // Placement system
    cvar_t *place;           // Place string
    struct hud_s *place_hud; // Parent HUD element
    qbool place_outside;     // Inside/outside parent
    int place_num;           // Placement type

    // Alignment
    cvar_t *align_x, *align_y;
    int align_x_num, align_y_num;

    // Position
    cvar_t *pos_x, *pos_y;

    // Custom parameters
    cvar_t **params;
    int num_params;

    cactive_t min_state;     // Minimum client state required
    unsigned flags;

    // Last draw parameters (for children)
    int lx, ly, lw, lh;      // Last position
    int al, ar, at, ab;      // Last frame params

    int last_try_sequence;
    int last_draw_sequence;

    struct hud_s *next;      // Linked list
} hud_t;
```

### 1.3 HUD Flags (lines 25-41 of hud.h)

```c
#define HUD_NO_DRAW         (1<<0)   // Draw only during events
#define HUD_NO_SHOW         (1<<1)   // Doesn't support show/hide
#define HUD_NO_POS_X        (1<<2)   // No X positioning
#define HUD_NO_POS_Y        (1<<3)   // No Y positioning
#define HUD_NO_FRAME        (1<<4)   // No frame support
#define HUD_ON_DIALOG       (1<<5)   // Draw on dialogs
#define HUD_ON_INTERMISSION (1<<6)   // Draw on intermission
#define HUD_ON_FINALE       (1<<7)   // Draw on finale
#define HUD_ON_SCORES       (1<<8)   // Draw on scoreboard
#define HUD_NO_GROW         (1<<9)   // No frame growth
#define HUD_PLUSMINUS       (1<<10)  // Auto +/- commands
#define HUD_OPACITY         (1<<11)  // Opacity support
#define HUD_INVENTORY       HUD_NO_GROW  // For status bar elements
```

### 1.4 Placement System (lines 47-56 of hud.h)

```c
#define HUD_PLACE_SCREEN    1  // Entire screen
#define HUD_PLACE_TOP       2  // Screen minus status bar
#define HUD_PLACE_VIEW      3  // View area
#define HUD_PLACE_SBAR      4  // Status bar
#define HUD_PLACE_IBAR      5  // Inventory bar
#define HUD_PLACE_HBAR      6  // Health bar
#define HUD_PLACE_SFREE     7  // Status bar free area
#define HUD_PLACE_IFREE     8  // Inventory bar free area
#define HUD_PLACE_HFREE     9  // Health bar free area
```

### 1.5 Alignment System (lines 58-66 of hud.h)

```c
// Horizontal
#define HUD_ALIGN_LEFT      1
#define HUD_ALIGN_CENTER    2
#define HUD_ALIGN_RIGHT     3
#define HUD_ALIGN_BEFORE    4  // Before element
#define HUD_ALIGN_AFTER     5  // After element

// Vertical
#define HUD_ALIGN_TOP       1
#define HUD_ALIGN_BOTTOM    3
#define HUD_ALIGN_CONSOLE   6  // Below console
```

---

## 2. ALL HUD ELEMENTS DOCUMENTED

### 2.1 **Health** (`hud_health.c`)
**Elements:** `health`, `healthdamage`, `bar_health`

**Default CVars:**
```
hud_health_show 1
hud_health_place "face"
hud_health_align_x "after"
hud_health_align_y "center"
hud_health_style 0           // 0=big nums, 1=small text, 2=big with minus, 3=golden
hud_health_scale 1
hud_health_digits 3
hud_health_align "right"
hud_health_proportional 0
```

**Health Damage Tracking:**
```
hud_healthdamage_show 0
hud_healthdamage_duration 0.8  // How long damage flash lasts
```

**Health Bar:**
```
hud_bar_health_width 64
hud_bar_health_height 16
hud_bar_health_direction 0     // 0=horizontal, 1=vertical
hud_bar_health_color_nohealth "128 128 128 64"
hud_bar_health_color_normal "32 64 128 128"
hud_bar_health_color_mega "64 96 128 128"
hud_bar_health_color_twomega "128 128 255 128"
hud_bar_health_color_unnatural "255 255 255 128"
```

**Functions:**
- `SCR_HUD_DrawHealth()` - Main health display
- `SCR_HUD_DrawHealthDamage()` - Damage tracking
- `SCR_HUD_DrawBarHealth()` - Health bar
- `HUD_HealthLow()` - Check if health is low (<=25 or tp_need threshold)

---

### 2.2 **Armor** (`hud_armor.c`)
**Elements:** `armor`, `iarmor`, `armordamage`, `bar_armor`

**Default CVars:**
```
hud_armor_show 1
hud_armor_place "face"
hud_armor_align_x "before"
hud_armor_pos_x -32
hud_armor_style 0            // 0=big nums, 1=text
hud_armor_scale 1
hud_armor_digits 3
hud_armor_pent_666 1         // Show 666 when carrying pentagram
hud_armor_hidezero 0         // Hide when armor is 0
hud_armor_proportional 0
```

**Armor Icon:**
```
hud_iarmor_show 1
hud_iarmor_style 0           // 0=graphic, 1=text (r/y/g/@)
hud_iarmor_scale 1
```

**Armor Bar:**
```
hud_bar_armor_width 64
hud_bar_armor_height 16
hud_bar_armor_direction 1
hud_bar_armor_color_noarmor "128 128 128 64"
hud_bar_armor_color_ga "32 128 0 128"
hud_bar_armor_color_ga_over "48 160 0 128"  // GA > 100
hud_bar_armor_color_ya "192 128 0 128"
hud_bar_armor_color_ra "128 0 0 128"
hud_bar_armor_color_unnatural "255 255 255 128"
```

---

### 2.3 **Ammo** (`hud_ammo.c`)
**Elements:** `ammo`, `ammo1-4`, `iammo`, `iammo1-4`

**Current Ammo:**
```
hud_ammo_show 1
hud_ammo_place "health"
hud_ammo_align_x "after"
hud_ammo_pos_x 32
hud_ammo_style 0             // 0/2=big nums, 1/3=text
hud_ammo_scale 1
hud_ammo_digits 3
hud_ammo_show_always 0       // Show even when no weapon selected
hud_ammo_text_color_low ""
hud_ammo_text_color_normal ""
```

**Individual Ammo Types:**
- `ammo1` - Shells
- `ammo2` - Nails
- `ammo3` - Rockets
- `ammo4` - Cells

Each has: style, scale, digits, align, proportional, text_color_low, text_color_normal

**Functions:**
- `HUD_AmmoLowByWeapon(int weapon)` - Check if ammo is low for weapon
- `State_AmmoNumForWeapon(int weapon)` - Get ammo type for weapon
- `State_AmmoForWeapon(int weapon)` - Get ammo amount for weapon

---

### 2.4 **Frags** (`hud_frags.c`)
**Elements:** `frags`, `teamfrags`

**Frags (Individual Players):**
```
hud_frags_show 0
hud_frags_cell_width 32
hud_frags_cell_height 8
hud_frags_rows 1
hud_frags_cols 4
hud_frags_space_x 1
hud_frags_space_y 1
hud_frags_vertical 0         // 0=horizontal, 1=vertical, 2=by team
hud_frags_strip 1            // Auto-adjust rows/cols
hud_frags_shownames 0
hud_frags_showteams 0
hud_frags_hidefrags 0
hud_frags_wipeout 1          // Support wipeout mode
hud_frags_padtext 1
hud_frags_extra_spec_info "ALL"  // RL|LG|ARMOR|HEALTH|POWERUP|TEXT|HMETER|PMETER
hud_frags_fliptext 0         // 0=normal, 1=flip, 2/3=alternate
hud_frags_style 0            // 0-8: various bracket/background styles
hud_frags_bignum 0           // Use big numbers
hud_frags_colors_alpha 1.0
hud_frags_maxname 16
hud_frags_notintp 0          // Don't show in teamplay
hud_frags_fixedwidth 0
hud_frags_scale 1
hud_frags_proportional 0
```

**Team Frags:**
```
hud_teamfrags_show 1
hud_teamfrags_cell_width 32
hud_teamfrags_cell_height 8
hud_teamfrags_rows 1
hud_teamfrags_cols 2
hud_teamfrags_extra_spec_info 1  // 0-4: none/before/ontop/noicon/rltext
hud_teamfrags_onlytp 0       // Only in teamplay
```

**Special Features:**
- Health/armor bars for players
- RL/LG indicators
- Powerup display (Q/P/R)
- Wipeout mode support (spawn timers, death indicators)
- Flexible layout system

---

### 2.5 **Speed** (`hud_speed.c`)
**Elements:** `speed`, `speed2`

**Speed (Bar Style):**
```
hud_speed_show 0
hud_speed_xyz 0              // 0=XY only, 1=XYZ
hud_speed_width 160
hud_speed_height 15
hud_speed_opacity 1.0
hud_speed_tick_spacing 0.2
hud_speed_vertical 0
hud_speed_vertical_text 1
hud_speed_text_align 1       // 0=none, 1=close, 2=center, 3=far
hud_speed_style 0            // 0=bar+text, 1=text, 2/3=split XYZ
hud_speed_color_stopped "52"
hud_speed_color_normal "100"
hud_speed_color_fast "72"
hud_speed_color_fastest "216"
hud_speed_color_insane "229"
hud_speed_scale 1
hud_speed_proportional 0
```

**Speed2 (Semicircle Style):**
```
hud_speed2_show 0
hud_speed2_xyz 0
hud_speed2_radius 50.0
hud_speed2_wrapspeed 500     // Speed at which needle wraps
hud_speed2_orientation 0     // 0=up, 1=down, 2=right, 3=left
hud_speed2_opacity 1.0
hud_speed2_scale 1
```

---

### 2.6 **Weapon Stats** (`hud_weapon_stats.c`)
**Element:** `weaponstats`

**CVars:**
```
hud_weaponstats_show 0
hud_weaponstats_format "&c990sg&r:%2 &c099ssg&r:%3 &c900rl&r:#7 &c009lg&r:%8"
hud_weaponstats_textalign "center"  // left/right/center
hud_weaponstats_scale 1
hud_weaponstats_proportional 0
```

**Format Codes:**
- `%N` - Accuracy percentage for weapon N (1-8)
- `#N` - Hit count for weapon N
- Weapons: 1=axe, 2=sg, 3=ssg, 4=ng, 5=sng, 6=gl, 7=rl, 8=lg

**Commands:**
```
+cl_wp_stats / -cl_wp_stats  // Toggle display
```

**Functions:**
- `Parse_WeaponStats(char *s)` - Parse weapon stats from server
- `SCR_CreateWeaponStatsPlayerText()` - Format display text
- `SCR_ClearWeaponStats()` - Reset on map change

---

### 2.7 **Tracker** (`vx_tracker.c`, `fragstats.c`)
**Element:** `tracker`

**Core Tracker CVars:**
```
r_tracker 1
r_tracker_flags 0            // Show flag events
r_tracker_frags 1            // Show frag events
r_tracker_streaks 0          // Show kill streaks
r_tracker_time 4             // Display duration (seconds)
r_tracker_messages 20        // Max simultaneous messages
r_tracker_pickups 0          // Show item pickups
r_tracker_align_right 1
r_tracker_scale 1
r_tracker_images_scale 1
r_tracker_proportional 0
r_tracker_x 0
r_tracker_y 0
r_tracker_frame_color "0 0 0 0"
r_tracker_inconsole 0        // 0=HUD, 1=console, 2=both, 3=both+nonotify
r_tracker_inconsole_colored_weapon 0
r_tracker_colorfix 0
```

**Tracker Colors:**
```
r_tracker_color_good "090"       // Good news
r_tracker_color_bad "900"        // Bad news
r_tracker_color_tkgood "990"     // TK not on your team
r_tracker_color_tkbad "009"      // TK on your team
r_tracker_color_myfrag "090"     // Your frags
r_tracker_color_fragonme "900"   // Fragged you
r_tracker_color_suicide "900"    // Suicides
```

**Tracker Strings:**
```
r_tracker_string_suicides " (suicides)"
r_tracker_string_died " (died)"
r_tracker_string_teammate "teammate"
r_tracker_string_enemy "enemy"
r_tracker_string_inconsole_prefix ""
r_tracker_own_frag_prefix "You fragged "
```

**Tracker Features:**
```
r_tracker_name_width 0       // Fixed name width (0=auto)
r_tracker_positive_enemy_suicide 0
r_tracker_positive_enemy_vs_enemy 0
r_tracker_weapon_first 0     // Show weapon before name
```

**Killing Streaks** (from `vx_tracker.c`):
```c
{ 100, "teh chet",           "0wnhack" },
{ 50,  "the master now",     "master" },
{ 20,  "godlike",            "godlike" },
{ 15,  "unstoppable",        "unstoppable" },
{ 10,  "on a rampage",       "rampage" },
{ 5,   "on a killing spree", "spree" }
```

**Fragfile System:**
- Loads from `fragfile.dat`
- Defines weapon classes and obituary messages
- Supports custom frag messages
- Format: ezquake-1.00

**Commands:**
```
loadFragfile <filename>  // Load custom fragfile
```

---

### 2.8 **Performance** (`hud_performance.c`)
**Elements:** `fps`, `ping`, `clock`, etc.

**FPS Counter:**
```
hud_fps_show 0
hud_fps_min_reset_interval 5.0
```

**Frame Time:**
```
hud_frametime_max_reset_interval 5.0
hud_performance_average 1
```

**Commands:**
```
hud_fps_min_reset  // Reset minimum FPS counter
```

---

### 2.9 **Clock** (`hud_clock.c`)
**Element:** `clock`

**Features:**
- Real-world time display
- Demo/match time tracking
- Customizable format

---

### 2.10 **Scores** (`hud_scores.c`)
**Element:** `scores`

**Sort CVars:**
```
hud_sortrules_playersort "frags"
hud_sortrules_teamsort "frags"
hud_sortrules_includeself 1
```

**Functions:**
- `HUD_Sort_Scoreboard(int flags)` - Sort players/teams
- Flags: HUD_SCOREBOARD_SORT_TEAMS, HUD_SCOREBOARD_SORT_PLAYERS, etc.

---

### 2.11 **Network** (`hud_net.c`)
**Elements:** `netgraph`, `netstats`

**Netgraph:**
```
hud_netgraph_show 0
hud_netgraph_width 256
hud_netgraph_height 64
hud_netgraph_swap_x 0
hud_netgraph_swap_y 0
hud_netgraph_ploss 1         // Show packet loss
```

---

### 2.12 **Team Info** (`hud_teaminfo.c`)
**Element:** `teaminfo`

**Features:**
- Team member health/armor
- Item pickups
- Powerup status
- Location tracking

---

### 2.13 **Items** (`hud_items.c`)
**Element:** `items`, `itemsclock`

**Items Clock:**
```
hud_itemsclock_show 0
hud_itemsclock_timelimit 5
hud_itemsclock_style 0
hud_itemsclock_scale 1
hud_itemsclock_filter ""     // RL|QUAD|RING|PENT|SUIT|LG|GL|SNG|MH|RA|YA|GA
hud_itemsclock_backpacks 0
hud_itemsclock_proportional 0
```

**Displays upcoming item respawns**

---

### 2.14 **Face** (`hud_face.c`)
**Element:** `face`

- Player face icon
- Shows damage direction
- Pain animations

---

### 2.15 **Guns** (`hud_guns.c`)
**Element:** `guns`

- Current weapon display
- Weapon switching
- Preselection system

---

### 2.16 **Groups** (`hud_groups.c`)
**Element:** `groups`

- HUD element grouping
- Batch show/hide

---

### 2.17 **Center Print** (`hud_centerprint.c`)
**Element:** `centerprint`

- Centered message display
- Server messages
- Print priorities

---

### 2.18 **Tracking** (`hud_tracking.c`)
**Element:** `tracking`

**Spectator Tracking:**
```
hud_tracking_show 1
hud_tracking_format "Tracking: %t %n, JUMP for next"
hud_tracking_scale 1
hud_tracking_proportional 0
scr_tracking (same format)
scr_spectatorMessage 1
```

**Format codes:**
- `%n` - Player name
- `%t` - Team name (if teamplay)

---

### 2.19 **Radar** (`hud_radar.c`)
**Element:** `radar`

- Minimap display
- Player positions
- Requires map images

**Functions:**
- `HUD_NewRadarMap()` - Load radar for new map
- `Radar_HudInit()` - Initialize radar system

---

### 2.20 **QTV** (`hud_qtv.c`)
**Element:** `qtv`

- QTV stream information
- Viewer count
- Stream status

---

### 2.21 **Auto ID** (`hud_autoid.c`)
**Element:** `autoid`

- Automatic player identification
- Crosshair names
- Distance display

---

### 2.22 **Game Summary** (`hud_gamesummary.c`)
**Element:** `gamesummary`

- End-of-match statistics
- Team comparison
- Player rankings

---

### 2.23 **Notify** (`hud_common.c`)
**Element:** `notify`

```
hud_notify_show 0
hud_notify_rows 4
hud_notify_cols 30
hud_notify_scale 1
hud_notify_time 4
hud_notify_proportional 0
```

---

### 2.24 **Static Text** (`hud_common.c`)
**Element:** `static_text`

```
hud_static_text_show 0        // Demos only
hud_static_text_big 0
hud_static_text_scale 1
hud_static_text_text ""
hud_static_text_textalign "left"  // left/right/center
hud_static_text_proportional 0
```

---

### 2.25 **Team Stack Bar** (`hud_common.c`)
**Element:** `teamstackbar`

```
hud_teamstackbar_show 0
hud_teamstackbar_opacity 0.8
hud_teamstackbar_width 200
hud_teamstackbar_height 8
hud_teamstackbar_vertical 0
hud_teamstackbar_vertical_text 0
hud_teamstackbar_show_text 1
hud_teamstackbar_onlytp 0
hud_teamstackbar_scale 1
hud_teamstackbar_proportional 0
```

---

## 3. CONSOLE COMMANDS

### 3.1 HUD Management Commands

```
show <element|all>           // Show HUD element(s)
hide <element|all>           // Hide HUD element(s)
togglehud <element|variable> // Toggle element or cvar
move <element> [x] [y]       // Set element offset
place <element> [area]       // Set element placement
align <element> [ax] [ay]    // Set element alignment
order <element> [option]     // Set draw order (forward/backward/front/back/#)
reset <element>              // Reset element to center screen
hud_recalculate              // Recalculate all element positions
hud_export                   // Export HUD configuration
hud_editor                   // Toggle HUD editor mode
```

### 3.2 HUD Element Shortcuts

For elements with `HUD_PLUSMINUS` flag:
```
+hud_<element>  // Show element
-hud_<element>  // Hide element
```

### 3.3 Legacy HUD Commands (hud_262.c)

```
hud262_add <element>
hud262_remove <element>
hud262_position <element> <x> <y>
hud262_bg <element> <color>
hud262_move <element> <x> <y>
hud262_width <element> <width>
hud262_alpha <element> <alpha>
hud262_blink <element>
hud262_disable <element>
hud262_enable <element>
hud262_list
hud262_bringtofront <element>
```

---

## 4. GLOBAL HUD CVARS

### 4.1 Core System

```
scr_newHud 1                 // Enable new HUD system
cl_hud ""                    // HUD preset name
r_drawhud 1                  // Draw HUD
cl_hudswap 0                 // Swap left/right HUD elements
hud_planmode 0               // Planning mode (test values)
hud_tp_need 0                // Use teamplay need thresholds
hud_digits_trim 1            // 0=999, 1=030, 2=100
hud_name_remove_prefixes ""  // Remove clan prefixes
```

### 4.2 Multiview

```
cl_mvdisplayhud 1
cl_mvhudvertical 0
cl_mvhudflip 0
cl_mvhudpos 0
cl_mvinsethud 1
```

### 4.3 Rankings/Scoreboard

```
scr_compactHud 0
scr_compactHudAlign 0
hud_centerranking 0
hud_rankingpos_x 0
hud_rankingpos_y 0
hud_faderankings 1
```

### 4.4 Editor

```
hud_editor_allowresize 1
hud_editor_allowmove 1
hud_editor_allowplace 1
hud_editor_allowalign 1
```

### 4.5 MVD Auto-HUD

```
mvd_autohud 0                // 0=off, 1=auto(1on1/4on4), 2=custom
```

**Behavior:**
- Automatically loads HUD config for MVD playback
- Saves temp config to restore after playback
- Configs: `cfg/mvdhud_1on1.cfg`, `cfg/mvdhud_4on4.cfg`, `cfg/mvdhud_custom.cfg`

---

## 5. DAMAGE & STAT TRACKING

### 5.1 Fragstats System (`fragstats.c`)

**Core CVars:**
```
cl_parseFrags 1              // Parse frag messages
con_fragmessages 1           // Show frag messages in console
cl_loadFragfiles 1           // Load fragfile.dat
cl_useimagesinfraglog 0      // Use images in frag log
```

**Functions:**
- `Stats_ParsePrint(char *s, int level, cfrags_format *cff)` - Parse print messages for frags
- `Stats_Reset()` - Reset all stats
- `Stats_NewMap()` - Called on map change
- `Stats_GetBasicStats(int num, int *playerstats)` - Get kills/deaths/TKs/suicides
- `Stats_GetFlagStats(int num, int *playerstats)` - Get touches/fumbles/captures
- `Stats_EnterSlot(int num)` - Initialize player slot
- `Stats_IsActive()` - Check if fragstats enabled
- `Stats_IsFlagsParsed()` - Check if flag parsing enabled

**Fragfile Format:**
```
#FRAGFILE VERSION ezquake-1.00
#FRAGFILE GAMEDIR <dir|ANY>
#META TITLE <title>
#META AUTHOR <author>
#META DESCRIPTION <desc>
#META EMAIL <email>
#META WEBPAGE <url>
#DEFINE WEAPON_CLASS <keyword> <name> <shortname> [imagename]
#DEFINE OBITUARY <type> <weapon> <msg1> [msg2]
#DEFINE FLAG_ALERT <type> <msg>
```

**Obituary Types:**
- PLAYER_DEATH
- PLAYER_SUICIDE
- X_FRAGS_UNKNOWN
- X_TEAMKILLS_UNKNOWN
- X_FRAGS_Y
- X_FRAGGED_BY_Y
- X_TEAMKILLS_Y
- X_TEAMKILLED_BY_Y
- X_TEAMKILLED_UNKNOWN

**Flag Alert Types:**
- X_TOUCHES_FLAG / X_GETS_FLAG / X_TAKES_FLAG
- X_DROPS_FLAG / X_FUMBLES_FLAG / X_LOSES_FLAG
- X_CAPTURES_FLAG / X_CAPS_FLAG / X_SCORES

**Weapon Functions:**
- `GetWeaponName(int num)` - Get weapon display name
- `GetColoredWeaponName(int num, const byte *color)` - Get colored weapon name
- `GetWeaponImageName(int num)` - Get weapon image path
- `GetWeaponTextName(int num)` - Get weapon text name

---

## 6. RENDERING PIPELINE

### 6.1 Draw Sequence (from `hud.c`)

1. **HUD_BeforeDraw()** - Pre-draw setup (sort scoreboard)
2. **HUD_DrawObject(hud)** for each element:
   - Check visibility (`HUD_ShouldShow()`)
   - Check min state requirement
   - Check event flags (intermission, scores, etc.)
   - Draw parent first if attached to another element
   - Call element's `draw_func()`
   - Update `last_draw_sequence`
3. **HUD_AfterDraw()** - Post-draw cleanup

### 6.2 Positioning Calculation (`HUD_PrepareDraw()`)

1. Calculate frame extents based on `frame` cvar
2. Determine bounds based on `place`:
   - If `place_hud` != NULL, use parent bounds
   - Otherwise use placement area (screen/view/sbar/etc.)
3. Calculate horizontal position based on `align_x`:
   - LEFT: area_x
   - CENTER: area_x + (area_width - width) / 2
   - RIGHT: area_x + area_width - width
   - BEFORE: area_x - width
   - AFTER: area_x + area_width
4. Add `pos_x` offset
5. Repeat for vertical with `align_y` and `pos_y`
6. Draw frame if needed
7. Store position in `lx, ly, lw, lh` for children
8. Check HUD editor confirmation
9. Return whether to draw content

### 6.3 Common Drawing Functions (`hud_common.c`)

```c
void SCR_HUD_DrawNum(hud_t *hud, int num, qbool low,
    float scale, int style, int digits, char *s_align, qbool proportional)
```
**Styles:**
- 0: Big numbers (24x24 scale)
- 1: Small text (8x8)
- 2: Big numbers with minus sign
- 3: Golden numbers

```c
void SCR_HUD_DrawBar(int direction, int value, float max_value,
    color_t color, int x, int y, int width, int height)
```
**Direction:** 0=horizontal, 1=vertical

```c
void SCR_HUD_MultiLineString(hud_t* hud, const char* in,
    qbool large_font, int alignment, float scale, qbool proportional)
```
**Alignment:** 0=left, 1=right, 2=center

---

## 7. CUSTOMIZATION SYSTEM

### 7.1 Per-Element CVars

Every HUD element gets these automatically:
```
hud_<element>_show <0|1|2|3>     // 0=hide, 1=show, 2=SP only, 3=MP only
hud_<element>_draw <0|1|2|3>     // Same values
hud_<element>_place <placement>
hud_<element>_align_x <alignment>
hud_<element>_align_y <alignment>
hud_<element>_pos_x <offset>
hud_<element>_pos_y <offset>
hud_<element>_order <z-order>
hud_<element>_frame <0|0.0-1.0|2>  // 0=none, 0.0-1.0=alpha box, 2=textbox
hud_<element>_frame_color <r g b>
hud_<element>_item_opacity <0.0-1.0>
```

Plus element-specific parameters passed to `HUD_Register()`.

### 7.2 Configuration Files

**HUD configs stored in:**
```
configs/*.cfg               // User configs
cfg/mvdhud_*.cfg           // MVD auto-load configs
```

**Export command:**
```
hud_export  // Saves current HUD to configs directory
```

### 7.3 HUD Editor Mode

**Activate:**
```
hud_editor  // Toggle editor
```

**Features:**
- Visual element selection
- Drag-and-drop positioning
- Resize handles (if allowed)
- Alignment guides
- Real-time preview
- Controlled by:
  - `hud_editor_allowresize`
  - `hud_editor_allowmove`
  - `hud_editor_allowplace`
  - `hud_editor_allowalign`

---

## 8. ADVANCED FEATURES

### 8.1 Element Relationships

**Snap to Another Element:**
```
place fps ping          // Place fps outside ping element
place fps @ping         // Place fps inside ping element
```

**Z-Order Management:**
- Higher order values draw on top
- Children auto-inherit parent's order + 1
- Use `order` command to adjust

### 8.2 Conditional Display

**Show/Draw Values:**
- 0 = Never
- 1 = Always
- 2 = Single-player only
- 3 = Multiplayer only

**Event Flags:**
```c
HUD_NO_DRAW              // Must specify additional flags
HUD_ON_INTERMISSION      // Show during intermission
HUD_ON_FINALE            // Show during finale
HUD_ON_SCORES            // Show with scoreboard
HUD_ON_DIALOG            // Show during dialogs
```

### 8.3 Text Rendering

**Proportional Fonts:**
- Most elements support `proportional` cvar
- 0 = Fixed-width (classic Quake)
- 1 = Proportional spacing

**Color Codes:**
- `&cRGB` - Set color (R/G/B = 0-F)
- `&r` - Reset to default
- Quake color codes (0x80 + char for colored chars)

### 8.4 Teamplay Integration

**TP Need System:**
```
tp_need_health <value>
tp_need_ra <value>
tp_need_ya <value>
tp_need_ga <value>
tp_need_weapon <8-char string>
tp_need_shells <value>
tp_need_nails <value>
tp_need_rockets <value>
tp_need_cells <value>
```

When `hud_tp_need 1`:
- Health/armor/ammo "low" indicators use these thresholds
- Otherwise uses hardcoded 25/10 values

### 8.5 Stats Calculation

**Player Sorting** (`hud_common.c`):
```c
typedef struct sort_players_info_s {
    int playernum;
    sort_teams_info_t *team;
} sort_players_info_t;

typedef struct sort_teams_info_s {
    char *name;
    int frags, min_ping, avg_ping, max_ping, nplayers;
    int top, bottom;           // Colors
    int rlcount, lgcount, weapcount;
    int ra_taken, ya_taken, ga_taken, mh_taken;
    int quads_taken, pents_taken, rings_taken;
    int stack;                 // Total damage team can take
    float ra_lasttime, ya_lasttime, ...;
} sort_teams_info_t;
```

**Global Arrays:**
```c
extern sort_players_info_t sorted_players_by_frags[MAX_CLIENTS];
extern sort_players_info_t sorted_players[MAX_CLIENTS];
extern sort_teams_info_t sorted_teams[MAX_CLIENTS];
extern int n_teams, n_players, n_spectators;
extern int active_player_position, active_team_position;
```

**Function:**
```c
void HUD_Sort_Scoreboard(int flags)
// Flags: HUD_SCOREBOARD_ALL, HUD_SCOREBOARD_SORT_TEAMS,
//        HUD_SCOREBOARD_SORT_PLAYERS, HUD_SCOREBOARD_UPDATE,
//        HUD_SCOREBOARD_AVG_PING
```

**Stack Calculation:**
```c
float SCR_HUD_TotalStrength(float health, float armorValue, float armorType)
// Returns total damage player can sustain

float SCR_HUD_ArmorType(int items)
// Returns armor absorption percentage:
// IT_INVULNERABILITY -> 0.99
// IT_ARMOR3 (RA) -> 0.8
// IT_ARMOR2 (YA) -> 0.6
// IT_ARMOR1 (GA) -> 0.3
```

---

## 9. DEVELOPER REFERENCE

### 9.1 Registering New HUD Elements

```c
hud_t *HUD_Register(
    char *name,              // Element name (used in cvars)
    char *var_alias,         // Alias name (can be NULL)
    char *description,       // Help text
    int flags,               // HUD_* flags
    cactive_t min_state,     // ca_disconnected/ca_connected/ca_active
    int draw_order,          // Initial z-order
    hud_func_type draw_func, // void (*draw_func)(hud_t *)
    char *show,              // Default show value
    char *place,             // Default placement
    char *align_x,           // Default X alignment
    char *align_y,           // Default Y alignment
    char *pos_x,             // Default X offset
    char *pos_y,             // Default Y offset
    char *frame,             // Default frame style
    char *frame_color,       // Default frame color
    char *item_opacity,      // Default opacity
    char *params, ...        // NULL-terminated param pairs
)
```

**Example:**
```c
HUD_Register(
    "health", NULL, "Part of your status - health level.",
    HUD_INVENTORY, ca_active, 0, SCR_HUD_DrawHealth,
    "1", "face", "after", "center", "0", "0", "0", "0 0 0", NULL,
    "style", "0",
    "scale", "1",
    "align", "right",
    "digits", "3",
    "proportional", "0",
    NULL
);
```

### 9.2 Drawing Function Template

```c
static void SCR_HUD_DrawMyElement(hud_t *hud)
{
    int x, y, width, height;

    // First-time cvar lookup (cached)
    static cvar_t *my_param = NULL;
    if (my_param == NULL) {
        my_param = HUD_FindVar(hud, "myparam");
    }

    // Calculate dimensions
    width = ...;
    height = ...;

    // Prepare to draw (handles positioning, frame, visibility)
    if (HUD_PrepareDraw(hud, width, height, &x, &y)) {
        // Draw your content at (x, y)
        Draw_String(x, y, "Hello!");
    }
}
```

### 9.3 Finding Elements/Cvars

```c
hud_t *HUD_Find(char *name);
cvar_t *HUD_FindVar(hud_t *hud, char *subvar);
cvar_t *HUD_FindInitTextColorVar(hud_t *hud, char *name);

// Global cvar lookup
cvar_t *Cvar_Find(char *name);
```

### 9.4 Common Patterns

**Caching Cvars:**
```c
static cvar_t *hud_foo_bar = NULL;
if (hud_foo_bar == NULL) {
    hud_foo_bar = HUD_FindVar(hud, "bar");
}
```

**Color Text Cvars:**
```c
cvar_t *color_var = HUD_FindInitTextColorVar(hud, "text_color");
// Auto-applies CVAR_COLOR flag and parses color names
```

**Drawing with Opacity:**
```c
Draw_SetOverallAlpha(hud->opacity->value);
// ... draw calls ...
Draw_SetOverallAlpha(1.0);
```

**Stat Access:**
```c
int value = HUD_Stats(STAT_HEALTH);  // Respects hud_planmode
// vs
int value = cl.stats[STAT_HEALTH];   // Direct access
```

---

## 10. FILE LOCATIONS SUMMARY

**Core HUD System:**
- `/home/quakeuser/ezquake-source/src/hud.h` (133 lines)
- `/home/quakeuser/ezquake-source/src/hud.c` (1647 lines)
- `/home/quakeuser/ezquake-source/src/hud_common.h` (107 lines)
- `/home/quakeuser/ezquake-source/src/hud_common.c` (1111 lines)
- `/home/quakeuser/ezquake-source/src/hud_editor.c`
- `/home/quakeuser/ezquake-source/src/r_hud.c`

**Individual Elements (25 files):**
- `src/hud_*.c` - See section 1.1 for complete list

**Tracking & Stats:**
- `src/vx_tracker.c` - Main tracker display
- `src/vx_tracker.h` - Tracker header
- `src/fragstats.c` - Frag statistics parsing
- `src/stats_grid.c` - Stats grid display

**Related Systems:**
- `src/sbar.c` - Status bar (classic HUD)
- `src/teamplay.c` - Teamplay mechanics
- `src/mvd_utils.c` - MVD utilities
- `src/mvd_autotrack.c` - MVD auto-tracking

---

## Additional Resources

**Resume Exploration:**
If you need to continue exploring the ezQuake HUD system or investigate specific features in more detail, you can resume the previous exploration session using agent ID: `a18523a`

**JSON Documentation:**
The ezQuake repository includes extensive cvar/command documentation:
- `/home/quakeuser/ezquake-source/help_variables.json` (22,935 lines)
- `/home/quakeuser/ezquake-source/help_commands.json` (2,105 lines)

These files contain additional metadata, descriptions, and groupings for all cvars and commands.
