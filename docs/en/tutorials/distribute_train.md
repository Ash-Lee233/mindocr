# Distributed parallel training

This document provides a tutorial on distributed parallel training.
There are three ways to train on the Ascend AI processor: by running scripts with MSRun or OpenMPI or configuring `RANK_TABLE_FILE` for training. Refer to [MindSpore Distributed Parallel Startup Methods](https://www.mindspore.cn/docs/en/master/model_train/parallel/startup_method.html) for more details.

> Please ensure that the `distribute` parameter in the yaml file is set to `True` before running the following commands for distributed training.

## Ascend

**Notes**:

On Ascend platform, some common restrictions on using the distributed service are as follows:

- In a single-node system, a cluster of 1, 2, 4, or 8 devices is supported. In a multi-node system, a cluster of 8 x N devices is supported.

- Each host has four devices numbered 0 to 3 and four devices numbered 4 to 7 deployed on two different networks. During training of 2 or 4 devices, the devices must be connected and clusters cannot be created across networks. This means, when training with 4 devices, only `{0, 1, 2, 3}` and  `{4, 5, 6, 7}` are available. While in training with 2 devices, devices cross networks, such as `{0, 4}` are not allowed. However, devices within networks, such as `{0, 1}`or `{1, 2}`, are allowed.

### Run scripts with MSRun

On Ascend hardware platform, users can use MindSpore's `msrun` to run distributed training with `n` devices. For example, in [DBNet Readme](https://github.com/mindspore-lab/mindocr/blob/main/configs/det/dbnet/README.md#34-training), the following command is used to train the model on devices `0` and `1`:

```shell
# worker_num is the total number of Worker processes participating in the distributed task.
# local_worker_num is the number of Worker processes pulled up on the current node.
# The number of processes is equal to the number of NPUs used for training. In the case of single-machine multi-card worker_num and local_worker_num must be the same.
msrun --worker_num 2 --local_worker_num 2 tools/train.py --config configs/det/dbnet/db_r50_icdar15.yaml
```

> Note that `msrun` will run training on sequential devices starting from device `0`. For example, `msrun --worker_num 4 --local_worker_num 4 start-scriptd` will run training on the four devices: `{0, 1, 2, 3}`.

### Run scripts with OpenMPI

On Ascend hardware platform, users can use OpenMPI's `mpirun` to run distributed training with `n` devices. For example, in [DBNet Readme](https://github.com/mindspore-lab/mindocr/blob/main/configs/det/dbnet/README.md#34-training), the following command is used to train the model on devices `0` and `1`:

```shell
# n is the number of NPUs used in training
mpirun --allow-run-as-root -n 2 python tools/train.py --config configs/det/dbnet/db_r50_icdar15.yaml
```

> Note that `mpirun` will run training on sequential devices starting from device `0`. For example, `mpirun -n 4 python-command` will run training on the four devices: `{0, 1, 2, 3}`.

### Configure RANK_TABLE_FILE for training

> Note that rank_table method will be deprecated in MindSpore 2.4 version.

#### Running on Eight (All) Devices

Before using this method for distributed training, it is necessary to create an HCCL configuration file in json format,
i.e. generate RANK_TABLE_FILE. The following is the command to generate the corresponding configuration file for 8 devices
(for more information please refer to [HCCL tools](https://gitee.com/mindspore/models/tree/master/utils/hccl_tools)):

```shell
python hccl_tools.py --device_num "[0,8)"
```
This command produces the following output file:
```
hccl_8p_10234567_127.0.0.1.json
```

An example of the content in `hccl_8p_10234567_127.0.0.1.json`:

```json
{
    "version": "1.0",
    "server_count": "1",
    "server_list": [
        {
            "server_id": "127.0.0.1",
            "device": [
                {
                    "device_id": "0",
                    "device_ip": "192.168.100.101",
                    "rank_id": "0"
                },
                {
                    "device_id": "1",
                    "device_ip": "192.168.101.101",
                    "rank_id": "1"
                },
                {
                    "device_id": "2",
                    "device_ip": "192.168.102.101",
                    "rank_id": "2"
                },
                {
                    "device_id": "3",
                    "device_ip": "192.168.103.101",
                    "rank_id": "3"
                },
                {
                    "device_id": "4",
                    "device_ip": "192.168.100.100",
                    "rank_id": "4"
                },
                {
                    "device_id": "5",
                    "device_ip": "192.168.101.100",
                    "rank_id": "5"
                },
                {
                    "device_id": "6",
                    "device_ip": "192.168.102.100",
                    "rank_id": "6"
                },
                {
                    "device_id": "7",
                    "device_ip": "192.168.103.100",
                    "rank_id": "7"
                }
            ],
            "host_nic_ip": "reserve"
        }
    ],
    "status": "completed"
}
```

Then start the training by running the following command:

```shell
bash ascend8p.sh
```

> Please ensure that the `distribute` parameter in the yaml file is set to `True` before running the command.

Here is an example of the `ascend8p.sh` script for CRNN training:

```shell
#!/bin/bash
export DEVICE_NUM=8
export RANK_SIZE=8
export RANK_TABLE_FILE="./hccl_8p_01234567_127.0.0.1.json"

for ((i = 0; i < ${RANK_SIZE}; i++)); do
    export DEVICE_ID=$i
    export RANK_ID=$i
    echo "Launching rank: ${RANK_ID}, device: ${DEVICE_ID}"
    if [ $i -eq 0 ]; then
      echo 'i am 0'
      python -u tools/train.py --config configs/rec/crnn/crnn_resnet34_zh.yaml &> ./train.log &
    else
      echo 'not 0'
      python -u tools/train.py --config configs/rec/crnn/crnn_resnet34_zh.yaml &> /dev/null &
    fi
done
```
When training other models, simply replace the yaml config file path in the script, i.e. `path/to/model_config.yaml`.

After the training has started, and you can find the training log `train.log` in the project root directory.

#### Running on Four (Partial) Devices

To run training on four devices, for example, `{4, 5, 6, 7}`, the `RANK_TABLE_FILE` and the run script are different from those for running on eight devices.

The `rank_table.json` is created by running the following command:

```shell
python hccl_tools.py --device_num "[4,8)"
```

This command produces the following output file:
```
hccl_4p_4567_127.0.0.1.json
```

An example of the content in `hccl_4p_4567_127.0.0.1.json`:

```json
{
    "version": "1.0",
    "server_count": "1",
    "server_list": [
        {
            "server_id": "127.0.0.1",
            "device": [
                {
                    "device_id": "4",
                    "device_ip": "192.168.100.100",
                    "rank_id": "0"
                },
                {
                    "device_id": "5",
                    "device_ip": "192.168.101.100",
                    "rank_id": "1"
                },
                {
                    "device_id": "6",
                    "device_ip": "192.168.102.100",
                    "rank_id": "2"
                },
                {
                    "device_id": "7",
                    "device_ip": "192.168.103.100",
                    "rank_id": "3"
                }
            ],
            "host_nic_ip": "reserve"
        }
    ],
    "status": "completed"
}
```

Then start the training by running the following command:

```shell
bash ascend4p.sh
```

Here is an example of the `ascend4p.sh` script for CRNN training:

```shell
#!/bin/bash
export DEVICE_NUM=8
export RANK_SIZE=4
export RANK_TABLE_FILE="./hccl_4p_4567_127.0.0.1.json"

for ((i = 0; i < ${RANK_SIZE}; i++)); do
    export DEVICE_ID=$((i+4))
    export RANK_ID=$i
    echo "Launching rank: ${RANK_ID}, device: ${DEVICE_ID}"
    if [ $i -eq 0 ]; then
      echo 'i am 0'
      python -u tools/train.py --config configs/rec/crnn/crnn_resnet34_zh.yaml &> ./train.log &
    else
      echo 'not 0'
      python -u tools/train.py --config configs/rec/crnn/crnn_resnet34_zh.yaml &> /dev/null &
    fi
done
```

Note that the `DEVICE_ID` and `RANK_ID` should be matched with `hccl_4p_4567_127.0.0.1.json`.
