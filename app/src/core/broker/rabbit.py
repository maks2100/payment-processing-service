from faststream.rabbit.fastapi import RabbitRouter, RabbitBroker

router = RabbitRouter("amqp://rabbitmq:5672/")
broker = router.broker


def get_broker() -> RabbitBroker:
    return broker


# async def declare_queues(broker: RabbitBroker) -> None:
#     await broker.declare_exchange(
#         RabbitExchange("payments_exchange", type=ExchangeType.TOPIC, durable=True)
#     )

#     await broker.declare_queue(
#         RabbitQueue("payments_new", durable=True, routing_key="payments.new")
#     )

#     await broker.declare_queue(
#         RabbitQueue("payments_dlq", durable=True, routing_key="payments.dlq")
#     )
