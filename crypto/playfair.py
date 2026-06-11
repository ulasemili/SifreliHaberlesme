def create_matrix(key):
    alphabet = "abcçdefgğhıijklmnoöprsştuüvyz .,!?:&"

    key = key.lower()
    seen = set()
    matrix_list = []

    # 🔹 önce key
    for char in key:
        if char in alphabet and char not in seen:
            matrix_list.append(char)
            seen.add(char)

    # 🔹 sonra kalanlar
    for char in alphabet:
        if char not in seen:
            matrix_list.append(char)

    # 🔹 6x6 matris
    matrix = [matrix_list[i:i+6] for i in range(0, 36, 6)]

    return matrix


def print_matrix(matrix):
    for row in matrix:
        print(" ".join(row))


#if __name__ == "__main__":
 #   key = "kerem"
  #  matrix = create_matrix(key)
   # print_matrix(matrix)


def find_position(matrix, char):
    for i in range(6):
        for j in range(6):
            if matrix[i][j] == char:
                return i, j
    raise ValueError(f"Karakter Matriste Bulunamadı! : {char}")


def prepare_text(text):
    text = text.lower()
    pairs = []

    i = 0
    while i < len(text):
        a = text[i]
        b = ''

        if i+1 < len(text):
            b = text[i+1]

        if a == b:
            pairs.append(a + '&')
            i += 1
        else:
            if b:
                pairs.append(a + b)
            else:
                pairs.append(a + '&')
            i += 2

    return pairs


def encrypt(text, matrix):
    pairs = prepare_text(text)
    cipher = ""

    for pair in pairs:
        a, b = pair
        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)

        # aynı satır
        if r1 == r2:
            cipher += matrix[r1][(c1+1) % 6]
            cipher += matrix[r2][(c2+1) % 6]

        # aynı sütun
        elif c1 == c2:
            cipher += matrix[(r1+1) % 6][c1]
            cipher += matrix[(r2+1) % 6][c2]

        # dikdörtgen
        else:
            cipher += matrix[r1][c2]
            cipher += matrix[r2][c1]

    return cipher


def decrypt(cipher, matrix):
    text = ""

    for i in range(0, len(cipher), 2):
        a = cipher[i]
        b = cipher[i+1]

        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)

        if r1 == r2:
            text += matrix[r1][(c1-1) % 6]
            text += matrix[r2][(c2-1) % 6]

        elif c1 == c2:
            text += matrix[(r1-1) % 6][c1]
            text += matrix[(r2-1) % 6][c2]

        else:
            text += matrix[r1][c2]
            text += matrix[r2][c1]
    
    if text.endswith("&"):
        text = text[:-1]

    return text

if __name__ == "__main__":
    key = "kerem"
    matrix = create_matrix(key)

    text = "merhaba"
    encrypted = encrypt(text, matrix)
    decrypted = decrypt(encrypted, matrix)

    print("Şifreli:", encrypted)
    print("Çözülmüş:", decrypted)