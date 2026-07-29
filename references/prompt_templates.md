# Prompt Templates Reference — Fighting-Game Combo & Frame-Data Optimization

> This document contains reusable prompt templates and patterns for fighting game analysis, combo optimization, and frame data evaluation.

---

## Template Structure

Each template includes:
- **Purpose**: When to use this template
- **Input Variables**: What information needs to be provided
- **Output Format**: Expected structure of the response
- **Example**: Sample filled-in template

---

## Core Analysis Templates

### Template 1: Frame Data Analysis

**Purpose**: Analyze frame data properties for a specific move and determine optimal punishes and usage.

**Input Variables**:
- `game`: Fighting game title
- `character`: Character name
- `move`: Specific move or normal to analyze
- `situation`: Hit/block/whiff scenario
- `opponent_character`: Opponent's character (for matchup context)

**Template**:
```
Analyze the frame data for {move} for {character} in {game}.

Situation: {situation}
Opponent: {opponent_character}

Please provide:
1. Frame data breakdown (startup, active, recovery, total)
2. Frame advantage on block and hit
3. Frame advantage on counter hit (if different)
4. Safe/unsafe status against common punishes
5. Best punish options for opponent if blocked
6. Best conversion routes if it hits
7. Optimal spacing requirements
8. Risk/reward assessment

Include specific frame counts and cite sources where possible.
```

**Output Format**:
```markdown
## Frame Data: {move} ({character} - {game})

### Properties
| Property | Frames | Notes |
|----------|--------|-------|
| Startup | X | First active frame |
| Active | X | Hitbox duration |
| Recovery | X | Vulnerable frames |
| Total | X | Sum of all phases |

### Frame Advantage
- **On Block**: ±X frames
- **On Hit**: ±X frames
- **On Counter Hit**: ±X frames (if applicable)

### Punish Game
- **If Blocked**: [Punish options with frame requirements]
- **If It Hits**: [Conversion routes with damage]

### Assessment
- **Safety**: [Safe/Unsafe/Punishable by X]
- **Usage**: [When to use this move optimally]
- **Sources**: [Citations]
```

---

### Template 2: Combo Optimization

**Purpose**: Generate optimal combo routes for a specific situation.

**Input Variables**:
- `game`: Fighting game title
- `character`: Character name
- `starting_move`: Initial move that connects
- `hit_type`: Normal hit, counter hit, or crouching hit
- `screen_position`: Midscreen, corner, or specific positioning
- `meter_available`: Current meter amount
- `optimization_goal`: Damage, meter efficiency, okizeme, or consistency

**Template**:
```
Generate optimal combo routes for {character} in {game}.

Starting Condition:
- Starting move: {starting_move}
- Hit type: {hit_type}
- Screen position: {screen_position}
- Meter available: {meter_available}
- Optimization goal: {optimization_goal}

Please provide:
1. Best combo route for the optimization goal
2. Alternative routes for different priorities
3. Total damage for each route (with scaling applied)
4. Meter cost/gain for each route
5. Knockdown properties and okizeme potential
6. Execution difficulty rating
7. Consistency considerations
8. Risk assessment (whiff punish risk if dropped)

Include specific inputs and frame timing where applicable.
```

**Output Format**:
```markdown
## Optimal Combo Routes: {character} ({game})

### Starting Situation
- **Move**: {starting_move} on {hit_type}
- **Position**: {screen_position}
- **Meter**: {meter_available}
- **Goal**: {optimization_goal}

### Recommended Route ({optimization_goal})
**Inputs**: [Input notation]
**Damage**: [X damage]
**Meter**: [±X meter]
**Knockdown**: [Yes/No, type]
**Difficulty**: [Easy/Medium/Hard]
**Consistency**: [% estimate]

### Alternative Routes
| Priority | Route | Damage | Meter | Difficulty |
|----------|-------|--------|-------|------------|
| [Goal 2] | [Inputs] | [X] | [±X] | [Rating] |
| [Goal 3] | [Inputs] | [X] | [±X] | [Rating] |

### Risk Assessment
- **Whiff Punish Risk**: [Risk level if dropped]
- **Spacing Requirements**: [Positioning needs]
- **Meter Economy**: [Efficiency rating]

### Sources
[Frame data and combo references]
```

---

### Template 3: Punish Optimization

**Purpose**: Determine optimal punishes for specific frame disadvantage situations.

**Input Variables**:
- `game`: Fighting game title
- `character`: Character doing the punishing
- `opponent_move`: Opponent's move to punish
- `frame_disadvantage`: How many frames opponent is at disadvantage
- `spacing`: Current spacing between characters
- `meter_available`: Meter for punish usage

