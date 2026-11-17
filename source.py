# dev copy of the tiny-chess engine (original code, written in-session)
# 0x88 board, bytearray, pieces stored +7 (empty=7, black 1..6, white 8..13)
import json, os, sys, urllib.request

V = (0, 100, 320, 330, 500, 900, 0)
KN = (-33, -31, -18, -14, 14, 18, 31, 33)
KI = (-17, -16, -15, -1, 1, 15, 16, 17)
BD = (-17, -15, 15, 17)
RD = (-16, -1, 1, 16)
QD = BD + RD
DIRS = {2: KN, 3: BD, 4: RD, 5: QD, 6: KI}
MATE = 100000
BUD = 40000  # node budget per move (fixed: deterministic, no clock)

# PSTs: classic tables, values /5 + 10 -> 'A'..'U', 32 chars each
# (files a-d, rank8 -> rank1; left-right symmetric, mirrored at lookup)
TS = ("KKKKUUUUMMOQLLMPKKKOLJIKLMMGKKKK",
      "ACEECGKKEKMNELNOEKNOELMNCGKLACEE",
      "GIIIIKKKIKLMILLMIKMMIMMMILKKGIII",
      "KKKKLMMMJKKKJKKKJKKKJKKKJKKKKKKL",
      "GIIJIKKKIKLLJKLLKKLLILLLIKLKGIIJ",
      "ECCAECCAECCAECCAGEECIGGGOOKKOQMK")
T = [[(ord(c) - 75) * 5 for c in s] for s in TS]

B = bytearray(128)
W = True   # side to move: True=white
C = 0      # castling rights: 1=K 2=Q 4=k 8=q
EP = -1    # en passant target square or -1
KW = 4
KB = 116
N = 0      # nodes searched this move
TT = {}
KIL = [0] * 256

def sqname(s):
    return "abcdefgh"[s & 7] + str((s >> 4) + 1)

def uci(m):
    s = sqname(m & 127) + sqname((m >> 7) & 127)
    q = (m >> 14) & 7
    return s + ("nbrq"[q - 2] if q else "")

def parse_fen(fen):
    global W, C, EP, KW, KB
    parts = fen.split()
    B[:] = bytes(128)
    for i in range(128):
        B[i] = 7
    r = 7
    f = 0
    for ch in parts[0]:
        if ch == "/":
            r -= 1
            f = 0
        elif ch.isdigit():
            f += int(ch)
        else:
            s = r * 16 + f
            p = "PNBRQK".index(ch.upper()) + 1
            B[s] = p + 7 if ch.isupper() else 7 - p
            if p == 6:
                if ch.isupper():
                    KW = s
                else:
                    KB = s
            f += 1
    W = parts[1] == "w"
    C = 0
    if len(parts) > 2:
        if "K" in parts[2]:
            C |= 1
        if "Q" in parts[2]:
            C |= 2
        if "k" in parts[2]:
            C |= 4
        if "q" in parts[2]:
            C |= 8
    EP = -1
    if len(parts) > 3 and parts[3] != "-":
        EP = "abcdefgh".index(parts[3][0]) + (int(parts[3][1]) - 1) * 16

def atk(s, by_white):
    # pawns
    for d in ((-15, -17) if by_white else (15, 17)):
        t = s + d
        if not t & 136 and B[t] == (8 if by_white else 6):
            return 1
    for d in KN:
        t = s + d
        if not t & 136 and B[t] == (9 if by_white else 5):
            return 1
    for d in KI:
        t = s + d
        if not t & 136 and B[t] == (13 if by_white else 1):
            return 1
    for d in BD:
        t = s + d
        while not t & 136:
            p = B[t]
            if p != 7:
                if p == (10 if by_white else 4) or p == (12 if by_white else 2):
                    return 1
                break
            t += d
    for d in RD:
        t = s + d
        while not t & 136:
            p = B[t]
            if p != 7:
                if p == (11 if by_white else 3) or p == (12 if by_white else 2):
                    return 1
                break
            t += d
    return 0

