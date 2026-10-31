# Werewolf Role Value Tournament — code and every number

Code and data behind the humandecoded video **"Does a Doctor Help the Village?"**
(Werewolf video #8). Six million games in total: one million per version.

## Headline results (villager win rate)

| Version | Villager win rate | 95% CI |
| --- | --- | --- |
| Doctor only (guessing) | 34.0% | [33.95, 34.13] |
| No help at all | 35.2% | [35.06, 35.25] |
| Seer only | 50.3% | [50.19, 50.38] |
| Seer + doctor | 51.3% | [51.24, 51.44] |
| Perfect doctor (cheat: kill blocked every night) | 66.7% exact (sim 66.63%) | sim [66.54, 66.72] |
| Seer + perfect doctor (cheat) | 92.0% (sim 91.96%) | sim [91.91, 92.01] |

Deltas: seer alone +15.13 points over no help; doctor alone −1.12 points
versus no help; both +1.05 points over seer alone.

Supporting numbers: seer finds a wolf in 51.61% of seer-only games and
never finds both wolves (0.00%) in that version — with no doctor, the
wolves kill the revealed seer before a second check. With a doctor, the
seer finds both wolves in 4.12% of games. The doctor blocks a kill in
29.82% of doctor-only games and in 45.78% of seer+doctor games.

## The setup

12 players, 2 werewolves in every arm. Night first, then day, repeat.
Night order: doctor protects → wolves kill → seer checks (only if the
seer is alive after the kill). The doctor protects randomly, except a
revealed seer is protected, and cannot protect the same player two
nights in a row. Wolves kill randomly, except a revealed seer is
targeted first. The seer checks one random un-checked player per night
and learns wolf-or-not only after picking. Day: if the seer found a
wolf and reveals, villagers lynch that wolf; otherwise the day lynch
is random among alive players, except a revealed seer is never randomly
lynched. Villagers win when both wolves are dead; wolves win at parity
(wolves >= living non-wolves), checked after night and after day.

Full rules, no-peek guarantees, and the perfect-doctor variants are in
`METHODS.md` and in the header of `engine.py`.

## Exact-math baseline check (independent of the simulation)

Pure math over every possible night and vote gives exactly
**244/693 = 35.209%** for the no-help arm. The simulation gives
35.16% [35.06, 35.25] — consistent. That check proves the code follows
the rules; it does not prove people play this way.

## Model limits — read before reusing these numbers

These are computer players, not people. They vote and kill by simple
rules: no arguing, no bluffing, no persuading, no remembering who voted
for whom. This is a test of voting and night mechanics, not a test of
deception. A smarter human seer, reading arguments and votes, might find
wolves faster than the random-checking bot seer here.

The "perfect doctor" in the video is a cheat, not a skill level: it
blocks the kill every single night by fiat (arms G/H in
`results_perfect.json`). The aim-while-alive perfect-doctor arms (E/F:
48.11% alone, 74.91% with seer) are also in that file but are NOT the
video's numbers — a doctor who must survive to protect dies by day vote
in many games. Real players land somewhere between the guessing doctor
and the cheat.

## Files

- `engine.py` — the simulation engine (original arms A–D plus the
  perfect-doctor arms E–H added for script v3).
- `METHODS.md` — full methods, limits, and diagnostics.
- `results.json` — arms A–D, 1,000,000 games each, seed 20261027.
- `results_perfect.json` — arms E–H, 1,000,000 games each, seed 20261027.
- `results_doctor_logging.json` — 200,000-game doctor-only logging run
  (block rate per night: 8.08% of all nights, 11.85% of nights while the
  doctor is alive).

## How to run

```bash
python3 engine.py --help
```

The engine writes per-arm results as JSON with win rates and 95%
confidence intervals. All 95% CIs are normal approximations (half-width
about 0.09–0.10 percentage points at one million games); the four main
arms' CIs are non-overlapping, and no game was capped in any arm.
