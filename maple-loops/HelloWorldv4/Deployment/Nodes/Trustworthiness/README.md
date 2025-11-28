https://github.com/INTO-CPS-Association/robosapiens-trustworthiness-checker/wiki/Docker-Service-Instructions

1. run the very simpel example: 
```bash
sudo docker run --network host -it thomasdwright/trustworthiness-checker:latest /opt/trustworthiness-checker/examples/simple_add.lola --input-mqtt-topics x y --output-mqtt-topics z
```
2. run the different boolean stream example:

```bash
docker run --network host -v ./host_models:/mnt/host_models -it thomasdwright/trustworthiness-checker:latest /mnt/host_models/maple_simple_seq.lola --input-file /mnt/host_models/maple_sequence_true.input --output-stdout
```
3. run single shared stream example:

```bash
docker run --network host -v ./host_models:/mnt/host_models -it thomasdwright/trustworthiness-checker:latest /mnt/host_models/maple_simple_single_topic.lola --input-file /mnt/host_models/maple_sequence_single_topic.input --output-stdout
```
4. run single shared stream example using mqtt:

```bash
docker run --network host -v ./host_models:/mnt/host_models -it thomasdwright/trustworthiness-checker:latest /mnt/host_models/maple_simple_single_topic.lola --input-mqtt-topics stage --output-mqtt-topics m a p l e maple 
```
