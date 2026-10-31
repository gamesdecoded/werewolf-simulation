Werewolf role-value tournament — methods (video #8)

Question: Which special role actually saves the village — seer, doctor,
both, or neither? Same setup played four ways.

Setup (approved 2026-10-27): 12 players, 2 werewolves in every arm.
  A Neither:  2 wolves + 10 plain villagers
  B Seer only: 2 wolves + 1 seer + 9 plain
  C Doctor only: 2 wolves + 1 doctor + 9 plain
  D Both: 2 wolves + 1 seer + 1 doctor + 8 plain

Cycle: night first, then day, repeat.
Night order: (1) doctor protects — random alive player, except a
revealed seer is protected if alive; no same player two nights in a
row; (2) wolves kill — random alive non-wolf, except a revealed seer
is targeted first; a protected target means no death that night;
(3) seer checks, only if alive after the kill — random alive non-seer,
un-checked players first, learns wolf-or-not for that player only.
Day: if the seer is alive and found a wolf last night, the seer
reveals and villagers lynch that wolf (seer revealed permanently).
Otherwise the day lynch is random among alive players, except a
revealed seer — a known villager — is never randomly lynched.
An unrevealed seer or doctor can be lynched by mistake.
Win: villagers win when both wolves are dead; wolves win at parity
(wolves >= living non-wolves), checked after night and after day.

Limits (for the video, same as the bots-are-not-humans caveat):
bots vote and kill by rules — they do not argue, bluff, or persuade.
This simulates voting and night mechanics, not deception.

No-peek: wolves and doctor use only public information (revealed
seer) plus random choice; the seer picks a check target randomly
and learns wolf-or-not only after the pick. No bot sees a hidden role.

Run: 1,000,000 games per arm, 4,000,000 total, seed 20261027
(arm seeds seed + 1000*arm_index), engine.py, 88.8 seconds.
Capped games: 0 in every arm. 95% CIs are normal approximations
(half-width about 0.09–0.10 percentage points at this size);
all four arms' CIs are non-overlapping.

Results (villager win rate):
  A Neither:  35.16% [35.06, 35.25], mean 4.47 rounds
  B Seer only: 50.29% [50.19, 50.38], mean 4.37 rounds,
               seer finds a wolf in 51.61% of games, both wolves 0.00%
  C Doctor only: 34.04% [33.95, 34.13], mean 4.71 rounds,
               doctor blocks a kill in 29.82% of games
  D Both: 51.34% [51.24, 51.44], mean 4.57 rounds,
               seer finds a wolf in 52.76% of games, both wolves 4.12%,
               doctor blocks a kill in 45.78% of games

Differences: seer alone +15.13 points over neither; doctor alone
-1.12 points versus neither; both +1.05 points over seer alone,
+16.18 over neither.

Mechanism note (from the diagnostics, not a separate claim):
in B the seer finds both wolves in 0.00% of games — by construction
the seer is the wolves' first target the night after revealing,
with no doctor to block it, so there is no second check. In D the
doctor lets the seer survive to a second check in 4.12% of games,
which is where D's small edge over B comes from.

---

PERFECT DOCTOR RUNS (script v3, 2026-10-29)
Engine extended in engine.py (original A-D arms unchanged):
  E Perfect aim while alive, doctor only
  F Perfect aim while alive, seer + doctor
  G Unconditional cheat, doctor only (kill blocked every night by fiat)
  H Unconditional cheat, seer + doctor
1,000,000 games each, seed 20261027 (arm offsets as in engine.py), 0 capped.
  E Perfect aim alone: 48.11% [48.02, 48.21], mean 6.93 rounds
  F Seer + perfect aim: 74.91% [74.83, 75.00], mean 5.59 rounds,
    seer finds a wolf 67.29% of games, both wolves 22.67%
  G Cheat alone: 66.63% [66.54, 66.72], mean 8.00 rounds
    Exact DP value 2/3 = 66.67% lies inside the sim CI.
  H Seer + cheat: 91.96% [91.91, 92.01], mean 5.82 rounds,
    seer finds a wolf 71.40% of games, both wolves 38.06%
Ranking with cheat arms (sim rounded): doctor 34.0, no help 35.2,
seer 50.3, both 51.3, perfect doctor 66.6 (exact 66.7), seer+perfect 92.0.
Aim-while-alive arms are NOT the script's cheat numbers: a doctor who
must survive to protect dies by day vote in many games, hence
48.11% / 74.91% versus cheat 66.63% / 91.96%.

DOCTOR-ONLY BLOCK RATE PER NIGHT (200,000-game logging run, C arm)
  Win 34.12% [33.91, 34.32], mean 4.71 rounds, blocks in 29.77% of games,
  blocks per game 0.3804, blocks per night (all nights) 8.08%,
  blocks per night while doctor alive 11.85%.
  Original production derivation agrees: 0.3814 blocks/game /
  4.708 rounds = 8.10% per night.
  The 8.08% all-nights rate is inside the 5-10% range cited for the
  simple exact model; the doctor-alive rate (11.85%) is not, so the
  exact-model line must state which definition it uses.

EXACT-MATH BASELINE CHECK (DP, independent of the sim)
  State (wolves, villagers) at night start; night kill first, then
  uniform day vote among all living; wolves win at wolves >= villagers.
  DP gives exactly 244/693 = 35.209235%, matching script v3's proof card.
  Sim baseline 35.16% [35.06, 35.25] is consistent with it.
  Rules check: sim matches all three assumptions for the baseline arm
  (night first, uniform day vote with no seer to exclude, >= parity
  checked after night and after day). The proof checks code against
  rules, not against real tables, as script v3 states.
