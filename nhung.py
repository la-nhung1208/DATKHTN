import ssl
import serial
import paho.mqtt.client as mqtt
import time
import board
import adafruit_bh1750
import Adafruit_DHT
import RPi.GPIO as GPIO

dht_sensor = Adafruit_DHT.DHT11
dht_pin = 4

i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)

relay1_pin = 17
relay2_pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay1_pin, GPIO.OUT)
GPIO.setup(relay2_pin, GPIO.OUT)
GPIO.output(relay1_pin, GPIO.HIGH)
GPIO.output(relay2_pin, GPIO.HIGH)

mqtt_host = "79965c95be5248e8a61185e66bf3c38f.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_username = "lanhung"
mqtt_password = "Lanhung2002"
mqtt_topic = "dulieumqtt"

mqtt_client = mqtt.Client()
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.connect(mqtt_host, mqtt_port)

def on_message(client, userdata, message):
    if message.topic == "relay1" and message.payload.decode() == "1":
        GPIO.output(relay1_pin, GPIO.HIGH)
        print("Relay 1 da tat")
    elif message.topic == "relay1" and message.payload.decode() == "0":
        GPIO.output(relay1_pin, GPIO.LOW)
        print("Relay 1 da bat")
    elif message.topic == "relay2" and message.payload.decode() == "1":
        GPIO.output(relay2_pin, GPIO.HIGH)
        print("Relay 2 da tat")
    elif message.topic == "relay2" and message.payload.decode() == "0":
        GPIO.output(relay2_pin, GPIO.LOW)
        print("Relay 2 da bat")

def main():
    uart = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)  

    mqtt_client.on_message = on_message
    mqtt_client.subscribe("relay1")
    mqtt_client.subscribe("relay2")
    mqtt_client.loop_start()

    while True:
        try:
      
            uart_data = uart.readline().decode('utf-8').strip()
            uart.flushInput() 

            if uart_data:
                soil_moisture = round(float(uart_data), 2)  

                humidity_dht, temperature_dht = Adafruit_DHT.read_retry(dht_sensor, dht_pin)

       
                lux = round(bh1750.lux, 2)

                print(f"Nhiet do DHT11: {temperature_dht} C, Do am DHT11: {humidity_dht} %, Do am dat: {soil_moisture} %, Cuong do anh sang: {lux} Lux")

             
                payload = f'{{"temperature": {temperature_dht}, "humidity": {humidity_dht}, "soil_moisture": {soil_moisture}, "lux": {lux}}}'
                mqtt_client.publish(mqtt_topic, payload)

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

if __name__ == "__main__":
    main()
