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
            # Calculate HMAC with generated_hash and salt
            hash_input = hmac.new(bytes.fromhex(self.generated_hash), self.salt.encode(), hashlib.sha256).hexdigest()
            hs = int(4)

            def divisible(hash_val, divisor):
                return int(hash_val, 16) % divisor == 0
                #this just checks if hash is divisible by four

            if divisible(hash_input, hs):
                self.crash_point = 1
            else:
                h = int(hash_input[:int(52 / 4)], 16)
                e = 2 ** 52
                self.crash_point = math.floor((100 * e - h) / (e - h)) / 100.0
                # for this logic below, if crash_point is greater than 5, for 66% of the time return a value in between 1 and 2. let's say value is 6.71, newvalue will be 1.67.. if value is 30.9, new value will be 1.31
                if self.crash_point > 5 and not divisible(hash_input, 3):
                    self.crash_point = round(float("1." + str(self.crash_point).replace(".", "")), 2)
                    return self.crash_point
                if self.crash_point > 10 and divisible(hash_input, 5):
                    self.crash_point = 1
                    return self.crash_point
                
                
               
                
                

            if self.crash_point > 500:
                self.crash_point = 500
                    
                    

            return self.crash_point

    def get_generated_hash(self):
        self.generated_hash = self.generate_hash()
        return self.generated_hash, self.server_seed, self.salt

    def get_crash_point(self):
        return self.crash_point

# Create an instance of the ServerSeedGenerator class

def VerifyHash(hash, game_hash, seed, salt):
        # Received hash, server seed, and salt
    received_hash = hash
    game_hash = game_hash
    received_server_seed = seed
    salt = salt

    # Concatenate hash and server seed
    input_string = received_hash + received_server_seed

    # Apply HMAC-SHA-256 with the salt
    generated_hash = hmac.new(salt.encode(), input_string.encode(), hashlib.sha256).hexdigest()

    # Compare generated hash with received hash
    if generated_hash == game_hash:
        return True
        
    else:
        return False
        
