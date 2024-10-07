import nacl.utils
from nacl.public import PrivateKey

# Funkcja generująca klucz prywatny i publiczny
def generate_keys():
    private_key = PrivateKey.generate()  # Generowanie klucza prywatnego
    public_key = private_key.public_key  # Uzyskiwanie klucza publicznego z klucza prywatnego
    
    return private_key, public_key

# Generowanie kluczy
private_key, public_key = generate_keys()

# Wyświetlanie kluczy w formacie hex
print(f"Prywatny klucz: {private_key.encode().hex()}")
print(f"Publiczny klucz: {public_key.encode().hex()}")