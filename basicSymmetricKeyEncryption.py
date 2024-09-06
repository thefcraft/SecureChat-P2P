import secrets
# import struct
from hashlib import sha256
# from itertools import cycle
# from tqdm import tqdm

class BasicSymmetricKeyEncrpter:
    def __init__(self, key: bytearray) -> None:
        # self.key = key
        self.key = bytearray(sha256(key + sha256(key + key).digest() + key).digest())
        self.key_len = len(self.key)
        
    @classmethod
    def from_random_key(cls, key_len=32):
        return cls(key = secrets.token_bytes(key_len))
    
    def encrypt_chunk(self, chunk, key):
        # return bytes(a ^ b for a, b in zip(chunk, cycle(key)))
        return bytes(a ^ b for a, b in zip(chunk, key))
    
    def set_key(self, key: bytearray):
        self.key = key
        self.key_len = len(self.key)
    
    @staticmethod
    def new_key(old_key, data_last):
        combined = old_key + data_last
        return bytearray(sha256(combined).digest())
    
    def update_key(self, data:bytearray):
        # change key based on the chunked data
        self.set_key(self.new_key(self.key, data))
    
    def encrypt(self, data:bytearray, update_key=False)->bytearray:
        result = bytearray()
    
        # Process the initial chunk separately
        initial_chunk = data[:self.key_len]
        result.extend(self.encrypt_chunk(initial_chunk, self.key))
        key = self.new_key(self.key, initial_chunk)

        # Process the rest of the data in chunks of 32 bytes
        for i in range(self.key_len, len(data), 32):
            chunk = data[i:i+32]  # len(32) .. sha256
            result.extend(self.encrypt_chunk(chunk, key))
            key = self.new_key(key, chunk)
        if update_key: self.set_key(key)
        return result
    
    def decrypt(self, data:bytearray, update_key=False)->bytearray:
        result = bytearray()
        
        # Process the initial chunk separately
        initial_chunk = data[:self.key_len]
        result.extend(self.encrypt_chunk(initial_chunk, self.key))
        key = self.new_key(self.key, result)

        # Process the rest of the data in chunks of 32 bytes
        for i in range(self.key_len, len(data), 32):
            chunk = data[i:i+32]
            decrypted = self.encrypt_chunk(chunk, key)
            result.extend(decrypted)
            key = self.new_key(key, decrypted)
            
        if update_key: self.set_key(key)
        return result

if __name__ == '__main__':
    
    original_data = b'''cryptor = BasicSymmetricKeyEncrpter(key=b"some secret key which is shared by rsa or so with help of maybe room code?..") 
# def middleware(data: str, encrypt: bool = True):
    
#     if encrypt: 
#         data:bytes = data.encode()
#         res:bytearray = cryptor.encrypt(data)
#         # cryptor.update_key(data)
#         print(f"encrypt => {bytes(res)}")
#         return base64.b64encode(res).decode() 
#     else:
#         res:bytearray = cryptor.decrypt(base64.b64decode(data))
#         # cryptor.update_key(res)
#         print(f"decrypt => {bytes(res)}")
#         return res.decode()'''
    
    # encrpter = BasicSymmetricKeyEncrpter.from_random_key(key_len=256)
    # encrpter1 = BasicSymmetricKeyEncrpter(key=b"laksh")
    # encrpter2 = BasicSymmetricKeyEncrpter(key=b"laksh")
    encrpter1 = BasicSymmetricKeyEncrpter(key=b"some secret key which is shared by rsa or so with help of maybe room code?..")
    encrpter2 = BasicSymmetricKeyEncrpter(key=b"some secret key which is shared by rsa or so with help of maybe room code?..")
    encrypted_data = encrpter1.encrypt(original_data, update_key=True)
    decrypted_data = encrpter2.decrypt(encrypted_data, update_key=True)
    encrpter1.update_key(original_data)
    encrpter2.update_key(decrypted_data)
    
    encrypted_data2 = encrpter1.encrypt(original_data, update_key=True)
    decrypted_data2 = encrpter2.decrypt(encrypted_data2, update_key=True)
    encrpter1.update_key(original_data)
    encrpter2.update_key(decrypted_data2)
    encrypted_data3 = encrpter1.encrypt(original_data, update_key=True)
    decrypted_data3 = encrpter2.decrypt(encrypted_data3, update_key=True)
    encrpter1.update_key(original_data)
    encrpter2.update_key(decrypted_data3)
    
    assert (original_data == decrypted_data)
    assert (original_data == decrypted_data2)
    assert (original_data == decrypted_data3)
    # with open('basicSymmetricKeyEncryption.crypt', 'wb') as f:
        # f.write(encrypted_data)
    
    # print(f"LEN[{len(original_data)}] original_data : ", original_data)
    # print(f"LEN[{len(encrypted_data)}] encrypted_data : ", encrypted_data)
    # print(f"LEN[{len(decrypted_data)}] decrypted_data : ", decrypted_data)
    
    
    
    # cryptor1 = BasicSymmetricKeyEncrpter(key=b"laksh")
    # cryptor2 = BasicSymmetricKeyEncrpter(key=b"laksh")
    
    # a1 = cryptor1.encrypt(b"My name is lak asd asd sh")
    # a2 = cryptor2.decrypt(a1)
    # print(a1, a2)
    # cryptor1.update_key(b"My name is lak asd asd sh")
    # cryptor2.update_key(a2)
    # print(cryptor1.key)
    # print(cryptor2.key)
    
    import base64
    cryptor1 = BasicSymmetricKeyEncrpter(key=b"some secret key which is shared by rsa or so with help of maybe room code?..") 
    cryptor2 = BasicSymmetricKeyEncrpter(key=b"some secret key which is shared by rsa or so with help of maybe room code?..") 
    def middleware(cryptor: BasicSymmetricKeyEncrpter, data: str, encrypt: bool = True):
        if encrypt: 
            data:bytes = data.encode()
            res:bytearray = cryptor.encrypt(data, update_key=True)
            cryptor.update_key(data)
            print(f"encrypt => {bytes(res)}")
            return base64.b64encode(res).decode() 
        else:
            data = base64.b64decode(data)
            res:bytearray = cryptor.decrypt(data, update_key=True)
            cryptor.update_key(res)
            print(f"decrypt => {bytes(res)}")
            return res.decode()
        
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))
    
    a = middleware(cryptor1, '''cryptor''')
    print(a)
    print(middleware(cryptor2, a, encrypt=False))