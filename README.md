# Password Generator

A secure password generator application that creates strong passwords based on user keywords and customizable constraint sets.

## Features

- **Keyword-Based Password Generation**: Create passwords that incorporate your personal keywords for better memorability while maintaining security.
- **Customizable Constraint Sets**: Define and save multiple sets of password generation rules.
- **Password Strength Analysis**: Get real-time feedback on password strength with detailed metrics.
- **Secure Storage**: Store your passwords with encryption and organize them by category.
- **Modern User Interface**: User-friendly interface with light and dark themes.
- **Import/Export**: Easily backup and restore your password database.

## Requirements

- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/password-generator.git
   cd password-generator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Docker Support

You can also run the application using Docker:

```
docker build -t password-generator .
docker run -p 5000:5000 password-generator
```

## Usage

### Generating Passwords

1. Enter your keywords (comma-separated) in the "Keywords" field.
2. Select a constraint set from the dropdown.
3. Click "Generate Password" to create a new password.
4. View the password strength and feedback.
5. Copy the password to clipboard or save it to the database.

### Managing Constraint Sets

1. Navigate to the "Constraints" tab.
2. Create, edit, or delete constraint sets.
3. Customize rules like length, character types, and specific included/excluded characters.

### Storing and Retrieving Passwords

1. Navigate to the "Passwords" tab to view all stored passwords.
2. Search and filter passwords by category or website.
3. View, edit, or delete stored passwords.
4. Export your password database for backup.

## Security

- All passwords are encrypted using the Fernet symmetric encryption algorithm.
- Encryption keys are stored separately from the password database.
- The application never transmits your passwords over the network.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
