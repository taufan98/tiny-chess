# tiny-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/taufan98/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/taufan98/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Tiny Chess is an original 0x88-board chess engine in a single packed Python file (main.py, 3,799 bytes of the 4,096 cap), stdlib only. Search: negamax + alpha-beta, iterative deepening to a fixed 100,000-node budget per move (deterministic, no clock), transposition table, killer moves, history heuristic, null-move pruning, check extensions, late-move reductions, futility pruning, and quiescence over captures, promotions and check replies. Eval: material + Michniewski piece-square tables + bishop-pair and passed-pawn bonuses. Practice trials (6-game gauntlet): Elo 1364 / 1191 / 1364, mean 1306 — above the 1,154 practice floor. source.py is the readable source; main.py is the packed entry.

## Run it

```sh
python3 main.py
```

The program runs as a chess engine driven by the harness (python3 -P -s main.py on Python 3.13); no install step, no network needed.

---

<sub>Entered on [make.fun](https://make.fun/?ref=va8excfs&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
