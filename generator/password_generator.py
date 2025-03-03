import random
import string
import re
from typing import List, Dict, Any, Optional

class PasswordGenerator:
    """
    A class to generate passwords based on user keywords and constraint sets.
    """
    
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special_chars = string.punctuation
        
    def generate_password(self, 
                         keywords: List[str], 
                         constraints: Dict[str, Any]) -> str:
        """
        Generate a password based on user keywords and constraints.
        
        Args:
            keywords: List of user-provided keywords
            constraints: Dictionary containing constraint rules
            
        Returns:
            A generated password string
        """
        # Extract constraints
        min_length = constraints.get('min_length', 8)
        max_length = constraints.get('max_length', 20)
        require_uppercase = constraints.get('require_uppercase', True)
        require_lowercase = constraints.get('require_lowercase', True)
        require_digits = constraints.get('require_digits', True)
        require_special = constraints.get('require_special', True)
        included_chars = constraints.get('included_chars', [])
        excluded_chars = constraints.get('excluded_chars', [])
        
        # Initialize password components
        password_components = []
        
        # Process keywords
        if keywords:
            # Select at least one keyword
            selected_keyword = random.choice(keywords)
            
            # Randomly modify the keyword (capitalize, add number, etc.)
            modified_keyword = self._modify_keyword(selected_keyword)
            password_components.append(modified_keyword)
        
        # Ensure we meet character type requirements
        if require_uppercase and not any(c.isupper() for c in ''.join(password_components)):
            password_components.append(random.choice(self.uppercase))
            
        if require_lowercase and not any(c.islower() for c in ''.join(password_components)):
            password_components.append(random.choice(self.lowercase))
            
        if require_digits and not any(c.isdigit() for c in ''.join(password_components)):
            password_components.append(random.choice(self.digits))
            
        if require_special and not any(c in self.special_chars for c in ''.join(password_components)):
            # Filter out any excluded special characters
            available_special = [c for c in self.special_chars if c not in excluded_chars]
            if available_special:
                password_components.append(random.choice(available_special))
        
        # Add included characters if specified
        for char in included_chars:
            if char not in ''.join(password_components):
                password_components.append(char)
        
        # Add random characters until we reach minimum length
        current_length = sum(len(component) for component in password_components)
        
        while current_length < min_length:
            char_pool = []
            if require_lowercase:
                char_pool.extend(self.lowercase)
            if require_uppercase:
                char_pool.extend(self.uppercase)
            if require_digits:
                char_pool.extend(self.digits)
            if require_special:
                char_pool.extend([c for c in self.special_chars if c not in excluded_chars])
                
            # Remove excluded characters from pool
            char_pool = [c for c in char_pool if c not in excluded_chars]
            
            if char_pool:
                password_components.append(random.choice(char_pool))
                current_length += 1
        
        # Shuffle the components
        random.shuffle(password_components)
        
        # Join and truncate if necessary
        password = ''.join(password_components)
        if len(password) > max_length:
            password = password[:max_length]
            
        return password
    
    def _modify_keyword(self, keyword: str) -> str:
        """
        Apply random modifications to a keyword to make it more secure.
        
        Args:
            keyword: The keyword to modify
            
        Returns:
            Modified keyword
        """
        modifications = [
            # Capitalize the keyword
            lambda k: k.capitalize(),
            # Capitalize random letter
            lambda k: k[:random.randint(0, max(0, len(k)-1))] + 
                     (k[random.randint(0, max(0, len(k)-1))].upper() if k else '') + 
                     k[random.randint(0, max(0, len(k)-1))+1:] if len(k) > 1 else k,
            # Add a random digit to the end
            lambda k: k + random.choice(self.digits),
            # Add a random digit to the beginning
            lambda k: random.choice(self.digits) + k,
            # Replace a random letter with a similar-looking number (e.g., 'e' -> '3')
            lambda k: self._replace_with_leet(k),
            # Add a random special character
            lambda k: k + random.choice(self.special_chars),
            # No modification
            lambda k: k
        ]
        
        # Apply 1-3 random modifications
        num_modifications = random.randint(1, 3)
        modified = keyword
        
        for _ in range(num_modifications):
            modification = random.choice(modifications)
            modified = modification(modified)
            
        return modified
    
    def _replace_with_leet(self, text: str) -> str:
        """
        Replace characters with their 'leet speak' equivalents.
        
        Args:
            text: The text to convert
            
        Returns:
            Text with some characters replaced
        """
        leet_map = {
            'a': '4',
            'e': '3',
            'i': '1',
            'o': '0',
            's': '5',
            't': '7',
            'l': '1',
            'z': '2'
        }
        
        # Only replace some characters (not all)
        result = list(text)
        positions = [i for i, char in enumerate(text.lower()) if char in leet_map]
        
        if positions:
            # Replace 1 or 2 characters at most
            num_to_replace = min(len(positions), random.randint(1, 2))
            for pos in random.sample(positions, num_to_replace):
                result[pos] = leet_map[text[pos].lower()]
                
        return ''.join(result)
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Evaluate the strength of a password.
        
        Args:
            password: The password to evaluate
            
        Returns:
            Dictionary with strength metrics
        """
        strength = {
            'score': 0,  # 0-100
            'length': len(password),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_digits': bool(re.search(r'[0-9]', password)),
            'has_special': bool(re.search(r'[^A-Za-z0-9]', password)),
            'feedback': []
        }
        
        # Score based on length (up to 40 points)
        length_score = min(40, len(password) * 2)
        strength['score'] += length_score
        
        # Score based on character variety (up to 40 points)
        variety_score = 0
        if strength['has_uppercase']:
            variety_score += 10
        if strength['has_lowercase']:
            variety_score += 10
        if strength['has_digits']:
            variety_score += 10
        if strength['has_special']:
            variety_score += 10
        strength['score'] += variety_score
        
        # Score based on entropy and patterns (up to 20 points)
        entropy_score = 0
        
        # Check for repeated characters
        repeated = re.search(r'(.)\1{2,}', password)
        if not repeated:
            entropy_score += 5
        else:
            strength['feedback'].append("Avoid repeated characters")
        
        # Check for sequential characters
        sequential = re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789|890)', 
                              password.lower())
        if not sequential:
            entropy_score += 5
        else:
            strength['feedback'].append("Avoid sequential characters")
        
        # Check for keyboard patterns
        keyboard_patterns = re.search(r'(qwer|asdf|zxcv|1234|5678|9012)', password.lower())
        if not keyboard_patterns:
            entropy_score += 5
        else:
            strength['feedback'].append("Avoid keyboard patterns")
        
        # Bonus for mixing character types throughout
        if (strength['has_uppercase'] and strength['has_lowercase'] and 
            strength['has_digits'] and strength['has_special']):
            entropy_score += 5
            
        strength['score'] += entropy_score
        
        # Add feedback based on score
        if strength['score'] < 50:
            strength['feedback'].append("Password is weak")
        elif strength['score'] < 80:
            strength['feedback'].append("Password is moderate")
        else:
            strength['feedback'].append("Password is strong")
            
        return strength
