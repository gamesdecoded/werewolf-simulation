"""
Werewolf role-value tournament engine — humandecoded video #8.

Approved design (2026-10-27, Decoder options tap):
  Setup identical in every arm: 12 players, 2 werewolves.
  A Neither:  2 wolves + 10 plain villagers
  B Seer only: 2 wolves + 1 seer + 9 plain
  C Doctor only: 2 wolves + 1 doctor + 9 plain
  D Both: 2 wolves + 1 seer + 1 doctor + 8 plain

Cycle: night first, then day, repeat.
Night, in this order (order matters, and is fixed):
  1. Doctor chooses a protection. Random alive player, except a
     REVEALED seer is protected if alive. The doctor may protect
     anyone alive including self, but not the same player two
     nights in a row.
  2. Wolves choose a kill target. Random alive non-wolf, except a
     REVEALED seer is targeted first. If the target is protected,
     the kill is blocked and nobody dies that night.
  3. If the seer is alive after the kill, the seer checks one
     alive non-seer player, preferring players not checked before.
     The seer learns wolf-or-not for that player only.
     A seer killed that night gets no check that night.
Day:
  - If the seer is alive and found a wolf on the previous night,
    the seer reveals and villagers lynch that wolf. The seer is
    revealed permanently from that point on.
  - Otherwise the day lynch is random among alive players, with
    one exception: a REVEALED seer is a known villager, so villagers
    never randomly lynch a revealed seer. An UNREVEALED seer or
    doctor can still be lynched by mistake.
Win: villagers win when both wolves are dead; wolves win at
parity (wolves >= living non-wolves), checked after night and
after day.

NO-PEEK RULES (checked by construction, not by trust):
  - Wolves never choose a target from hidden role knowledge, except
    the revealed-seer rule, which is public information.
  - Doctor never chooses from the hidden kill target, except the
    revealed-seer rule, which is public information.
  - Seer never chooses a check target from hidden role knowledge:
    the target is random (un-checked first), and wolf-or-not is
    learned only AFTER the pick.
  - Random day lynch never excludes hidden wolves or hidden
    villagers; it excludes only the revealed seer, public info.
  - No bot sees another player's hand/role, argues, bluffs, or
    persuades. This is a voting/night-mechanics sim, not deception.
"""
import argparse
import json
import math
import random
import time

ARMS = {
    "A_neither": {"seer": False, "doctor": False},
    "B_seer_only": {"seer": True, "doctor": False},
    "C_doctor_only": {"seer": False, "doctor": True},
    "D_both": {"seer": True, "doctor": True},
    # v3 Perfect Doctor arms (2026-10-29, NOT part of the original approved design):
    # E/F = perfect aim while alive: if the doctor is alive, the kill target is
    #   blocked that night (doctor knows the target); if the doctor is dead,
    #   night kills resume normally.
    # G/H = unconditional cheat: the nightly kill is blocked every night by
    #   fiat, regardless of whether the doctor token is still alive. This is
    #   the model whose exact DP value is 2/3 for the doctor-alone arm.
    "E_perfect_doctor_only": {"seer": False, "doctor": True, "perfect": "aim"},
    "F_seer_perfect_doctor": {"seer": True, "doctor": True, "perfect": "aim"},
    "G_perfect_doctor_cheat": {"seer": False, "doctor": True, "perfect": "cheat"},
    "H_seer_perfect_doctor_cheat": {"seer": True, "doctor": True, "perfect": "cheat"},
}

# role codes
VILLAGER = 0
WOLF = 1
SEER = 2
DOCTOR = 3


