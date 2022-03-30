#define relay_lna 7
#define relay_dgen 4
int conn = 2;

void setup() {
  Serial.begin(9600);

  pinMode(relay_lna, OUTPUT);
  pinMode(relay_dgen, OUTPUT);

  digitalWrite(relay_lna, LOW);
  digitalWrite(relay_dgen, LOW);
}

void loop() {
  if (Serial.available()) {
    conn = Serial.read();
    //Serial.println(conn, BIN);
    if (conn == 2) {
      Serial.write("Switching to LNA\n");
      digitalWrite(relay_lna, HIGH);
      digitalWrite(relay_dgen, LOW);
    } else if (conn == 1) {
      Serial.write("Switching to Delay Generator\n");
      digitalWrite(relay_lna, LOW);
      digitalWrite(relay_dgen, HIGH);
    } else {
      Serial.write("Switching to open\n");
      digitalWrite(relay_lna, LOW);
      digitalWrite(relay_dgen, LOW);
    }

    Serial.write(conn);
  }
}
