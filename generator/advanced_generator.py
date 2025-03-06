import random
import string
import re
from typing import List, Dict, Any, Optional
import os

class AdvancedGenerator:
    """
    Advanced password generator with support for passphrases,
    pronounceable passwords, and pattern-based generation.
    """
    
    def __init__(self):
        """Initialize the advanced generator."""
        # Load word lists for passphrases
        self.common_words = self._load_word_list("common_words.txt", ["password", "welcome", "admin", "user"])
        
        # Syllables for pronounceable passwords
        self.consonants = 'bcdfghjklmnpqrstvwxyz'
        self.vowels = 'aeiou'
        self.consonant_pairs = ['bl', 'br', 'ch', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 
                               'pl', 'pr', 'sc', 'sh', 'sk', 'sl', 'sm', 'sn', 'sp', 'st', 
                               'sw', 'th', 'tr', 'tw', 'wh', 'wr']
        self.vowel_pairs = ['ai', 'ay', 'ea', 'ee', 'ei', 'eu', 'ie', 'oo', 'ou', 'ow', 'oy']
        self.end_consonants = ['ck', 'ft', 'ld', 'lk', 'lm', 'lp', 'lt', 'mp', 'nd', 'nk', 
                             'nt', 'pt', 'rd', 'rk', 'rm', 'rn', 'rp', 'rt', 'sk', 'sp', 
                             'ss', 'st', 'th']
        
    def _load_word_list(self, filename: str, fallback_words: List[str]) -> List[str]:
        """
        Load a word list from a file or use fallback words.
        
        Args:
            filename: Path to the word list file
            fallback_words: Words to use if file cannot be loaded
            
        Returns:
            List of words
        """
        words = []
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, "wordlists", filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    words = [word.strip().lower() for word in f if len(word.strip()) >= 3]
        except Exception as e:
            print(f"Error loading word list: {str(e)}")
        
        # Use fallback if no words were loaded
        if not words:
            words = fallback_words
            
        return words
    
    def generate_passphrase(self, 
                           num_words: int = 4, 
                           separator: str = "-", 
                           capitalize: bool = True,
                           include_number: bool = True,
                           include_special: bool = True) -> str:
        """
        Generate a memorable passphrase with common words.
        
        Args:
            num_words: Number of words to include (3-6 recommended)
            separator: Character(s) to separate words
            capitalize: Whether to capitalize the first letter of each word
            include_number: Whether to append a number
            include_special: Whether to append a special character
            
        Returns:
            Generated passphrase
        """
        if num_words < 2:
            num_words = 2  # Minimum words for security
        
        # Select random words
        if len(self.common_words) < num_words:
            # Add fallback words if not enough words available
            self.common_words.extend(["secure", "protect", "defend", "guard", "shield"])
            
        selected_words = random.sample(self.common_words, num_words)
        
        # Apply capitalization if requested
        if capitalize:
            selected_words = [word.capitalize() for word in selected_words]
        
        # Add a number if requested
        if include_number:
            selected_words[-1] = f"{selected_words[-1]}{random.randint(0, 999)}"
        
        # Add a special character if requested
        if include_special:
            special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
            selected_words[-1] = f"{selected_words[-1]}{random.choice(special_chars)}"
        
        # Join words with separator
        return separator.join(selected_words)
    
    def generate_pronounceable(self, 
                              length: int = 12,
                              include_number: bool = True,
                              include_special: bool = True) -> str:
        """
        Generate a pronounceable password that is easier to remember.
        
        Args:
            length: Approximate desired length (may vary slightly)
            include_number: Whether to include a number
            include_special: Whether to include a special character
            
        Returns:
            Pronounceable password
        """
        min_syllables = max(2, length // 4)
        max_syllables = max(3, length // 3)
        
        num_syllables = random.randint(min_syllables, max_syllables)
        
        # Generate syllables
        password = ""
        for i in range(num_syllables):
            # Randomly choose syllable pattern
            pattern = random.choice([
                "CV",   # consonant-vowel (ba, ce, di)
                "VC",   # vowel-consonant (ab, ed, il) 
                "CVC",  # consonant-vowel-consonant (bam, cel, dip)
                "CVVC", # consonant-vowel-vowel-consonant (baim, ceel, doop)
                "CCVC", # consonant-consonant-vowel-consonant (slam, cred, prot)
            ])
            
            syllable = ""
            for char in pattern:
                if char == 'C':
                    # Use consonant pair at the beginning of syllable
                    if len(syllable) == 0 and random.random() < 0.3:
                        syllable += random.choice(self.consonant_pairs)
                    # Use ending consonant pair at the end
                    elif char == pattern[-1] and random.random() < 0.3:
                        syllable += random.choice(self.end_consonants)
                    else:
                        syllable += random.choice(self.consonants)
                elif char == 'V':
                    # Use vowel pair with some probability
                    if random.random() < 0.3:
                        syllable += random.choice(self.vowel_pairs)
                    else:
                        syllable += random.choice(self.vowels)
            
            password += syllable
            
        # Ensure minimum length
        while len(password) < length - 2:  # -2 to leave room for number/special
            if random.random() < 0.5:
                syllable = random.choice(self.vowels) + random.choice(self.consonants)
            else:
                syllable = random.choice(self.consonants) + random.choice(self.vowels)
            password += syllable
        
        # Capitalize first letter
        password = password[:1].upper() + password[1:]
        
        # Add a number if requested
        if include_number:
            password += str(random.randint(0, 9))
        
        # Add a special character if requested
        if include_special:
            special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
            password += random.choice(special_chars)
        
        return password[:length]  # Ensure exact length
    
    def generate_pattern_based(self, pattern: str) -> str:
        """
        Generate a password based on a pattern.
        
        Pattern syntax:
        - a: lowercase letter
        - A: uppercase letter
        - n: number
        - s: special character
        - x: any character (letter, number, or special)
        - Any other character is included literally
        
        Examples:
        - "aaaa-nnnn-aaaa" -> "wxyz-1234-abcd"
        - "Aaa-nnn-sss" -> "Bcd-456-!@#"
        
        Args:
            pattern: Pattern to follow
            
        Returns:
            Generated password following the pattern
        """
        password = ""
        
        for char in pattern:
            if char == 'a':
                password += random.choice(string.ascii_lowercase)
            elif char == 'A':
                password += random.choice(string.ascii_uppercase)
            elif char == 'n':
                password += random.choice(string.digits)
            elif char == 's':
                password += random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?/")
            elif char == 'x':
                all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
                password += random.choice(all_chars)
            else:
                # Keep any other character as-is (literals)
                password += char
                
        return password
    
    def validate_pattern(self, pattern: str) -> bool:
        """
        Validate that a pattern contains only supported characters.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            True if pattern is valid, False otherwise
        """
        return bool(re.match(r'^[aAnsxwWdDcC\-_.,;:|!@#$%^&*()=+\[\]{}]+$', pattern))

    def generate_emoji_password(self, num_emoji: int = 4, include_text: bool = True) -> str:
        """
        Generate a password containing emojis.
        
        Args:
            num_emoji: Number of emojis to include
            include_text: Whether to include text characters as well
            
        Returns:
            Password with emojis
        """
        # Common emojis that are widely supported
        emojis = [
            "😀", "😁", "😂", "😃", "😄", "😅", "😆", "😇", "😈", "😉", "😊", "😋", "😌", 
            "😍", "😎", "😏", "😐", "😑", "❤️", "💙", "💚", "💛", "💜", "💔", "✨", "⭐", 
            "🔥", "💧", "❄️", "🌟", "⚡", "☀️", "🌈", "🍎", "🍌", "🍒", "🍓", "🍇", "🥝", 
            "🍕", "🍔", "🌮", "🍦", "🍭", "🍫", "🍿", "🥤", "☕", "🍷", "🥂", "🎂", "🎮",
            "🏀", "⚽", "🏈", "⚾", "🎾", "🎯", "🏆", "🥇", "🥈", "🥉"
        ]
        
        # Select random emojis
        selected_emojis = random.sample(emojis, min(num_emoji, len(emojis)))
        
        if include_text:
            # Add some text characters between emojis
            result = ""
            for emoji in selected_emojis:
                if result:
                    # Add 1-3 random characters between emojis
                    chars = random.randint(1, 3)
                    for _ in range(chars):
                        char_type = random.randint(0, 2)
                        if char_type == 0:
                            result += random.choice(string.ascii_letters)
                        elif char_type == 1:
                            result += random.choice(string.digits)
                        else:
                            result += random.choice("!@#$%^&*()-_=+")
                result += emoji
            return result
        else:
            # Just return the emojis joined together
            return "".join(selected_emojis) 