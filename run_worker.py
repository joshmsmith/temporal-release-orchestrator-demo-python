import asyncio

import coloredlogs, logging
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
from activities import collect_deploys
from activities import collect_release_approval
from activities import build
from activities import testInDev
from activities import testInTest
from activities import testInQC
from activities import testInProd
from activities import deployToDev
from activities import deployToTest
from activities import deployToQC
from activities import deployToProd
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
        activities=[say_hello, 
                    collect_deploys, 
                    collect_release_approval,
                    build,
                    testInDev,
                    testInTest,
                    testInQC,
                    testInProd,
                    deployToDev,
                    deployToTest,
                    deployToQC,
                    deployToProd],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
