from workers.tasks import test_worker


def main():

    result = test_worker.delay()

    print("Task submitted successfully.")
    print("Task ID:", result.id)
    print("Initial status:", result.status)

    print("Waiting for result...")

    print(result.get(timeout=30))

    print("Final status:", result.status)


if __name__ == "__main__":
    main()