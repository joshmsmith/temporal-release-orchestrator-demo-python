import asyncio

from run_worker import ReleaseWorkflow
from release_dataclasses import ReleaseInfo
from temporalio.client import Client


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # todo use cloud
    # todo create inputs
    # todo create a signal to approve

    release_input = ReleaseInfo(release_key="RELEASE-JAN-24-ALPHA", 
                                release_date= "2024-01-14", 
                                approved=True, 
                                approved_by="Joshua Smith",
                                deploys=[],
                                )
    # Execute a workflow
    result = await client.execute_workflow(
        ReleaseWorkflow.run, release_input, id=f"release-workflow:{release_input.release_key}", task_queue="release-task-queue"
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())