**Template**:
```
Calculate optimal punishes for {character} in {game}.

Punish Situation:
- Opponent move: {opponent_move}
- Frame disadvantage: {frame_disadvantage} frames
- Spacing: {spacing}
- Meter available: {meter_available}

Please provide:
1. Guaranteed punishes (most consistent)
2. Optimal damage punishes (if spacing allows)
3. Metered punish options (with ROI analysis)
4. Whiff punish scenarios (if opponent completely misses)
5. Block punish vs hit punish differences
6. Risk assessment for each punish option

Include specific startup requirements and timing windows.
```

**Output Format**:
```markdown
## Punish Analysis: {character} vs {opponent_move} ({game})

### Punish Window
- **Frame Disadvantage**: {frame_disadvantage} frames
- **Usable Startup**: Up to {X} frame moves
- **Spacing Factor**: {spacing effect}

### Guaranteed Punishes (Most Consistent)
| Punish | Startup | Damage | Meter | Notes |
|--------|---------|--------|-------|-------|
| [Option 1] | [Xf] | [X] | [±X] | [Details] |
| [Option 2] | [Xf] | [X] | [±X] | [Details] |

### Optimal Damage Punishes
| Punish | Inputs | Total Damage | Meter | Difficulty |
|--------|--------|--------------|-------|------------|
| [Option 1] | [Inputs] | [X] | [±X] | [Rating] |
| [Option 2] | [Inputs] | [X] | [±X] | [Rating] |

### Whiff Punish Options
If opponent completely misses the move:
[More damaging whiff punish options]

### Risk Assessment
- **Tightest Window**: [X frames for [option]]
- **Spacing Sensitivity**: [How much spacing matters]
- **Risk if Dropped**: [Punishment risk]
```

---

### Template 4: Meter Economy Analysis

**Purpose**: Analyze optimal meter usage strategies for specific game situations.

**Input Variables**:
- `game`: Fighting game title
- `character`: Character name
- `current_meter`: Current meter amount
- `max_meter`: Maximum meter capacity
- `match_state`: Winning, losing, or close game
- `round_format`: First to X rounds or best of Y

**Template**:
```
Analyze meter economy for {character} in {game}.

Current Situation:
- Current meter: {current_meter}/{max_meter}
- Match state: {match_state}
- Round format: {round_format}

Please provide:
1. Optimal meter usage strategy for this situation
2. Meter efficiency analysis (damage per meter spent)
3. When to save vs spend meter
4. Comeback factor considerations
5. Build vs spend analysis for key moves
6. Opportunity cost of spending now vs saving
7. Risk-adjusted recommendations

Include specific meter costs and expected returns for each option.
```

**Output Format**:
```markdown
## Meter Economy Analysis: {character} ({game})

### Current Situation
- **Meter**: {current_meter}/{max_meter}
- **Match State**: {match_state}
- **Round Format**: {round_format}

### Strategy Recommendations
| Situation | Spend | Save | Reasoning |
|-----------|-------|------|-----------|
| [Scenario 1] | [Amount] | [Amount] | [Why] |
| [Scenario 2] | [Amount] | [Amount] | [Why] |

### Meter Efficiency
| Usage | Cost | Expected Return | Efficiency |
|-------|------|-----------------|------------|
| [Option 1] | [X meter] | [Damage/Utility] | [Per meter] |
| [Option 2] | [X meter] | [Damage/Utility] | [Per meter] |

### Key Factors
- **Build Opportunities**: [Which moves build meter efficiently]
- **Spending Thresholds**: [When to definitely spend]
- **Comeback Factor**: [How being behind affects strategy]
- **Opportunity Cost**: [What you lose by spending now]

### Sources
[Meter data and community consensus]
```

---

### Template 5: Okizeme (Wake-up Offense)

**Purpose**: Design optimal wake-up offense sequences after knockdown.

**Input Variables**:
- `game`: Fighting game title
- `character`: Character applying pressure
- `opponent_character`: Character waking up
- `knockdown_type': Hard knockdown, soft knockdown, or techable
- `meter_available`: Meter for okizeme setup
- `wake_up_timing': Quick wake-up or delayed wake-up if applicable

**Template**:
```
Design okizeme setup for {character} vs {opponent_character} in {game}.

Knockdown Situation:
- Knockdown type: {knockdown_type}
- Meter available: {meter_available}
- Wake-up timing: {wake_up_timing}

Please provide:
1. Meaty timing setup (which moves and when to time them)
2. Safe jump setup (if applicable)
3. Mixup options (high/low/throw/grab)
4. Option Select coverage
5. Risk assessment for each option
6. Counter-play awareness (reversals, backdash, etc.)
7. Meter investment analysis for setups

Include specific timing windows and frame data.
```

