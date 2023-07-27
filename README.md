# APIprod by Harrison Getches

## Overview

APIprod is a Flask-based web application that allows users to login, query various APIs, and save encrypted API keys to their account. The application provides a user-friendly interface for users to access different types of APIs and retrieve the data they need.

Users can query the Osu! API, which is the official API for a video game, and pull statistics of users or maps that have been recently ranked. They can also access the OpenAI API to use artificial intelligence to generate completions or summaries based on text, images, or talk to a chatbot.

Additionally, the app allows users to query various APIs and save encrypted API keys to their account, and query any API using their own endpoint and saved key using multiple methods. This feature allows users to easily access different types of APIs without having to re-enter their API key each time they want to make a request.

The application uses Sqlite3 as the back-end database, which stores user information, and their encrypted keys. Keys are encrypted using Fernet, a symmetric encryption algorithm that utilizes a secret key stored for each user in an INI file. This ensures that the keys are stored securely and can only be accessed by authorized users.

APIprod also has a built-in support for a dark mode and a light mode, which allows users to choose the theme that is most comfortable for them. It also sources images from Unsplash.com and Wikipedia, which adds a visually appealing aspect to the application.

Moreover, the application also has a feature that allows users to generate API keys for their own endpoints, and save them securely in their account. This feature is particularly useful for users who have multiple API endpoints to access, and do not want to have to keep track of multiple API keys.

In addition to the features mentioned above, APIprod also provides additional functionality such as password hashing and checking, session handling, and regular expression handling. These functionalities are implemented using libraries such as Werkzeug, tempfile, Flask-Session, CS50, Re, ConfigParser, and Secrets.

With a user-friendly interface and built-in security features, APIprod is an ideal tool for developers, data scientists, and other professionals who need to access various APIs in their work.

### Prerequisites

- Python 3.11.1
- Flask
- requests
- Werkzeug
- tempfile
- Flask-Session
- CS50
- Re
- ConfigParser
- Secrets
- Datetime
- Base64
- Cryptography
- SQLite3
- OpenAI and Osu! API keys; in system variables called API_KEY and OSU_API_KEY, respectively

## API Usage

The app allows users to query the Osu! api (a video games official API), and pull users stats, or the maps that have been recently ranked (at /osu); as well as the OpenAI API to use artificial intelligence to generate completions or summaries based on text, images, or talk to a chatbot (at /completions, /summary, /generate_image, and /chatbot, respectively).
Additionally, the app allows users to query various APIs and save encrypted API keys to their account (on index.html), and query any API using their own endpoint and saved key using multiple methods (on /any-api.html). To use these APIs, you must provide your own API key and endpoint. The app will encrypt the keys using a secret key within an INI file, so that it can be decrypted and used later.

## Flask App Usage

1. Ensure all prerequisites are installed
2. Create a config.ini file within the app directory, and leave it empty.
3. Store API keys using ```export API_KEY="yourOpenAIKEY"``` and ```export API_KEY_OSU="yourOsuKEY"```
4. Run the App using ```python3 -m flask run```

### Additional Information

- This app uses Werkzeug library for password hashing and checking, as well as tempfile library to create a temporary directory.
- Flask-Session is used to handle sessions in the app.
- CS50 library is used for accessing SQLite3 database.
- Re library is used for regular expressions.
- ConfigParser is used to read and write configuration files.
- Secrets library is used to generate cryptographically-secure random numbers.
- Datetime and timedelta are used to handle datetime objects.
- Base64 and Fernet from cryptography library are used for encryption and decryption.

### Video Demo:  <https://youtu.be/HMcTAVuoyHw>

## Contact

If you have any issues or questions, please contact me at <harrison.getches@colorado.edu>