def play_one_game(rng, has_seer, has_doctor, perfect=None):
    # Build roles: 2 wolves, optional seer/doctor, rest villagers. 12 total.
    roles = [WOLF, WOLF]
    if has_seer:
        roles.append(SEER)
    if has_doctor:
        roles.append(DOCTOR)
    while len(roles) < 12:
        roles.append(VILLAGER)
    rng.shuffle(roles)

    alive = [True] * 12
    wolves_alive = 2
    nonwolves_alive = 10
    seer_id = roles.index(SEER) if has_seer else -1
    doctor_id = roles.index(DOCTOR) if has_doctor else -1

    checked = set()          # players the seer has checked (seer's own knowledge)
    found_wolf = -1          # wolf found last night, awaiting day reveal
    revealed = False         # seer has revealed at least once (public)
    last_protected = -1
    doctor_blocks = 0
    seer_found_wolf = False
    wolves_found_by_seer = 0  # diagnostic only: how many distinct wolves the seer checked
    rounds = 0
    nights_doctor_alive = 0
    nights_total = 0

    def alive_ids():
        return [i for i in range(12) if alive[i]]

    def kill(pid):
        nonlocal wolves_alive, nonwolves_alive
        alive[pid] = False
        if roles[pid] == WOLF:
            wolves_alive -= 1
        else:
            nonwolves_alive -= 1

    for _ in range(100):  # hard cap; real games end in a handful of rounds
        # ---- NIGHT ----
        rounds += 1
        living = alive_ids()

        # 1. Doctor protection (public-info rules only)
        protected = -1
        if has_doctor and alive[doctor_id]:
            nights_doctor_alive += 1
            if revealed and alive[seer_id] and seer_id != last_protected:
                protected = seer_id
            else:
                eligible = [p for p in living if p != last_protected]
                if not eligible:
                    eligible = living
                protected = rng.choice(eligible)
            last_protected = protected
        else:
            last_protected = -1

        # 2. Wolf kill (public-info rules only)
        if revealed and alive[seer_id]:
            target = seer_id
        else:
            nonwolf_living = [p for p in living if roles[p] != WOLF]
            target = rng.choice(nonwolf_living)
        nights_total += 1
        if perfect == "cheat":
            # Unconditional cheat: kill blocked every night by fiat.
            doctor_blocks += 1
        elif perfect == "aim" and has_doctor and alive[doctor_id]:
            # Perfect aim while alive: doctor knows the target and blocks it.
            doctor_blocks += 1
        elif target != protected:
            kill(target)
        else:
            doctor_blocks += 1

        # Win check after night
        if wolves_alive == 0:
            return True, rounds, seer_found_wolf, revealed, doctor_blocks, wolves_found_by_seer, nights_total, nights_doctor_alive
        if wolves_alive >= nonwolves_alive:
            return False, rounds, seer_found_wolf, revealed, doctor_blocks, wolves_found_by_seer, nights_total, nights_doctor_alive

        # 3. Seer check, only if alive after the kill
        if has_seer and alive[seer_id]:
            candidates = [p for p in alive_ids() if p != seer_id and p not in checked]
            if not candidates:
                candidates = [p for p in alive_ids() if p != seer_id]
            target_check = rng.choice(candidates)
            checked.add(target_check)
            if roles[target_check] == WOLF:
                found_wolf = target_check
                seer_found_wolf = True
                wolves_found_by_seer += 1

        # ---- DAY ----
        living = alive_ids()
        if has_seer and alive[seer_id] and found_wolf != -1 and alive[found_wolf]:
            lynch = found_wolf
            revealed = True
            found_wolf = -1
        else:
            # Random lynch; revealed seer is known villager, never lynched.
            candidates = [p for p in living if not (revealed and p == seer_id)]
            if not candidates:
                candidates = living
            lynch = rng.choice(candidates)
        kill(lynch)

        if wolves_alive == 0:
            return True, rounds, seer_found_wolf, revealed, doctor_blocks, wolves_found_by_seer, nights_total, nights_doctor_alive
        if wolves_alive >= nonwolves_alive:
            return False, rounds, seer_found_wolf, revealed, doctor_blocks, wolves_found_by_seer, nights_total, nights_doctor_alive

    # Capped game (should be 0): count as wolf win is NOT used; caller counts it.
    return None, rounds, seer_found_wolf, revealed, doctor_blocks, wolves_found_by_seer, nights_total, nights_doctor_alive


