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
async def build(deploy: DeployInfo) -> str:
    return release_management.build(deploy)

@activity.defn
async def testInDev(deploy: DeployInfo) -> str:
    return release_management.test(deploy, release_management.development)

@activity.defn
async def testInTest(deploy: DeployInfo) -> str:
    return release_management.test(deploy, release_management.testing)

@activity.defn
async def testInQC(deploy: DeployInfo) -> str:
    return release_management.test(deploy, release_management.qualitycontrol)

@activity.defn
async def testInProd(deploy: DeployInfo) -> str:
    return release_management.test(deploy, release_management.production)


@activity.defn
async def deployToDev(deploy: DeployInfo) -> str:
    return release_management.deploy(deploy, release_management.development)

@activity.defn
async def deployToTest(deploy: DeployInfo) -> str:
    return release_management.deploy(deploy, release_management.testing)

@activity.defn
async def deployToQC(deploy: DeployInfo) -> str:
    return release_management.deploy(deploy, release_management.qualitycontrol)

@activity.defn
async def deployToProd(deploy: DeployInfo) -> str:
    return release_management.deploy(deploy, release_management.production)

@activity.defn
async def collect_deploys(release_info: ReleaseInfo) -> ReleaseInfo:
    """ collect_releases: gather all releases for this deploy
    
    This is mocked for demo purposes but in the future all it needs to do is collect releasable 
    items from input or from a deployment source, like a database, JSON/YAML file, or API """

    logging.info("Collecting Release Info for %s ", release_info.release_key)
    release_info = release_management.gather_deployments(release_info)

    logging.info("Release Info for %s collected.", release_info.release_key)
    return release_info


@activity.defn
async def collect_release_approval(release_info: ReleaseInfo) -> ReleaseInfo:
    """ collect_release_approval: gather approval for this deploy
    
    This is mocked for demo purposes but in the future it could await a signal or approval in another system via API """

    logging.info("Collecting Approval Info for %s ", release_info.release_key)
    release_info = release_management.gather_release_approval(release_info)

    logging.info("Release Approval for %s collected.", release_info.release_key)
    return release_info
