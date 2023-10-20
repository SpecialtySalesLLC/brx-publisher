from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json
import os
from random import choice, randint, uniform

received_all_event = threading.Event()

thing_name = 'dev-iot-device-1'
device_id = '1234567890'
mac_address = '12345678Afghfhg'
frequency = 10

pub_topic = 'brx/data'
cert_filepath = './DeviceCertificate.pem'
private_key_filepath = './private.pem'
ca_filepath = './AmazonRootCA1.pem'

target_ep = 'a1brrzwqiohmvf-ats.iot.us-east-2.amazonaws.com'
type_list = ['valves', 'sensors']
location_list = ['system', 'lane1', 'lane2', 'lane2', 'lane3', 'lane4']
valves_name_list = ['main_water', 'main_drain', 'chem1',
                    'chem2', 'bath', 'fill', 'drain', 'flash', 'air_blow', 'pod']
sensors_name_list = ['water_meter', 'temperature',
                     'chem1_level', 'chem2_level', 'pod_level']

# Callback when connection is accidentally lost.


def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

# Callback when an interrupted connection is re-established.


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(
        return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

# Callback when the subscribed topic receives a message


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))


def subscribe_topic():
    print("Subscribing to topic " + pub_topic)
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=pub_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)
    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))


def get_random_message():
    message = {
        'device_name': thing_name,
        'device_id': device_id,
        'mac_address': mac_address,
        'message_type': choice(type_list),
        'location': choice(location_list),
        'name': choice(valves_name_list) if type == 'valves' else choice(sensors_name_list),
        'state': randint(0, 1) if type == 'valves' else uniform(0.00, 1000.00),
        'time_reading': time.time()
    }
    return message


def publish_random_messages():
    message = get_random_message()
    print('Publishing message on topic {}'.format(pub_topic))
    message_json = json.dumps(message)
    mqtt_connection.publish(
        topic=pub_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE)


# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

proxy_options = None

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=target_ep,
    port=8883,
    cert_filepath=cert_filepath,
    pri_key_filepath=private_key_filepath,
    client_bootstrap=client_bootstrap,
    ca_filepath=ca_filepath,
    on_connection_interrupted=on_connection_interrupted,
    on_connection_resumed=on_connection_resumed,
    client_id=thing_name,
    clean_session=True,
    keep_alive_secs=30,
    http_proxy_options=proxy_options)

print("Connecting to {} with client ID '{}'...".format(
    target_ep, thing_name))

# Connect to the gateway
while True:
    try:
        connect_future = mqtt_connection.connect()
        # Future.result() waits until a result is available
        connect_future.result()
    except:
        print("Connection to IoT Core failed...  retrying in 5s.")
        time.sleep(5)
        continue
    else:
        print("Connected!")
        break

# Subscribe then publish
while True:
    publish_random_messages()
    time.sleep(frequency)
