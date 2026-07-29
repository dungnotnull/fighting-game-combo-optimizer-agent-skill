# Domain Knowledge Reference — Fighting-Game Combo & Frame-Data Optimization

> This document contains core domain concepts, terminology, and foundational knowledge for fighting game combo optimization and frame data analysis.

---

## Core Concepts

### Frame Data

Frame data is the technical measurement of move properties in fighting games, measured in frames (typically 60 frames = 1 second). Understanding frame data is essential for competitive play.

| Property | Description | Impact |
|----------|-------------|--------|
| **Startup** | Frames before a move becomes active/hitable | Determines how fast a move can punish |
| **Active** | Frames during which a move can hit | Determines how easy a move is to whiff punish |
| **Recovery** | Frames after active frames until full recovery | Determines vulnerability period |
| **Frame Advantage** | Net frames gained/lost on block or hit | Positive = your turn, Negative = opponent's turn |
| **Cancel Window** | Frames during which a move can be cancelled | Enables combo routes and pressure |
| **Link Window** | Frames to connect another move after hit | Determines combo difficulty |

### Combo Theory

A **combo** is a sequence of moves that an opponent cannot block between. Key concepts:

| Term | Definition |
|------|------------|
| **BnB (Bread and Butter)** | Reliable, practical combo used frequently |
| **Optimal Combo** | Maximum damage combo for a given situation |
| **Situational Combo** | Combo requiring specific conditions (corner, meter, etc.) |
| **Damage Scaling** | Damage reduction per hit in a combo |
| **Proration** | Initial damage reduction from starting moves |
| **Meter Management** | Strategic resource allocation for special moves |
| **Okizeme** | Wake-up offense/pressure after knockdown |
| **Conversion** | Turning a hit into a full combo |
| **Punish** | Attacking during opponent's recovery |
| **Whiff Punish** | Attacking a move that completely missed |

### Frame Advantage Calculation

```
Frame Advantage = (Blockstun/Hitstun) - (Recovery + Active)

Positive Advantage: You recover first (+ frames to act)
Negative Advantage: Opponent recovers first (they can punish)
Neutral: Both recover at same time
```

### Damage Scaling Formula

Most games use damage scaling that reduces damage as combo length increases:

```
Scaled Damage = Base Damage × Scaling Factor

Where Scaling Factor typically follows:
- Hit 1-3: 100% scaling
- Hit 4-6: 80% scaling
- Hit 7+: 50% scaling (varies by game)
```

### Punish Windows

**Punishability** depends on frame disadvantage:

| Disadvantage | Punish Type | Example |
|--------------|-------------|---------|
| -1 to -3 | Light punish only | Fast jab |
| -4 to -6 | Medium punish | Standing medium |
| -7 to -10 | Heavy punish | Crouching heavy, special move |
| -11+ | Any punish | Full combo, super |

---

## Game-Specific Terminology

### Universal Terms

| Term | Meaning |
|------|---------|
| **Meaty** | Timing a move's active frames to hit as opponent wakes up |
| **Safe Jump** | Jump attack that allows safe landing vs reversals |
| **OS (Option Select)** | Input covering multiple options |
| **Reversal** | Instant move on wake-up (usually with invincibility) |
| **Cross-up** | Attack crossing up opponent's defense |
| **High/Low Mixup** | Unseeable high/low attack combination |
| **Throw Tech** | Breaking a throw attempt |
| **Throw Setup** | Situation where opponent must guess between throw/strike |
| **Pressure** | Offensive sequence limiting opponent's options |
| **Frame Trap** | Deliberate gap in blockstring to catch button presses |

### Meter Usage

**Meter** (or Super Meter, Tension, etc.) is a limited resource. Optimal usage:

1. **Damage vs Utility**: Spend for maximum damage OR save for utility (supers, DRC, etc.)
2. **Build vs Spend**: Some moves build meter; spending meter may prevent future use
3. **Okizeme Investment**: Spending meter for knockdown setups may be worth more than raw damage
4. **Comeback Factor**: Saving meter for clutch situations vs consistent spending

---

## Analytical Frameworks

### Combo Optimization Algorithm

```
1. Identify Starting Situation
   - Character vs Character
   - Starting normal/special
   - Counter hit (CH) or normal hit
   - Screen position (midscreen vs corner)
   - Available meter

2. Determine Constraints
   - Hit advantage (from frame data)
   - Cancel availability
   - Meter budget
   - Consistency vs optimization preference

3. Evaluate Combo Routes
   - Calculate total damage (with scaling)
   - Calculate meter cost/gain
   - Calculate ender knockdown properties
   - Assess execution difficulty

4. Select Optimal Route
   - If max damage needed: Choose highest damage route
   - If meter conservation: Choose efficient route
   - If consistency priority: Choose easiest execution
   - If okizeme priority: Choose best knockdown ender
```

