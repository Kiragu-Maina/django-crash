import hashlib
import hmac
import math
import secrets  # Import the secrets module for secure random generation

class ServerSeedGenerator:
    def __init__(self):
        # Generate a secure random server seed and salt
        self.server_seed = secrets.token_hex(32)  # Generates a random hexadecimal string of 32 bytes
        self.salt = secrets.token_hex(16)
        self.generated_hash = None
        self.crash_point = None

    def generate_hash(self):
        self.generated_hash = hashlib.sha256(self.server_seed.encode()).hexdigest()
        return self.generated_hash

    def crash_point_from_hash(self):
        hash_input = hmac.new(self.server_seed.encode(), self.salt.encode(), hashlib.sha256).hexdigest()
        hs = int(100 / 4)

        def divisible(hash_val, divisor):
            return int(hash_val, 16) % divisor == 0

        if divisible(hash_input, hs):
            self.crash_point = 1
        else:
            h = int(hash_input[:int(52 / 4)], 16)
            e = 2 ** 52
            self.crash_point = math.floor((100 * e - h) / (e - h)) / 100.0

        return self.crash_point

    def get_generated_hash(self):
        return self.generated_hash

    def get_crash_point(self):
        return self.crash_point

# Create an instance of the ServerSeedGenerator class

