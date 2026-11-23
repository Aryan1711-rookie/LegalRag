from database.redis_client import redis_client, check_redis_connection

def main():
    print("Checking Redis connection...")

    if check_redis_connection():
        print("Redis connection successful!")

    redis_client.set("legalmind:test", "LegalMind is working!", ex=60)

    print(redis_client.get("legalmind:test"))

    redis_client.delete("legalmind:test")

if __name__ == "__main__":
    main()
