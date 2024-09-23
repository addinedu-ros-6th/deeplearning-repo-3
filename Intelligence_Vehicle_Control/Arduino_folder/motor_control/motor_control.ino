#include <Encoder.h>
#define L_MOTOR_IN1 10
#define L_MOTOR_IN2 11
#define L_MOTOR_PWM 12

#define R_MOTOR_IN1 7
#define R_MOTOR_IN2 8
#define R_MOTOR_PWM 13

#define MOTOR_STBY 9// 모터 스탠바이 핀

#define L_ENC_A 2   // 왼쪽 모터 엔코더 핀 A
#define L_ENC_B 22   // 왼쪽 모터 엔코더 핀 B
#define R_ENC_A 3   // 오른쪽 모터 엔코더 핀 A
#define R_ENC_B 23   // 오른쪽 모터 엔코더 핀 B

int motorSpeed = 100;// 기본 모터 속도 (0~255)

Encoder leftEncoder(L_ENC_A, L_ENC_B);
Encoder rightEncoder(R_ENC_A, R_ENC_B);

long leftEncoderValue = 0;
long rightEncoderValue = 0;
char motorState = 'S'; // 기본 모터 상태는 정지

int right_motor_correction = 5;

unsigned long previousMillis = 0;
unsigned long currentMillis = 0;
long interval = 500;

void setup() 
{
    // 모터 핀 설정
    pinMode(L_MOTOR_IN1, OUTPUT);
    pinMode(L_MOTOR_IN2, OUTPUT);
    pinMode(L_MOTOR_PWM, OUTPUT);

    pinMode(R_MOTOR_IN1, OUTPUT);
    pinMode(R_MOTOR_IN2, OUTPUT);
    pinMode(R_MOTOR_PWM, OUTPUT);

    pinMode(MOTOR_STBY, OUTPUT);
    digitalWrite(MOTOR_STBY, HIGH);    // 모터 스탠바이 해제

    Serial.begin(9600);    // 시리얼 통신 시작
}
void loop() 
{
    currentMillis = millis();
    if (Serial.available() > 0) 
    {
        String input = Serial.readStringUntil('\n'); // 시리얼 입력 읽기
        char command = input.charAt(0); // 첫 번째 문자는 명령어
        int speed = input.substring(1).toInt(); // 그 이후는 속도 값
        if (speed > 0 && speed <= 255 && command != 'C') 
        {
            motorSpeed = speed; // 새로운 속도 값 설정
        }
        if (command == 'F') 
        {
            // 모터 전진
            digitalWrite(L_MOTOR_IN1, LOW);
            digitalWrite(L_MOTOR_IN2, HIGH);
            analogWrite(L_MOTOR_PWM, motorSpeed);
            // 설정된 속도로 모터 전진
            digitalWrite(R_MOTOR_IN1, HIGH);
            digitalWrite(R_MOTOR_IN2, LOW);
            analogWrite(R_MOTOR_PWM, motorSpeed+right_motor_correction);
        }
        else if (command == 'B') 
        {
            // 모터 후진
            digitalWrite(L_MOTOR_IN1, HIGH);
            digitalWrite(L_MOTOR_IN2, LOW);
            analogWrite(L_MOTOR_PWM, motorSpeed);
            // 설정된 속도로 모터 후진
            digitalWrite(R_MOTOR_IN1, LOW);
            digitalWrite(R_MOTOR_IN2, HIGH);
            analogWrite(R_MOTOR_PWM, motorSpeed+right_motor_correction);
        }
        else if (command == 'T') 
        {// 제자리 좌회전
            // 모터 후진
            digitalWrite(L_MOTOR_IN1, HIGH);
            digitalWrite(L_MOTOR_IN2, LOW);
            analogWrite(L_MOTOR_PWM, motorSpeed);
            // 설정된 속도로 모터 전진
            digitalWrite(R_MOTOR_IN1, HIGH);
            digitalWrite(R_MOTOR_IN2, LOW);
            analogWrite(R_MOTOR_PWM, motorSpeed+right_motor_correction);
        }
        else if (command == 'S') 
        {
            // 모터 정지
            analogWrite(L_MOTOR_PWM, 0);
            analogWrite(R_MOTOR_PWM, 0);
        }
        else if (command == 'C')
        {
            right_motor_correction = speed;
        }
        else if (command == 'E')
        {
            // 엔코더 값 초기화
            leftEncoder.write(0);
            rightEncoder.write(0);
        }
    }
    if (currentMillis - previousMillis >interval)
    {
        // 엔코더 값 읽기
        leftEncoderValue = leftEncoder.read();
        rightEncoderValue = rightEncoder.read();

        // 엔코더 값 시리얼로 전송
        // Serial.print("L:");
        // Serial.print(leftEncoderValue);
        // Serial.print(" R:");
        // Serial.println(rightEncoderValue);
        Serial.print("L - R:");
        Serial.println(leftEncoderValue+rightEncoderValue);
        previousMillis = currentMillis;
        // delay(100);    // 0.1초마다 엔코더 값 전송
    }
    
}