# Simple Website Lock
Creates a very simple, embeddable, password protected lock to hide a small amount of content, ideal for digital breakouts in the classroom. Made with Flask, Firebase Realtime Database, and Bulma.

**This tool is not secure enough to be used in any serious security-focused setting. Use with caution.** 

## How it works
### Storing your data
The password that you enter is used to encode your hidden content using a Vigenère cipher, which should not be used for any security applications. However, for short messages it is virtually unbreakable. The password is then hashed using MD5, and stored with the enoded content in the database.

### Checking password
The user's password attempt is hashed and checked against the hashed password stored in the database. If they match, then the user's attempt is valid, and therefore can be used to decode the content (using the Vigenère cipher).