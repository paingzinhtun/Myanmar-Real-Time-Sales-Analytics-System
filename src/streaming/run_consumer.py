from src.streaming.consumer import SalesStreamConsumer


def main() -> None:
    consumer = SalesStreamConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
