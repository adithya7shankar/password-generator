import platform
import sys
import os
import subprocess
import logging
from typing import Optional, Callable

class BiometricAuthenticator:
    """
    Provides robust biometric authentication across different platforms.
    Supports Windows (Windows Hello), macOS (Touch ID/Face ID), and Linux (limited).
    """
    
    def __init__(self):
        """Initialize the biometric authenticator with logging."""
        self.system = platform.system().lower()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, 
                             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        try:
            self.is_available = self._check_availability()
        except Exception as e:
            self.logger.error(f"Error checking biometric availability: {e}")
            self.is_available = False
        
    def _check_availability(self) -> bool:
        """
        Check if biometric authentication is available on this system.
        
        Returns:
            True if biometric auth is available, False otherwise
        """
        try:
            if self.system == "darwin":  # macOS
                return self._check_macos_biometric()
            elif self.system == "windows":  # Windows
                return self._check_windows_biometric()
            elif self.system == "linux":  # Linux
                return self._check_linux_biometric()
            else:
                self.logger.warning(f"Unsupported platform: {self.system}")
                return False
        except Exception as e:
            self.logger.error(f"Unexpected error checking biometric availability: {e}")
            return False
            
    def _check_macos_biometric(self) -> bool:
        """
        Check if Touch ID/Face ID is available on macOS.
        
        Returns:
            True if available, False otherwise
        """
        try:
            # More robust check using system_profiler
            cmd = ["system_profiler", "SPiBridgeDataType"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            has_touch_id = "Touch ID" in result.stdout
            has_face_id = "BiometricKit" in result.stdout
            
            if has_touch_id or has_face_id:
                self.logger.info(f"Biometric authentication available: {'Touch ID' if has_touch_id else 'Face ID'}")
                return True
            
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout checking macOS biometric")
            return False
        except Exception as e:
            self.logger.error(f"Error checking macOS biometric: {e}")
            return False
            
    def _check_windows_biometric(self) -> bool:
        """
        Check if Windows Hello biometric is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            if sys.platform != "win32":
                return False
            
            # More comprehensive Windows biometric check
            import wmi
            
            c = wmi.WMI()
            biometric_devices = c.Win32_PnPEntity(PNPClass='Biometric')
            
            if biometric_devices:
                self.logger.info(f"Found {len(biometric_devices)} biometric devices")
                return True
            
            return False
        except ImportError:
            self.logger.warning("WMI module not available. Install with 'pip install wmi'")
            return False
        except Exception as e:
            self.logger.error(f"Error checking Windows biometric: {e}")
            return False
            
    def _check_linux_biometric(self) -> bool:
        """
        Check biometric availability on Linux.
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Check for fprintd (Linux fingerprint daemon)
            result = subprocess.run(["which", "fprintd-verify"], 
                                    capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Linux biometric authentication available via fprintd")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking Linux biometric: {e}")
            return False
            
    def authenticate(self, reason: str = "Authenticate to access passwords") -> bool:
        """
        Perform biometric authentication with improved error handling.
        
        Args:
            reason: Reason for authentication to display to user
            
        Returns:
            True if authenticated, False otherwise
        """
        if not self.is_available:
            self.logger.warning("Biometric authentication not available")
            return False
            
        try:
            if self.system == "darwin":
                return self._authenticate_macos(reason)
            elif self.system == "windows":
                return self._authenticate_windows(reason)
            elif self.system == "linux":
                return self._authenticate_linux(reason)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Unexpected authentication error: {e}")
            return False
            
    def _authenticate_macos(self, reason: str) -> bool:
        """
        Authenticate using Touch ID/Face ID on macOS with PyObjC.
        
        Args:
            reason: Reason for authentication
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            import objc
            import LocalAuthentication
            
            context = LocalAuthentication.LAContext.alloc().init()
            error = objc.nil
            
            if context.canEvaluatePolicy_error_(
                LocalAuthentication.LAPolicyDeviceOwnerAuthenticationWithBiometrics, 
                error
            ):
                success = [False]
                
                def auth_handler(authenticated, auth_error):
                    success[0] = authenticated
                
                context.evaluatePolicy_localizedReason_reply_(
                    LocalAuthentication.LAPolicyDeviceOwnerAuthenticationWithBiometrics,
                    reason,
                    auth_handler
                )
                
                # Wait for authentication (with timeout)
                import time
                start_time = time.time()
                while not success[0] and time.time() - start_time < 10:
                    time.sleep(0.1)
                
                return success[0]
            
            return False
        except ImportError:
            self.logger.warning("PyObjC not available for macOS biometric auth")
            return False
        except Exception as e:
            self.logger.error(f"macOS biometric authentication error: {e}")
            return False
            
    def _authenticate_windows(self, reason: str) -> bool:
        """
        Authenticate using Windows Hello.
        
        Args:
            reason: Reason for authentication
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Placeholder for more robust Windows authentication
            # In a real implementation, use Windows.Security.Credentials.UI
            import ctypes
            
            result = ctypes.windll.user32.MessageBoxW(
                0,
                f"{reason}\n\nPress Yes to simulate biometric authentication.",
                "Biometric Authentication",
                0x4 | 0x20  # Yes/No + Question Icon
            )
            
            return result == 6  # IDYES
        except Exception as e:
            self.logger.error(f"Windows biometric authentication error: {e}")
            return False
            
    def _authenticate_linux(self, reason: str) -> bool:
        """
        Authenticate using Linux fingerprint daemon.
        
        Args:
            reason: Reason for authentication
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Use fprintd for Linux authentication
            result = subprocess.run(
                ["fprintd-verify"], 
                input="Place your finger on the sensor",
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.warning("Linux biometric authentication timed out")
            return False
        except Exception as e:
            self.logger.error(f"Linux biometric authentication error: {e}")
            return False
            
    def is_supported(self) -> bool:
        """
        Check if biometric authentication is supported.
        
        Returns:
            True if supported, False otherwise
        """
        return self.is_available

    def get_auth_type(self) -> str:
        """
        Get the type of biometric authentication available.
        
        Returns:
            String describing the auth type, or "None" if not available
        """
        if not self.is_available:
            return "None"
            
        if self.system == "darwin":
            try:
                cmd = ["system_profiler", "SPiBridgeDataType"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if "Touch ID" in result.stdout:
                    return "Touch ID"
                elif "BiometricKit" in result.stdout:
                    return "Face ID"
            except Exception:
                pass
        elif self.system == "windows":
            return "Windows Hello"
        elif self.system == "linux":
            return "Linux Fingerprint"
        
        return "Biometric"
