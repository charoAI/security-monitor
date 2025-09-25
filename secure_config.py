import keyring
import os
from getpass import getpass

class SecureConfig:
    SERVICE_NAME = "SecurityMonitor"
    
    @staticmethod
    def store_email_credentials():
        """Store credentials securely in Windows Credential Manager"""
        email = input("Enter email address: ")
        password = getpass("Enter email password (hidden): ")
        
        keyring.set_password(SecureConfig.SERVICE_NAME, "email", email)
        keyring.set_password(SecureConfig.SERVICE_NAME, "password", password)
        print("Credentials stored securely in Windows Credential Manager")
    
    @staticmethod
    def get_credentials():
        """Retrieve credentials from Windows Credential Manager"""
        email = keyring.get_password(SecureConfig.SERVICE_NAME, "email")
        password = keyring.get_password(SecureConfig.SERVICE_NAME, "password")
        return email, password
    
    @staticmethod
    def clear_credentials():
        """Remove stored credentials"""
        try:
            keyring.delete_password(SecureConfig.SERVICE_NAME, "email")
            keyring.delete_password(SecureConfig.SERVICE_NAME, "password")
            print("Credentials cleared")
        except:
            print("No credentials to clear")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "store":
            SecureConfig.store_email_credentials()
        elif sys.argv[1] == "clear":
            SecureConfig.clear_credentials()
    else:
        print("Usage: python secure_config.py [store|clear]")