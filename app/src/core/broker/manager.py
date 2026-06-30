from faststream.rabbit.fastapi import RabbitRouter

rabbit_router = RabbitRouter("amqp://rabbitmq:5672/")
rabbit_broker = rabbit_router.broker