def run_arm(arm, n, seed):
    cfg = ARMS[arm]
    rng = random.Random(seed)
    villager_wins = 0
    capped = 0
    total_rounds = 0
    seer_found_games = 0
    seer_revealed_games = 0
    seer_found_both_games = 0
    wolves_found_total = 0
    doctor_block_games = 0
    doctor_blocks_total = 0
    nights_total_sum = 0
    nights_doctor_alive_sum = 0
    for _ in range(n):
        win, rounds, found, revealed, blocks, wolves_found, nt, nda = play_one_game(
            rng, cfg["seer"], cfg["doctor"], perfect=cfg.get("perfect")
        )
        total_rounds += rounds
        nights_total_sum += nt
        nights_doctor_alive_sum += nda
        wolves_found_total += wolves_found
        if wolves_found >= 2:
            seer_found_both_games += 1
        if found:
            seer_found_games += 1
        if revealed:
            seer_revealed_games += 1
        if blocks > 0:
            doctor_block_games += 1
        doctor_blocks_total += blocks
        if win is None:
            capped += 1
        elif win:
            villager_wins += 1
    p = villager_wins / n if n else 0.0
    se = math.sqrt(p * (1 - p) / n) if n else 0.0
    return {
        "arm": arm,
        "seer": cfg["seer"],
        "doctor": cfg["doctor"],
        "games": n,
        "villager_wins": villager_wins,
        "villager_win_rate": p,
        "ci95_low": max(0.0, p - 1.96 * se),
        "ci95_high": min(1.0, p + 1.96 * se),
        "ci95_halfwidth": 1.96 * se,
        "mean_rounds": total_rounds / n if n else 0.0,
        "capped_games": capped,
        "seer_found_wolf_games": seer_found_games,
        "seer_found_wolf_rate": seer_found_games / n if n else 0.0,
        "seer_found_both_wolves_games": seer_found_both_games,
        "seer_found_both_wolves_rate": seer_found_both_games / n if n else 0.0,
        "wolves_found_by_seer_per_game": wolves_found_total / n if n else 0.0,
        "seer_revealed_games": seer_revealed_games,
        "doctor_block_games": doctor_block_games,
        "doctor_block_game_rate": doctor_block_games / n if n else 0.0,
        "doctor_blocks_total": doctor_blocks_total,
        "doctor_blocks_per_game": doctor_blocks_total / n if n else 0.0,
        "nights_total": nights_total_sum,
        "nights_doctor_alive": nights_doctor_alive_sum,
        "doctor_blocks_per_night": doctor_blocks_total / nights_total_sum if nights_total_sum else 0.0,
        "doctor_blocks_per_night_doctor_alive": doctor_blocks_total / nights_doctor_alive_sum if nights_doctor_alive_sum else 0.0,
        "perfect": cfg.get("perfect"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261027)
    ap.add_argument("--arms", default=",".join(ARMS.keys()))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    t0 = time.time()
    results = []
    for i, arm in enumerate(args.arms.split(",")):
        arm = arm.strip()
        r = run_arm(arm, args.games, args.seed + 1000 * i)
        results.append(r)
        print(
            f"{arm}: villager {r['villager_win_rate']*100:.2f}% "
            f"[{r['ci95_low']*100:.2f}, {r['ci95_high']*100:.2f}] "
            f"mean_rounds={r['mean_rounds']:.2f} capped={r['capped_games']} "
            f"seer_found={r['seer_found_wolf_rate']*100:.1f}% "
            f"doctor_block_games={r['doctor_block_game_rate']*100:.1f}%",
            flush=True,
        )
    payload = {
        "config": {
            "players": 12,
            "wolves": 2,
            "seed": args.seed,
            "games_per_arm": args.games,
            "arms": list(ARMS.keys()),
        },
        "elapsed_seconds": time.time() - t0,
        "results": results,
    }
    if args.out:
        with open(args.out, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Wrote {args.out}")
    return payload


if __name__ == "__main__":
    main()