def gen(caponly):
    ms = []
    for s in range(128):
        if s & 136:
            continue
        v = B[s]
        if v == 7 or (v > 7) != W:
            continue
        p = v - 7 if v > 7 else v - 7  # signed piece
        a = abs(p)
        if a == 1:
            d = 16 if W else -16
            t = s + d
            if not t & 136 and B[t] == 7:
                if (t >> 4) == (7 if W else 0):
                    for q in (5, 4, 3, 2):
                        ms.append(s | (t << 7) | (q << 14))
                elif not caponly:
                    ms.append(s | (t << 7))
                    if (s >> 4) == (1 if W else 6):
                        t2 = s + 2 * d
                        if B[t2] == 7:
                            ms.append(s | (t2 << 7))
            for dd in (d - 1, d + 1):
                t = s + dd
                if t & 136:
                    continue
                c = B[t]
                if c != 7 and (c > 7) != W:
                    if (t >> 4) == (7 if W else 0):
                        for q in (5, 4, 3, 2):
                            ms.append(s | (t << 7) | (q << 14))
                    else:
                        ms.append(s | (t << 7))
                elif t == EP and EP >= 0:
                    ms.append(s | (t << 7))
        elif a == 2 or a == 6:
            for d in DIRS[a]:
                t = s + d
                if t & 136:
                    continue
                c = B[t]
                if c == 7:
                    if not caponly:
                        ms.append(s | (t << 7))
                elif (c > 7) != W:
                    ms.append(s | (t << 7))
            if a == 6:
                # castling
                if W and s == 4:
                    if C & 1 and B[5] == 7 and B[6] == 7 and B[7] == 11 and not atk(4, False) and not atk(5, False) and not atk(6, False):
                        ms.append(4 | (6 << 7))
                    if C & 2 and B[3] == 7 and B[2] == 7 and B[1] == 7 and B[0] == 11 and not atk(4, False) and not atk(3, False) and not atk(2, False):
                        ms.append(4 | (2 << 7))
                elif not W and s == 116:
                    if C & 4 and B[117] == 7 and B[118] == 7 and B[119] == 3 and not atk(116, True) and not atk(117, True) and not atk(118, True):
                        ms.append(116 | (118 << 7))
                    if C & 8 and B[115] == 7 and B[114] == 7 and B[113] == 7 and B[112] == 3 and not atk(116, True) and not atk(115, True) and not atk(114, True):
                        ms.append(116 | (114 << 7))
        else:
            for d in DIRS[a]:
                t = s + d
                while not t & 136:
                    c = B[t]
                    if c == 7:
                        if not caponly:
                            ms.append(s | (t << 7))
                    else:
                        if (c > 7) != W:
                            ms.append(s | (t << 7))
                        break
                    t += d
    return ms

def make(m):
    global W, C, EP, KW, KB
    f = m & 127
    t = (m >> 7) & 127
    q = (m >> 14) & 7
    p = B[f]
    c = B[t]
    x = -1
    if abs(p - 7) == 1 and t == EP and EP >= 0:
        x = t + (-16 if W else 16)
        c = B[x]
        B[x] = 7
    B[t] = (q + 7 if W else 7 - q) if q else p
    B[f] = 7
    if abs(p - 7) == 6:
        if W:
            KW = t
        else:
            KB = t
        if abs(t - f) == 2:
            if t > f:
                B[t - 1] = B[t + 1]
                B[t + 1] = 7
            else:
                B[t + 1] = B[t - 2]
                B[t - 2] = 7
    nc = C
    if f == 4 or t == 4:
        nc &= ~3
    if f == 0 or t == 0:
        nc &= ~2
    if f == 7 or t == 7:
        nc &= ~1
    if f == 116 or t == 116:
        nc &= ~12
    if f == 112 or t == 112:
        nc &= ~8
    if f == 119 or t == 119:
        nc &= ~4
    nep = -1
    if abs(p - 7) == 1 and abs(t - f) == 32:
        nep = f + 16 if W else f - 16
    u = (m, c, C, EP, x)
    C = nc
    EP = nep
    W = not W
    return u

def unmake(u):
    global W, C, EP, KW, KB
    m, c, oc, oep, x = u
    f = m & 127
    t = (m >> 7) & 127
    q = (m >> 14) & 7
    p = B[t]
    W = not W
    if abs(p - 7) == 6:
        if W:
            KW = f
        else:
            KB = f
        if abs(t - f) == 2:
            if t > f:
                B[t + 1] = B[t - 1]
                B[t - 1] = 7
            else:
                B[t - 2] = B[t + 1]
                B[t + 1] = 7
    B[f] = (1 + 7 if W else 7 - 1) if q else p
    if x >= 0:
        B[t] = 7  # en passant target was empty; captured pawn sits at x
        B[x] = 6 if W else 8
    else:
        B[t] = c
    C = oc
    EP = oep

def ev():
    s = 0
    wb = 0
    bb = 0
    for i in range(128):
        if i & 136:
            continue
        v = B[i]
        if v == 7:
            continue
        p = v - 7
        a = abs(p)
        r = (7 - (i >> 4)) if p > 0 else (i >> 4)
        col = i & 7
        if col > 3:
            col = 7 - col
        val = V[a] + T[a - 1][r * 4 + col]
        if p > 0:
            s += val
            if a == 3:
                wb += 1
        else:
            s -= val
            if a == 3:
                bb += 1
    if wb >= 2:
        s += 30
    if bb >= 2:
        s -= 30
    return s if W else -s

class Abort(Exception):
    pass

