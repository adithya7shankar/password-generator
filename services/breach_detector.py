import requests
import hashlib
from typing import Dict, List, Any, Tuple
import time

class BreachDetector:
    """
    Service for checking if passwords have been exposed in data breaches
    using the Have I Been Pwned (HIBP) API.
    """
    
    def __init__(self):
        """Initialize the breach detector."""
        self.api_base_url = "https://api.pwnedpasswords.com/range/"
        self.last_check_time = {}  # Store the last check time for rate limiting
        
    def check_password(self, password: str) -> Tuple[bool, int]:
        """
        Check if a password has been exposed in known data breaches.
        
        Args:
            password: The password to check
            
        Returns:
            Tuple of (is_breached, count) where:
            - is_breached: True if the password has been found in breaches
            - count: Number of times the password appears in breaches (if found)
        """
        # Hash the password with SHA-1
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        
        # Split the hash - first 5 chars are sent to API, rest is used for comparison
        prefix = password_hash[:5]
        suffix = password_hash[5:]
        
        # Rate limit to avoid API abuse (wait at least 1.5 seconds between requests)
        current_time = time.time()
        if prefix in self.last_check_time:
            time_diff = current_time - self.last_check_time[prefix]
            if time_diff < 1.5:
                time.sleep(1.5 - time_diff)
        
        # Make API request
        try:
            response = requests.get(f"{self.api_base_url}{prefix}")
            self.last_check_time[prefix] = time.time()
            
            if response.status_code != 200:
                # API error or rate limit hit
                return False, 0
                
            # Process response
            hashes = response.text.split('\r\n')
            for h in hashes:
                # Each line is in format: SUFFIX:COUNT
                line_suffix, count = h.split(':')
                if line_suffix == suffix:
                    return True, int(count)
            
            # Password not found in breaches
            return False, 0
            
        except Exception as e:
            # Handle network errors, etc.
            print(f"Error checking breach status: {str(e)}")
            return False, 0
    
    def check_passwords(self, passwords: List[str]) -> Dict[str, Tuple[bool, int]]:
        """
        Check multiple passwords for breaches.
        
        Args:
            passwords: List of passwords to check
            
        Returns:
            Dictionary mapping each password to its breach status (is_breached, count)
        """
        results = {}
        for password in passwords:
            results[password] = self.check_password(password)
        return results
    
    def check_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Check if an email has been in any breaches.
        
        Note: This is a placeholder for future implementation. The actual HIBP API 
        for checking emails requires an API key and authentication.
        
        Args:
            email: Email address to check
            
        Returns:
            List of breach details or empty list if none found/error
        """
        # This would require API key for actual implementation
        # For now, we'll just return an example response format
        
        # In a real implementation you would:
        # 1. Use your API key in the request headers
        # 2. Make a request to the HIBP API endpoint for email breach checking
        # 3. Parse and return the response data
        
        return [] # Placeholder, would return actual breach data with API key 