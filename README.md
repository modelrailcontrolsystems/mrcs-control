# mrcs-control

_The Model Rail Control Systems (MRCS) commander_

---

### Repos

Requires MRCS repos:

* **[mrcs-core](https://github.com/modelrailcontrolsystems/mrcs-core)**

---

### Services

Before running services, optionally clear the messaging queues (in case of incorrect routings):

* `mrcs_control_broker --verbose --queue --erase --test &`

The following backend services should be running continuously:

* `mrcs_control_clock_service --verbose --subscribe &`
* `mrcs_control_cron_service --verbose --clean --run-save &`
* `mrcs_control_crontab_service --verbose --subscribe &`
* `mrcs_control_mpu_service --verbose --drain --run &`
* `mrcs_control_recorder_service --verbose --drain --clean --subscribe &`
* `mrcs_control_router_service --verbose --run &`
* `mrcs_control_track_service --verbose --drain --run &`

The following service supports the MRCS APIs:

* `mrcs_api_uvicorn_service --verbose --reload &`

---

### Prolog

The MRCS route planner is written in the open source [SWI-Prolog](https://www.swi-prolog.org/) language.

The interpreter is started and stopped automatically. Only one interpreter may run
in a process; this is managed by the MRCS software.

SWI-Prolog is distributed under the
[Simplified BSD license](https://github.com/SWI-Prolog/swipl-devel/blob/master/LICENSE).

---

### RabbitMQ

[The Homebrew RabbitMQ Formula](https://www.rabbitmq.com/docs/install-homebrew)

#### Operations

RabbitMQ must be running on the host. Install and run (permanently) with the following:

`
brew install rabbitmq
`

`
brew services restart rabbitmq
`

`
rabbitmqctl enable_feature_flag all
`

[Deleting queues in RabbitMQ](https://stackoverflow.com/questions/6742938/deleting-queues-in-rabbitmq)

`
channel.queue_delete(queue='queue-name')
`

[How can I list or discover queues on a RabbitMQ exchange using python?](https://stackoverflow.com/questions/4287941/how-can-i-list-or-discover-queues-on-a-rabbitmq-exchange-using-python)

`
def rest_queue_list ...
`

#### Monitoring

`
rabbitmqctl list_queues name messages_ready messages_unacknowledged
`

---

