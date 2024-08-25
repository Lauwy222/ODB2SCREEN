#define RXD2 16  // You can change these pins as needed
#define TXD2 17  // These are connected to the HC-05 TX and RX pins

void setup() {
  // Start the serial communication with the computer
  Serial.begin(115200);
  Serial.println("Enter AT commands:");
  
  // Start the serial communication with the Bluetooth module
  Serial2.begin(38400, SERIAL_8N1, RXD2, TXD2);  // HC-05 default baud rate in AT command mode
  delay(1000);

  // Configure HC-05 using AT commands
  // sendATCommand("AT+RESET", "OK");
  // sendATCommand("AT+ORGL", "OK");
  sendATCommand("AT+ROLE=1", "OK");          // Set to Master
  sendATCommand("AT+CMODE=0", "OK");         // Connect to a specific address
  sendATCommand("AT+BIND=1234,56,789c72", "OK"); // Bind to ELM327 MAC address
  sendATCommand("AT+INIT", "OK");
  sendATCommand("AT+PAIR=1234,56,789c72,20", "OK"); // Pair with ELM327
  sendATCommand("AT+LINK=1234,56,789c72", "OK"); // Link to ELM327
}

void loop() {
  // Keep checking for responses from the HC-05
  if (Serial2.available()) {
    Serial.write(Serial2.read());
  }
  if (Serial.available()) {
    Serial2.write(Serial.read());
  }
}

void sendATCommand(String command, String expectedResponse) {
  Serial.print("Sending: ");
  Serial.println(command);
  Serial2.println(command);
  delay(1000); // Wait for response
  String response = "";
  while (Serial2.available()) {
    char c = Serial2.read();
    response += c;
  }
  Serial.print("Response: ");
  Serial.println(response);
  if (response.indexOf(expectedResponse) == -1) {
    Serial.println("Error in response");
  }
}
