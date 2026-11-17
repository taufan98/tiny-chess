# Tiny Chess — build notes

## Entry
- `main.py` — packed entry, **3,799 bytes** (cap 4,096), from
  `makefun compress source.py --out main.py` (sha256 28d45bad…).
- `source.py` — readable source, NOT committed; sent with the bundle
  via `--compress-source main.py=source.py`.
- Snapshot under the 8,192-byte cap, no file over 4,096. MIT license.
  Engine is original code (no sunfish/GPL code).

## Design
- 0x88 board, bytearray; full legal moves (castling, en passant,
  promotions); checkmate/stalemate detection.
- Negamax + alpha-beta, iterative deepening to a FIXED 100,000-node
  budget/move (deterministic, never a clock). Transposition table,
  killers, history, null-move pruning (R=2), check extension,
  late-move reductions, futility pruning, quiescence (captures,
  promotions, check replies).
- Eval: material P100 N320 B330 R500 Q900 + Michniewski PSTs +
  bishop pair +30 + passed-pawn bonus. ~27-37k nps; worst move
  ~3.5 s — under the 10,000 ms limit.

## Tests
- Perft (18 checks incl. startpos, Kiwipete, POS3/4/5): all pass.
- Mate-in-1, back-rank mate, stalemate/mated root None, board
  integrity, passed-pawn test (3,000 random sets), self-play vs
  greedy 6/6 — all pass.
- Practice trials (packed main.py, 6-game gauntlet): v2 mean Elo
  1219; **v3 mean Elo 1306 (1364/1191/1364)**. No time losses.
- WARNING: v3 at 150k nodes scored Elo 997 with 4 games lost by
  time (moves 12-22 s). 150k is UNSAFE; do not raise the budget.
- Real trials play 8 games (practice has 6): nodes-1M/2M are added
  in grading and will likely be losses.
