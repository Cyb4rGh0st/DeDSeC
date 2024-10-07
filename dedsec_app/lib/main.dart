import 'package:cryptography/cryptography.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
Widget build(BuildContext context) {
  return MaterialApp(
    title: 'DeDSeC Communicator',
    theme: ThemeData(
      primarySwatch: Colors.grey, // Set to gray
    ),
    home: const ChatScreen(),
  );
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<String> messages = [];
  final TextEditingController _controller = TextEditingController();

  void _sendMessage() {
    if (_controller.text.isNotEmpty) {
      setState(() {
        messages.add(_controller.text);
      });
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DeDSeC Chat'),
      ),
      body: Column(
        children: <Widget>[
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(messages[index]),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(hintText: 'Enter message'),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}


// Zdefiniowanie algorytmu AES-GCM
final Cipher aesGcm = AesGcm.with256bits();

/// Funkcja generująca parę kluczy publiczny/prywatny Curve25519
Future<KeyPair> generateKeyPair() async {
  final algorithm = X25519();
  final keyPair = await algorithm.newKeyPair();
  return keyPair;
}

/// Szyfrowanie wiadomości
Future<List<int>> encryptMessage(
  String message,
  PublicKey recipientPublicKey,
  KeyPair senderKeyPair,
) async {
  final algorithm = X25519();

  // Tworzymy wspólny sekret
  final sharedSecret = await algorithm.sharedSecretKey(
    keyPair: senderKeyPair,
    remotePublicKey: recipientPublicKey,
  );

  // Szyfrowanie AES-GCM
  final secretBox = await aesGcm.encrypt(
    message.codeUnits,
    secretKey: sharedSecret,
    nonce: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], // Nonce o długości 12 bajtów
  );
  return secretBox.concatenation();
}

/// Odszyfrowanie wiadomości
Future<String> decryptMessage(
  List<int> encryptedMessage,
  PublicKey senderPublicKey,
  KeyPair recipientKeyPair,
) async {
  final algorithm = X25519();

  // Tworzymy wspólny sekret
  final sharedSecret = await algorithm.sharedSecretKey(
    keyPair: recipientKeyPair,
    remotePublicKey: senderPublicKey,
  );

  // Odszyfrowanie AES-GCM
  final secretBox = SecretBox.fromConcatenation(
    encryptedMessage,
    nonceLength: 12, // standardowa długość nonce (12 bajtów)
    macLength: 16,   // standardowa długość MAC (16 bajtów)
  );

  // Odszyfrowanie za pomocą AES-GCM
  final decrypted = await aesGcm.decrypt(
    secretBox,
    secretKey: sharedSecret,
  );

  return String.fromCharCodes(decrypted);
}
