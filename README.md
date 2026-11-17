# tiny-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/taufan98/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/taufan98/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Tiny Chess is an original 0x88-board chess engine in one packed Python file (main.py, 3,799 bytes of the 4,096 cap), stdlib only. Negamax + alpha-beta, iterative deepening to a fixed 100,000-node budget per move, transposition table, killers, history, null-move pruning, check extensions, late-move reductions, futility pruning, quiescence. Eval: material + Michniewski piece-square tables + bishop-pair and passed-pawn bonuses. Practice trials: Elo 1364 / 1191 / 1364, mean 1306, above the 1,154 floor.

## Run it

```sh
python3 main.py
```

Runs as a chess engine driven by the harness (python3 -P -s main.py, Python 3.13). No install, no network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=va8excfs&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
