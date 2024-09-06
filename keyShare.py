import random, math


def is_prime(n, k=20):
    """Miller-Rabin primality test."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d where d is odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=256):
    """Generate a random prime number of 'bits' length."""
    while True:
        candidate = random.getrandbits(bits)
        if is_prime(candidate):
            return candidate

def gcd(a:int, b:int)->int:
    # The Euclidean algorithm is based on the principle that the GCD of two numbers also divides their difference.
    while b:
        a, b = b, a % b
    return a
def is_coprime(a:int, b:int)->bool:
    return gcd(a, b)==1
def is_integer(n:int)->bool:
    return n%1 == 0

def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y
def modular_inverse(e: int, phi: int) -> int:
    g, x, y = extended_gcd(e, phi)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    else:
        return x % phi

def int_to_base255(n: int) -> bytearray:
    if n == 0:
        return bytearray(b'\0')
    
    digits = b''
    while n:
        digits += chr(n % 255).encode()
        n //= 255
    
    return bytearray(reversed(digits))  # Reverse the list to get the correct order
def base255_to_int(digits: bytearray) -> int:
    n = 0
    for digit in digits:
        n = n * 255 + digit
    
    return n
def int_to_bytes(value, byte_size=255):
    """Convert an integer to a list of bytes, ensuring each byte is within the range 0-255."""
    bytes_list = []
    while value > 0:
        bytes_list.append(value % byte_size)
        value //= byte_size
    return bytes_list[::-1]  # Reverse the list to maintain the correct order

def split_into_chunks(lst, chunk_size=3):
    """Splits a list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def cryptor_raw(data:int, key:int, n:int)->int:
    assert data < n, "data must be less than n"
    result = 1  # Initialize result
    base = data % n  # Ensure base is in the correct range

    while key > 0:
        # If key is odd, multiply the base with the result
        if key % 2 == 1:
            result = (result * base) % n
        
        # Now key must be even, divide it by 2
        key = key // 2
        base = (base * base) % n  # Square the base and reduce it modulo n

    return result
def rsaCryptor(data:bytearray, key:int, n:int)->bytearray:
    # encoded = [cryptor_raw(base255_to_int(i), key, n) for i in split_into_chunks(data, chunk_size=1)]
    result = []
    for i in data:
        encoded_value = cryptor_raw(i, key, n)
        encoded_bytes = int_to_bytes(encoded_value)
        result.append(len(encoded_bytes))  # Store the length of the encoded segment
        result.extend(encoded_bytes)
    return bytearray(result)
    
class RSA:
    def __init__(self, p=None, q=None)->None:
        self.p = p or generate_prime(bits=256)
        self.q = q or generate_prime(bits=512)
        # mod = lambda x: x if x>=0 else -x
        # assert mod(self.p - self.q) > 1000_000_000, "gap between p and q are shoud be very large"
        assert self.p != self.q
        self.n = self.p*self.q
        self.phi = (self.p-1)*(self.q-1)
        self.public_key = self.__public_key()
        self.private_key = self.__private_key()
    def __public_key(self):
        # for e in [3, 5, 17, 257, 65537]:
            # if e < self.phi and is_coprime(e, self.phi): return e
        for e in range(2+1, self.phi):
            if is_coprime(e, self.phi): return e
        raise ValueError("Failed to find a valid public key")
    def __private_key(self):
        return modular_inverse(self.public_key, self.phi)
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(\n"
                f"    p={self.p},\n"
                f"    q={self.q},\n"
                f"    phi={self.phi},\n"
                f"    public_key={self.public_key},\n"
                f"    private_key={self.private_key},\n"
                f"    n={self.n}\n)")
    def decryptor_raw(self, data:int)->int:
        return cryptor_raw(data, self.private_key, self.n)
    def decryptor(self, data:bytearray)->bytearray:
        decrypted = []
        idx = 0
        while idx < len(data):
            segment_length = data[idx]
            idx += 1
            encoded_value = 0
            for j in range(segment_length):
                encoded_value = encoded_value * 255 + data[idx]
                idx += 1
            decrypted_value = self.decryptor_raw(encoded_value)
            decrypted.append(decrypted_value)
        return bytearray(decrypted)


if __name__ == "__main__":
    # client = RSA()
    # client_pubkey = client.public_key
    # client_n = client.n

    server = RSA()
    print(server)
    server_pubkey = server.public_key
    server_n = server.n
    
    m = 999
    print(f"original message : {m}")
    c = cryptor_raw(m, key=server_pubkey, n=server_n)
    print(f"encrypted message : {c}")
    m = server.decryptor_raw(c)
    print(f"decrypted message : {m}")
    
    import secrets
    
    key = bytearray(secrets.token_bytes(64))
    # client want to send to server
    message = key
    print(message)
    message_encrypted = rsaCryptor(message, key=server_pubkey, n=server_n)
    print(len(message_encrypted))
    message_decrypted = server.decryptor(message_encrypted)
    print(len(message_decrypted))
    assert message_decrypted == message
    # handshake ig signature ...
    
    import base64
    PUBLIC_KEY = 7
    PUBLIC_N = 304243382736758884459971936886812234827429608133610358061501186514883490809124898877533849379680993610204403562210743162143491931645358535092049777704258428888066813333841945742158507982135578125656903038159181086130762852486028357
    ske_key = bytearray(secrets.token_bytes(64))
    ske_key_encrypted = base64.b64encode(rsaCryptor(ske_key, key=PUBLIC_KEY, n=PUBLIC_N)).decode()
    ske_key_encrypted = base64.b64encode(bytearray(b'\xcf]x\x9d\xddP\xbd;\x97\xdc\x8f\xca\x1e\x0e\x82\xd1\x93\xa2D\x9dvjr7\xb2\xb03\xb0Bz\xca\xee\xaaN\x1c\\t.\xc0\x8bOpq\xe1\x08\n\xba\x9do\x9b\xc6\xed\xfd\xd8^\xdf\x9c\tp\xf7\xa2\xdd)k')).decode()
    print(f"KEY: {ske_key_encrypted}")
    
    
    ske_key = bytearray(b'4)\x0c\xdefq\x08\xbcJ\x8c4[\x0f\x9aF\xee\x98\x8dl\xbb\xe4\x85\x0c\xfbJ\x06U\xdf\x04\x98a\xac2\xe3\xc3\xf8\x19r\xed\xb7\x95N$\xfa\xee&\x01O\xaf\xf0\xe6\xc1\xdb\r\x9c*\xab\x85\x16\x00\xeb\x12\xad<')
    print(f"ske_key: {ske_key}")
    try:
        ske_key_encrypted = rsaCryptor(ske_key, key=PUBLIC_KEY, n=PUBLIC_N)
        print(f"ske_key_encrypted: {ske_key_encrypted}")
    except Exception as e:
        print(f"ERROR: {e}")
    a = int_to_base255(100)
    print(a)
    print(base255_to_int(a))