### Punish Optimization

```
1. Identify Punish Window
   - Opponent move frame disadvantage
   - Available reaction time
   - Character spacing

2. Match to Punish
   - For -1 to -3 frames: Fast light (5f startup)
   - For -4 to -6 frames: Medium (7-8f startup)
   - For -7+ frames: Full combo conversion

3. Consider Spacing
   - Proximity required for chosen punish
   - Pushback from opponent's move
   - Need for dash-in punish
```

### Meter Economy Analysis

```
Meter Economy Calculation:

Total Value = (Damage Dealed × Damage Weight)
            + (Knockdown Value × Setup Weight)
            + (Meter Gained × Future Value Weight)

Where weights depend on:
- Match state (winning/losing vs close)
- Character archetype (zoner vs rushdown)
- Opponent's weaknesses
- Time remaining
```

---

## Decision Frameworks

### Risk/Reward Calculation

For any offensive option:

```
Risk/Reward Ratio = (Success Rate × Reward) / (Failure Rate × Risk)

Where:
- Success Rate: Execution consistency × opponent's defense capability
- Reward: Damage + okizeme + meter gained
- Risk: Punishment damage taken + position loss
```

### Scenario Planning

When choosing combos/routes, consider three scenarios:

| Scenario | Probability | Combo Choice |
|----------|-------------|--------------|
| **Best Case** | Counter hit, ideal spacing | Max damage combo |
| **Base Case** | Normal hit, standard spacing | BnB combo |
| **Worst Case** | Wrong spacing, dropped input | Safe combo/blockstring |

---

## Execution Difficulty

### Difficulty Factors

| Factor | Impact | Mitigation |
|--------|--------|------------|
| **Timing Windows** | Tight links (1-2f) are hard | Practice, plinking, macros |
| **Input Complexity** | Complex motions (360, 720) | Simplify routes |
| **Character Knowledge** | Spacing awareness | Match experience |
| **Fatigue** | Performance drops over time | Use simpler combos later |

### Consistency vs Optimization Tradeoff

```
Consistency Score = (Success Rate in Practice) × (Stress Factor)

Where Stress Factor accounts for:
- Tournament pressure (0.5x)
- Casual match (1.0x)
- Practice mode (1.5x)
```

**Rule of thumb**: Use the simplest combo that achieves your strategic goal.

---

## Evidence Sources

### Authoritative Frame Data Sources

| Source | Coverage | Update Frequency |
|--------|----------|------------------|
| **Dustloop** | Anime games | Regular |
| **Mizuumi** | French Bread games | Regular |
| **FatOnline** | Multiple games | Regular |
| **SuperCombo Wiki** | Community crowdsourced | Community updates |
| **Game-Specific Discords** | Real-time optimization | Continuous |

### Academic Research

While fighting game research is limited, relevant domains include:

- **Game Design Theory**: Balance and frame data impact
- **Human-Computer Interaction**: Input methods and timing
- **Cognitive Science**: Decision-making under time pressure
- **Sports Psychology**: Competitive performance and stress

---

## Common Pitfalls

### Mental Errors

1. **Auto-piloting**: Doing combos without considering situation
2. **Over-optimizing**: Choosing max damage when safe damage wins
3. **Ignoring meter**: Spending without consideration of future needs
4. **Tunnel vision**: Focusing on combos without neutral awareness
5. **Risk mismanagement**: Taking unnecessary risks when ahead

### Technical Errors

1. **Not knowing frame data**: Guessing instead of knowing
2. **Inconsistent combos**: Optimal on paper, inconsistent in practice
3. **Poor meter usage**: Wasting resources on suboptimal conversions
4. **Wrong punish choice**: Choosing heavy punish when light is guaranteed
5. **Spacing ignorance**: Attempting combos without proper positioning

---

## Reference Material

### Quick Reference Formulas

```
1. Frame Advantage = Hitstun/Blockstun - (Recovery + Active)
2. Punish Window Required = Move Startup + Reaction Time
3. Damage with Scaling = Base Damage × (Scaling Factor)^Hit Number
4. Meter Efficiency = (Damage + Utility) / Meter Cost
```

### Glossary

- **BNB**: Bread and Butter (reliable combo)
- **CH**: Counter Hit (hit during opponent's startup)
- **FC**: Fat Cancel (special cancel mechanism)
- **KD**: Knockdown
- **OS**: Option Select
- **Oki**: Okizeme (wake-up offense)
- **RC**: Roman Cancel (system mechanic)
- **TH**: Throw Hitbox
- **WH**: Whiff (move that missed completely)

---

*This document is a living reference. Update as new techniques and understanding emerge.*
