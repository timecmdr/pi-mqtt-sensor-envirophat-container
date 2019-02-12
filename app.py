# This code has both the publish and the subscribe callbacks implemented
import paho.mqtt.client as mqttClient
import time
import json
import ssl
import base64
from envirophat import light, motion, weather, leds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:
        print("Connection failed")

def on_publish(client, userdata, result):
        print ("Published!")

def on_message(client, userdata, message):
    print ("New message received!")
    print ("Topic: ", message.topic)
    print ("Message: ", str(message.payload.decode("utf-8")))

Connected = False
broker_address= "10.0.110.51" # Should be the Nutanix edge IP address
port = 1883
topic = "home/garage/envirophat"

client = mqttClient.Client()
# Set callbacks for connection event, publish event and message receive event
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.tls_set(ca_certs="certs/ca.crt", certfile="certs/mqtt-client.crt", keyfile="certs/mqtt-client.key", cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
# Set this to ignore hostname only. TLS is still valid with this setting.
client.tls_insecure_set(True)
client.connect(broker_address, port=port)
client.subscribe(topic)
client.loop_start()

while Connected != True:    #Wait for connection
    print ("Connecting...")
    time.sleep(1)

try:
    while True:
        lux = light.light()
        leds.on() # shows a reading has been taken
        rgb = str(light.rgb())[1:-1].replace(' ', '')
        leds.off()
        acc = str(motion.accelerometer())[1:-1].replace(' ', '')
        heading = motion.heading()
        temp = weather.temperature()
        press = weather.pressure()
        values = {
            "temp": temp,
            "pressure": press,
            "heading": heading,
            "accelerometer": acc,
            "light_level": lux,
            "light_colour": rgb
        }

        json_output = json.dumps(values)
        client.publish(topic, json_output)
        time.sleep(5)

except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()
    leds.off()
