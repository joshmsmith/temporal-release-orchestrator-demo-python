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

    
    
    releasekey = "RELEASE-NOV-23-INITIAL" # everything to 1.0
    #releasekey = "RELEASE-NOV-23-HOTFIX-STAGE" # new versions to everything but PROD
    #releasekey = "RELEASE-DEC-2023-BUGFIXES-PROD" # new versions to PROD
    #releasekey = "RELEASE-JAN-24-ALPHA-DEV" # January release to DEV
    #releasekey = "RELEASE-JAN-24-ALPHA-QC" # January release to TEST, QC
    #releasekey = "RELEASE-JAN-24-ALPHA-PROD" # January release to PROD

    # Release Keys must match in the release info function/data source
    if releasekey == "RELEASE-NOV-23-INITIAL":
        release_input = ReleaseInfo(release_key="RELEASE-NOV-23-INITIAL", 
                                    release_date= "2023-11-15", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    elif releasekey == "RELEASE-NOV-23-HOTFIX-STAGE":
        release_input = ReleaseInfo(release_key="RELEASE-NOV-23-HOTFIX-STAGE", 
                                    release_date= "2023-11-24", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    elif releasekey == "RELEASE-DEC-2023-BUGFIXES-PROD": 
        release_input = ReleaseInfo(release_key="RELEASE-DEC-2023-BUGFIXES-PROD", 
                                    release_date= "2023-12-12", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    elif releasekey == "RELEASE-JAN-24-ALPHA-DEV":
        release_input = ReleaseInfo(release_key="RELEASE-JAN-24-ALPHA-DEV", 
                                    release_date= "2024-01-12", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    elif releasekey == "RELEASE-JAN-24-ALPHA-QC":
        release_input = ReleaseInfo(release_key="RELEASE-JAN-24-ALPHA-QC", 
                                    release_date= "2024-01-17", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    elif releasekey == "RELEASE-JAN-24-ALPHA-PROD":
        release_input = ReleaseInfo(release_key="RELEASE-JAN-24-ALPHA-PROD", 
                                    release_date= "2024-01-24", 
                                    approved=True, 
                                    approved_by="Joshua Smith",
                                    deploys=[],
                                    )
    else:
        release_input = ReleaseInfo(release_key="RELEASE-NOV-23-INITIAL", 
                                    release_date= "2023-11-15", 
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