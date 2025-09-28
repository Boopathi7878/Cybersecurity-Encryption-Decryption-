from flask import Flask, render_template, request

app = Flask(__name__)

# ------------------ Playfair Cipher Core ------------------ #
def generate_key_square(key: str):
    key = key.upper()
    seen = set()
    square = []
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J omitted
    for ch in key:
        if not ch.isalpha():
            continue
        if ch == "J":
            ch = "I"
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    for ch in alphabet:
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    return [square[i*5:(i+1)*5] for i in range(5)]

def find_position(square, ch):
    if ch == "J":
        ch = "I"
    for r in range(5):
        for c in range(5):
            if square[r][c] == ch:
                return r, c
    raise ValueError(f"{ch} not in square")

def preprocess_plaintext(plaintext, filler="X"):
    s = []
    for ch in plaintext.upper():
        if ch.isalpha():
            s.append('I' if ch == 'J' else ch)
    digraphs = []
    i = 0
    while i < len(s):
        a = s[i]
        if i+1 >= len(s):
            b = filler
            i += 1
        else:
            b = s[i+1]
            if a == b:
                b = filler
                i += 1
            else:
                i += 2
        digraphs.append((a, b))
    return digraphs

def encrypt_pair(pair, square):
    a, b = pair
    ra, ca = find_position(square, a)
    rb, cb = find_position(square, b)
    if ra == rb:
        return (square[ra][(ca+1)%5], square[rb][(cb+1)%5])
    if ca == cb:
        return (square[(ra+1)%5][ca], square[(rb+1)%5][cb])
    return (square[ra][cb], square[rb][ca])

def decrypt_pair(pair, square):
    a, b = pair
    ra, ca = find_position(square, a)
    rb, cb = find_position(square, b)
    if ra == rb:
        return (square[ra][(ca-1)%5], square[rb][(cb-1)%5])
    if ca == cb:
        return (square[(ra-1)%5][ca], square[(rb-1)%5][cb])
    return (square[ra][cb], square[rb][ca])

def encrypt(plaintext, key):
    square = generate_key_square(key)
    digraphs = preprocess_plaintext(plaintext)
    cipher_pairs = [encrypt_pair(p, square) for p in digraphs]
    return "".join(a+b for a,b in cipher_pairs)

def decrypt(ciphertext, key):
    square = generate_key_square(key)
    s = [ch for ch in ciphertext.upper() if ch.isalpha()]
    digraphs = [(s[i], s[i+1]) for i in range(0, len(s), 2)]
    plain_pairs = [decrypt_pair(p, square) for p in digraphs]
    return "".join(a+b for a,b in plain_pairs)

# ------------------ Flask Routes ------------------ #
@app.route("/", methods=["GET", "POST"])
def index():
    result, text, key = None, "", ""
    if request.method == "POST":
        key = request.form.get("key", "")
        text = request.form.get("text", "")
        action = request.form.get("action")
        if action == "encrypt":
            result = encrypt(text, key)
        elif action == "decrypt":
            result = decrypt(text, key)
    return render_template("index.html", result=result, text=text, key=key)

if __name__ == "__main__":
    app.run(debug=True)
