import asyncio

import coloredlogs, logging
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
from activities import collect_deploys
from workflows import ReleaseWorkflow
from workflows import DeployWorkflow

async def main():
    # todo set it up for my namespace
    client = await Client.connect("localhost:7233", namespace="default")

    #todo add more activities and workflows here
    # Run the worker
    worker = Worker(
        client, task_queue="release-task-queue", 
        workflows=[ReleaseWorkflow, DeployWorkflow], 
        activities=[say_hello, collect_deploys],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
