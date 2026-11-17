# Tiny Chess — a 4 KB chess engine

Original 0x88-board chess engine in a single packed Python file
(`main.py`, 3,799 bytes). Stdlib only, no external chess library.

Search: negamax + alpha-beta, iterative deepening to a fixed
100,000-node budget per move (deterministic, no clock), transposition
table, killer moves, history heuristic, null-move pruning, check
extensions, late-move reductions, futility pruning, and a quiescence
search over captures, promotions and check replies.

Evaluation: material (P100 N320 B330 R500 Q900) + Michniewski
piece-square tables + bishop-pair bonus + passed-pawn bonus.

Practice trials (local env, 6-game gauntlet): Elo 1364 / 1191 / 1364,
mean 1306 — above the 1,154 practice floor, just under the ~1,365
house-baseline (sunfish-4k) mean. No time losses in any game.

`source.py` is the readable source; `main.py` is the packed entry
produced by `makefun compress source.py --out main.py`. The source is
sent with the bundle (`--compress-source main.py=source.py`) and is
not part of the committed snapshot.