**Output Format**:
```markdown
## Okizeme Setup: {character} vs {opponent_character} ({game})

### Knockdown Properties
- **Type**: {knockdown_type}
- **Wake-up Window**: [X frames of advantage]
- **Reversal Coverage**: [Which reversals are covered]

### Meaty Setup
- **Move**: [Move name]
- **Timing**: [Press X frames after knockdown]
- **Active Frames**: [Creates X frame meaty]
- **Coverage**: [Beats which options]

### Mixup Options
| Option | Input | Beats | Risk |
|--------|-------|-------|------|
| [Option 1] | [Input] | [Defensive options] | [Risk] |
| [Option 2] | [Input] | [Defensive options] | [Risk] |

### Option Selects
- **OS 1**: [What it covers, how to input]
- **OS 2**: [What it covers, how to input]

### Risk Assessment
- **Reversals**: [Which reversals beat this setup]
- **Backdash**: [Does this catch backdash?]
- **Cost**: [Meter investment, positioning]

### Sources
[Okizeme references and matchup data]
```

---

## Analysis Workflow Templates

### Template 6: Full Matchup Analysis

**Purpose**: Comprehensive matchup analysis covering neutral, offense, and defense.

**Input Variables**- `game`: Fighting game title
- `your_character`: Your character
- `opponent_character`: Opponent's character
- `analysis_focus': Neutral, offense, defense, or comprehensive

**Template**:
```
Provide comprehensive matchup analysis: {your_character} vs {opponent_character} in {game}.

Analysis Focus: {analysis_focus}

Please provide:
1. Character matchup summary (score and key dynamics)
2. Your character's advantages and how to leverage them
3. Your character's disadvantages and how to mitigate them
4. Key moves/tools to use in this matchup
5. Moves/tools to avoid or use carefully
6. Neutral game strategy (spacing, whiff punishing)
7. Offensive strategy (pressure routes, mixups)
8. Defensive strategy (defensive tools, anti-airs)
9. Key frame data interactions
10. Meter strategy for this matchup
11. Common pitfalls to avoid

Cite sources and provide specific frame data where relevant.
```

**Output Format**:
```markdown
## Matchup Analysis: {your_character} vs {opponent_character} ({game})

### Matchup Overview
- **Matchup Score**: [Estimated ratio]
- **Your Advantages**: [Key strengths]
- **Your Disadvantages**: [Key weaknesses]

### Key Tools
| Your Tool | Usage | Risk | Effectiveness |
|-----------|-------|-------|--------------|
| [Tool 1] | [When to use] | [Risk level] | [Rating] |
| [Tool 2] | [When to use] | [Risk level] | [Rating] |

### Neutral Strategy
[Spacing, whiff punish, approach strategy]

### Offensive Strategy
[Pressure routes, mixup options, conversion priorities]

### Defensive Strategy
[Defensive tools, anti-air coverage, escape options]

### Meter Strategy
[How to use meter specifically in this matchup]

### Key Interactions
[Specific frame data interactions that matter]

### Common Mistakes
[Mistakes to avoid and why]

### Sources
[Matchup guides and frame data references]
```

---

## Template Customization Guidelines

### Adding Variables

To add a new variable to a template:

1. Define the variable name using `{variable_name}` syntax
2. Add it to the Input Variables section with description
3. Include it in the template where relevant
4. Update the output format if the variable changes structure

### Template Selection Guide

| Analysis Goal | Use Template |
|---------------|--------------|
| Move properties and punishes | Template 1: Frame Data Analysis |
| Max damage combos | Template 2: Combo Optimization |
| Punishing specific moves | Template 3: Punish Optimization |
| Resource management | Template 4: Meter Economy Analysis |
| Wake-up offense | Template 5: Okizeme |
| Full matchup understanding | Template 6: Matchup Analysis |

### Chaining Templates

Templates can be combined for deeper analysis:

```
Frame Data Analysis (Template 1) → Combo Routes (Template 2) → Meter Economy (Template 4)
```

This chain analyzes a move, finds optimal conversions, and evaluates meter investment.

---

## Template Metadata

**Last Updated**: 2026-07-28
**Version**: 1.0.0
**Maintainer**: fighting-game-combo-optimizer skill

---

*This document is a living reference. Add new templates as patterns emerge.*