def order(ms, ttmove, y):
    def sc(m):
        if m == ttmove:
            return 1 << 20
        t = B[(m >> 7) & 127]
        if t != 7:
            return 10000 + 10 * V[abs(t - 7)] - V[abs(B[m & 127] - 7)] // 10
        if m == KIL[2 * y] or m == KIL[2 * y + 1]:
            return 9000
        return 0
    ms.sort(key=sc, reverse=True)
    return ms

def qs(a, b, y):
    global N
    N += 1
    if N > BUD:
        raise Abort
    st = ev()
    if st >= b:
        return b
    if st > a:
        a = st
    if y > 40:
        return a
    inchk = atk(KW if W else KB, not W)
    for m in order(gen(0 if inchk else 1), 0, y):
        u = make(m)
        if atk(KW if not W else KB, W):
            unmake(u)
            continue
        try:
            s = -qs(-b, -a, y + 1)
        except Abort:
            unmake(u)
            raise
        unmake(u)
        if s >= b:
            return b
        if s > a:
            a = s
    return a

def sr(a, b, d, y):
    global N
    N += 1
    if N > BUD:
        raise Abort
    if d <= 0:
        return qs(a, b, y)
    al = a
    k = (bytes(B), W, C, EP)
    e = TT.get(k)
    ttm = 0
    if e and e[0] >= d:
        if e[2] == 0:
            return e[1]
        if e[2] == 1 and e[1] >= b:
            return e[1]
        if e[2] == 2 and e[1] <= a:
            return e[1]
        ttm = e[3]
    ms = order(gen(0), ttm, y)
    bs = -MATE - 1
    bm = 0
    legal = 0
    for m in ms:
        u = make(m)
        if atk(KW if not W else KB, W):
            unmake(u)
            continue
        legal += 1
        try:
            s = -sr(-b, -al, d - 1, y + 1)
        except Abort:
            unmake(u)
            raise
        unmake(u)
        if s > bs:
            bs = s
            bm = m
        if s > al:
            al = s
        if al >= b:
            if B[(m >> 7) & 127] == 7:
                KIL[2 * y + 1] = KIL[2 * y]
                KIL[2 * y] = m
            break
    if legal == 0:
        return -MATE + y if atk(KW if W else KB, not W) else 0
    if abs(bs) < MATE - 1000:
        fl = 2 if bs <= a else (1 if bs >= b else 0)
        TT[k] = (d, bs, fl, bm)
    return bs

def root():
    global N, TT
    ms = []
    for m in gen(0):
        u = make(m)
        if atk(KW if not W else KB, W):
            unmake(u)
            continue
        unmake(u)
        ms.append(m)
    if not ms:
        return None
    if len(ms) == 1:
        return ms[0]
    N = 0
    TT = {}
    for i in range(256):
        KIL[i] = 0
    best = ms[0]
    scores = {m: 0 for m in ms}
    for d in range(1, 9):
        try:
            ms.sort(key=lambda m: scores[m], reverse=True)
            al = -MATE - 1
            bb = -MATE - 1
            bm = best
            a = -MATE - 1
            b = MATE + 1
            for m in ms:
                u = make(m)
                try:
                    s = -sr(-b, -a, d - 1, 1)
                except Abort:
                    unmake(u)
                    raise
                unmake(u)
                scores[m] = s
                if s > bb:
                    bb = s
                    bm = m
                if s > a:
                    a = s
            best = bm
        except Abort:
            break
    return best

# ---- env driver: play the gauntlet through MAKEFUN_ENV_URL ----
ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")


def post(path, body):
    """POST a JSON body to the env and return its JSON answer."""
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")


def uci_of(m):
    """Move int -> UCI string."""
    s = "abcdefgh"[m & 7] + str((m >> 4) + 1) + "abcdefgh"[(m >> 7) & 7] + str(((m >> 7) >> 4) + 1)
    q = (m >> 14) & 7
    return s + ("nbrq"[q - 2] if q else "")


def fallback(legal):
    """Best 1-ply move from the env's legal list (safety net if root disagrees)."""
    best = None
    best_score = -MATE - 1
    for u in legal:
        f = "abcdefgh".index(u[0]) + (int(u[1]) - 1) * 16
        t = "abcdefgh".index(u[2]) + (int(u[3]) - 1) * 16
        q = "nbrq".index(u[4]) + 2 if len(u) == 5 else 0
        mv = f | (t << 7) | (q << 14)
        undo = make(mv)
        s = -ev()
        unmake(undo)
        if s > best_score:
            best_score = s
            best = mv
    return best


while True:
    g = post("/game", {})
    if g["status"] == "done":
        break
    while g["status"] == "your_move":
        parse_fen(g["fen"])
        mv = root()
        if mv is None or uci_of(mv) not in g["legal_moves"]:
            mv = fallback(g["legal_moves"])
        g = post("/move", {"game": g["game"], "move": uci_of(mv)})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)
