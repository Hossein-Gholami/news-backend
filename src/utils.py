import asyncio
import pymongo
from fastapi import FastAPI
from typing import Callable

from src.bus import MessageBus


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        try:
            bus = MessageBus()
            app._bus = bus
            app._db_client = bus.db_client
            app._db = bus.db
            # await bus.db.drop_collection("news")
            # await bus.db.create_collection("news")
            await bus.db["news"].create_index([("time", pymongo.DESCENDING)], background=True)
            app._redis_consumer_task = asyncio.create_task(app._bus.redis_consumer.start())
            app._bus.scheduler.add_crawler_task()
            asyncio.create_task(app._bus.scheduler.engine.serve())
            # asyncio.create_task(asyncio.to_thread(app._bus.scheduler.engine.run))
        except Exception as e:
            print(f"error in app startup. {e}")
            raise SystemExit(1)
        # else:
        #     print("App startup complete.")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    def stop_app() -> None:
        try:
            app._bus.scheduler.engine.session.shut_down()
            app._redis_consumer_task.cancel()
            app._db_client.close()
        except Exception as e:
            print(f"error in app shutdown. {e}")
        # else:
        #     print("App shutdown complete.")
    
    return stop_app


# # ALSO REDIS
# redis_conf = config.redis
# redis_conn = Redis(
#     host=redis_conf.host,
#     port=redis_conf.port,
#     db=redis_conf.db,
#     password=redis_conf.password,
#     decode_responses=True,
#     encoding="utf-8",
# )
# app.redis = redis_conn
# app.redis_consumer_task = None

# @app.on_event("startup")
# def startup_event():
#     # mongo_conf = config.mongodb
#     # mongo_conn_str = f"mongodb://{mongo_conf.user}:{mongo_conf.password}@{mongo_conf.host}:{mongo_conf.port}"
#     # app.mongodb_client = MongoClient(mongo_conn_str)
#     # app.database = app.mongodb_client[mongo_conf.db]
#     # print("Connected to the MongoDB database! brilliant...")
#     ##########
#     # app.redis_consumer_task = asyncio.create_task(redis_consumer(app))
#     ...

# @app.on_event("shutdown")
# def shutdown_event():
#     app.mongodb_client.close()
#     # try:
#     #     app.redis_consumer_task.cancel()
#     # except Exception as e:
#     #     pass
