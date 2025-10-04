import paho.mqtt.client as mqtt
import ssl

BROKER_HOST = "tddf6216.ala.asia-southeast1.emqxsl.com"
BROKER_PORT = 8883
CLIENT_ID = "PythonSecureClient"
USERNAME = "uromed"
PASSWORD = "uromed"

CA_CERT = "emqxsl-ca.crt"          # file root CA


def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("uromed/out")


def on_message(client, userdata, msg):
    print(f"{msg.topic} => {msg.payload.decode()}")


client = mqtt.Client(client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Konfigurasi TLS
client.tls_set(ca_certs=CA_CERT,
               tls_version=ssl.PROTOCOL_TLS_CLIENT)

# Bisa tambahkan ini kalau broker pakai self-signed cert:
# client.tls_insecure_set(True)

client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()
