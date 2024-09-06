# SecureChat-P2P

Welcome to **SecureChat-P2P**, a peer-to-peer chat application designed with your privacy in mind. This application ensures that your conversations remain private and secure through advanced encryption techniques.

## Features

- **👥 Private Chats:** Connect with others in secure, private chat rooms.
- **🔒 End-to-End Encryption:** All messages are encrypted on your device and can only be decrypted by your chat partner. No one, not even us, can read your messages.
- **🔗 Peer-to-Peer:** Enjoy direct connections between users without intermediary servers.
- **🔐 Advanced Encryption:** Uses RSA and symmetric key encryption to protect your communications.
- **💾 No Data Storage:** Conversations are not stored on our servers. Once a chat room is closed, all data is permanently deleted.

## Installation

- From Python Src
    1. **Install dependencies**
        - install dependencies using `pip install -r requirements.txt`

    2. **Run Python File**
       - run python source files using `python app.py`

- From Executable
    1. **Download the Executable:**
       - Get the Windows executable from the [latest release](https://github.com/thefcraft/SecureChat-P2P/releases/tag/v0.0.2-alpha).

    2. **Run the Installer:**
       - Open the downloaded `.exe` file and follow the installation instructions.

- Setup:
  - Once installed, open the application and start a new chat or join an existing chat room using the generated room code.

## Usage

1. **Starting a New Chat:**
   - Open the application and select "Start New Chat."
   - Generate a room code and share it with your chat partner.

2. **Joining an Existing Chat:**
   - Open the application and select "Join Existing Chat."
   - Enter the room code provided by your chat partner.

3. **Ending a Chat:**
   - Close the chat room window to ensure all data is permanently deleted.

## Img

![HOME PAGE](/img/home.png)

![CREATE PAGE](/img/create.png)

![CHAT PAGE](/img/chat.png)

## Important Notes

- **Handshake Server:** If no user activity is detected, the handshake server will enter sleep mode. Allow 30 to 60 seconds for the server to wake up and generate a room code.

- **Encryption Details:** SecureChat-P2P uses RSA encryption for secure key exchange and symmetric key encryption for securing message content.

## Contributing

We welcome contributions to improve SecureChat-P2P! To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and test thoroughly.
4. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please open an issue on this repository or contact us via [email](mailto:sisodiyalaksh@gmail.com).
