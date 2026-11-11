int road1_red = 3;
int road1_yellow = 4;
int road1_green = 5;

int road2_red = 6;
int road2_yellow = 7;
int road2_green = 8;

String receivedData = "";

void setup() {
    Serial.begin(9600);
    pinMode(road1_red, OUTPUT);
    pinMode(road1_yellow, OUTPUT);
    pinMode(road1_green, OUTPUT);
    pinMode(road2_red, OUTPUT);
    pinMode(road2_yellow, OUTPUT);
    pinMode(road2_green, OUTPUT);
    
    setRoadState(1, 'G'); // Start with Road 1 green, Road 2 red
    setRoadState(2, 'R');
}

void loop() {
    while (Serial.available() > 0) {
        char c = Serial.read();
        receivedData += c;

        if (receivedData.length() >= 2) {
            int road = receivedData[1] - '0';
            char signal = receivedData[0];
            setRoadState(road, signal);
            receivedData = "";
        }
    }
}

void setRoadState(int road, char state) {
    int redPin = (road == 1) ? road1_red : road2_red;
    int yellowPin = (road == 1) ? road1_yellow : road2_yellow;
    int greenPin = (road == 1) ? road1_green : road2_green;

    if (state == 'R') {
        digitalWrite(redPin, HIGH);
        digitalWrite(yellowPin, LOW);
        digitalWrite(greenPin, LOW);
    } else if (state == 'Y') {
        digitalWrite(redPin, LOW);
        digitalWrite(yellowPin, HIGH);
        digitalWrite(greenPin, LOW);
    } else if (state == 'G') {
        digitalWrite(redPin, LOW);
        digitalWrite(yellowPin, LOW);
        digitalWrite(greenPin, HIGH);
    }
}
