from temporalio import activity
import coloredlogs, logging
from dataclasses import dataclass
from temporalio import workflow
from release_dataclasses import DeployInfo, ReleaseInfo
import release_management
coloredlogs.install()

# todo add more activities here
# such as validate release, 
# deploy (child workflow here), 
# validate deploy, check security (prints to console), deploy (moves files)
# etc
@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@activity.defn
async def collect_deploys(release_info: ReleaseInfo) -> ReleaseInfo:
    """ collect_releases: gather all releases for this deploy
    
    This is mocked for demo purposes but in the future all it needs to do is collect releasable 
    items from input or """

    logging.info("Collecting Release Info for %s ", release_info.release_key)
    release_info = release_management.gather_deployments(release_info)

    logging.info("Release Info for %s collected.", release_info.release_key)
    return release_info
