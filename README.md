# mrcs-control
_The Model Rail Control Systems (MRCS) commander_

---

### Repos

Requires MRCS repos:
* **[mrcs-core](https://github.com/modelrailcontrolsystems/mrcs-core)**

---

### Services

Before running services, optionally clear the messaging queues (in case of incorrect routings):
* `mrcs_broker --verbose --queue --erase --test &`

The following services should be running continuously:
* `mrcs_clock_manager --verbose --subscribe --test &`
* `mrcs_cron --verbose --run-save --test &`
* `mrcs_crontab --verbose --subscribe --test &`
* `mrcs_recorder --verbose --subscribe --test &`

---

### RabbitMQ

[The Homebrew RabbitMQ Formula](https://www.rabbitmq.com/docs/install-homebrew)

#### Operations
`
brew services restart rabbitmq
`
`
/usr/local/opt/rabbitmq/sbin/rabbitmqctl enable_feature_flag all
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

