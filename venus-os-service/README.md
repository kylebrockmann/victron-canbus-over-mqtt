Put this is our venus os service folder at /service/canmqtt
To persist after upgrades save in /data and symlink to /service/canmqtt
IE: ln -s /data/canmqtt /service/canmqtt
# Venus OS Service: canmqtt
This service reads CAN bus data for a Victron Energy system and publishes it to an MQTT broker. 
It is designed to run on Venus OS, the operating system used in Victron Energy products.
