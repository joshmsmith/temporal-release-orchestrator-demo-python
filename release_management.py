import coloredlogs, logging
from dataclasses import dataclass
from release_dataclasses import DeployInfo, ReleaseInfo
import utils
coloredlogs.install()

# define some environment names - feel free to configure these strings for you but changing the varnames means some code has to change
# assuming we go in this order, from development->testing->qualitycontrol->production
production =        "PROD"
qualitycontrol =    "QC"
testing =           "TEST"
development =       "DEV"


def gather_deployments(release_info: ReleaseInfo) -> ReleaseInfo:
    """ collect_releases: gather all releases for this deploy
    
    In a real system this could look up the info for each deploy, here it is mocked. """
    
    logging.debug("Collecting Release Info for %s ", release_info.release_key)

    # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Deployment Exception: Gathering releases for {release_info.release_key} failed.!")
    
    
    # mock gather things to deploy: for this purpose we'll just make some things up

    deploy_frontend = DeployInfo(deploy_key= release_info.release_key+":frontend", 
                                 container_id= "frontend", 
                                 container_version="1.1", 
                                 git_url="https://github.com/mybiz/coolfrontend", 
                                 approved=True, 
                                 approved_by="Josh Smith", 
                                 envs=[production],
                                 release_key=release_info.release_key,
    )
    logging.info(f"Deploy Info for { deploy_frontend.deploy_key} collected.")


    deploy_store = DeployInfo(deploy_key = release_info.release_key+":sbstore", 
                              container_id = "sbstore", 
                              container_version="1.7",
                              git_url = "https://github.com/mybiz/sbstore.git", 
                              approved = True, 
                              approved_by = "Bob Johnson", 
                              envs=[production],
                              release_key = release_info.release_key,
                            )
    logging.info(f"Deploy Info for { deploy_store.deploy_key} collected.")
    
    deploy_backend_for_frontend = DeployInfo(deploy_key = release_info.release_key+":BFF", 
                                             container_id = "backendforfrontend", 
                                             container_version="1.7",
                                             git_url = "https://github.com/mybiz/backendff.git", 
                                             approved = True, 
                                             approved_by = "James Garner", 
                                             envs=[production],
                                             release_key = release_info.release_key,
                                            )
    
    logging.info(f"Deploy Info for { deploy_backend_for_frontend.deploy_key} collected.")

    deploys = [deploy_frontend, deploy_store, deploy_backend_for_frontend]

   # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Release Exception: At end of gathering releases for {release_info.release_key} failed!")
    
    release_info.deploys = deploys
    

    logging.debug(f"Release Info for { release_info.release_key} collected.")
    return release_info



def gather_release_approval(release_info: ReleaseInfo) -> ReleaseInfo:
    """ gather_release_approval: look up if a release is approved.
     
    This could be provided by an external system, here it is mocked. """
    
    logging.debug("Collecting Release Approval for %s ", release_info.release_key)

    # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Release Exception: Gathering release approval for {release_info.release_key} failed.")
    
    release_info.approved = True
    release_info.approved_by = "Joshua Smith"
    

    logging.debug(f"Release Approval Info for { release_info.release_key} collected.")
    return release_info


# todo: Build for Dev
     # Trigger: ready to be built
     # containers
     # new version of container
     # new version of main/checkin
     # need old version and old dates?
     # Build done after tests or mark it somewhere or after container is versioned or set somewhere if there's a release overlord
     # need something to tie container versions to scans - need scan output and connect them somehow
     #   // pdfs or something you can link to
     # set build done in database - why?
     # notify success/fail in slack

def build(deployinfo: DeployInfo) -> str:
    """ build: run a build

    input: info on an app to build
    output: status str
    changes: creates a new artificat in the artifact repo place
    this could be smart and do different kinds of builds, call an external build system, or whatever, but for demo it is mocked. """
    
    logging.debug("Building for %s ", deployinfo.deploy_key)

    # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Build Exception: build failed, artifact not created.")
    
    #todo fail in a human-repairable way, to simulate a security or build problem that can be repaired
    #todo make new artifacts in dev with new container_version
    #todo create output artifacts to simulate test results and scans
    #todo - update container version with new build info?

    logging.debug(f"Build successful for {deployinfo.deploy_key}, new artifact in Dev.")
    return "BUILD SUCCESSFUL"

def test(deployinfo: DeployInfo, evn: str) -> str:
    """ test: validate a build

    input: info on an app to test and env to test in
    output: status str
    this could be smart and do different kinds of tests, like performance or whatever, but for demo it is mocked. """
    
    logging.debug("Testing for %s ", deployinfo.deploy_key)

    # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Test Exception: test failed, could not complete test.")
    
    #todo fail in a human-repairable way, to simulate a performance, security, or quality problem that can be repaired
    
    logging.debug(f"Test successful for {deployinfo.deploy_key}, new artifact is working in Dev.")
    return "TESTS SUCCESSFUL"

# Deploy: for each env
     # choose which environments to deploy to: [dev, IQ, CIT, Prod] - no skipping but could only go to lower envs
     # assume it was already in the lower environment, so Dev->IQ, IQ->prod, or Dev->IQ->prod
     # // pick up config and containers from lower, so like conf from dev and myapp-1.72:dev
     # OK to deploy: secure, tested, approved, and scheduled has arrived
     #   // approved: for Dev: always yes or tech lead says yes
     #   // secure: passed tests
     #   // tested: passed automated tests (for dev, may want approvals for higher envs)
     #   //  at the time of release XYZ
     # Get container from build process or artifact repo
     # install/update container and get from config in git:
     #   // go get config for env and replace from git by /env folder
     # Validate health, if good, yay done, ping /health
     # indicate deploy is done in database

def deploy(deployinfo: DeployInfo, destination: str) -> str:
    """ deploy: deploy an artifact and its config to a destination

    input: deploy info about an application and where to deploy it
    output: status str
    """
    
    logging.info(f"Deploying {deployinfo.deploy_key}")

    logging.debug(f"Updating Config for {deployinfo.deploy_key} from {deployinfo.git_url}")
    logging.debug(f"Config update complete for {deployinfo.deploy_key}")
    logging.debug(f"Moving {deployinfo.container_id}:{deployinfo.container_version} to {destination} for {deployinfo.deploy_key}")
    logging.debug(f"Artifact Move complete for {deployinfo.deploy_key}...restarting {deployinfo.container_id}.")

    # throw an error here sometimes
    if utils.isErrorRarely() :
         raise RuntimeError(f"Deploy Exception: deploy failed, app not deployed.")
    
    #todo actually move stuff around into folders
    
    logging.info(f"Deploy successful for {deployinfo.deploy_key}, new artifact is deployed to {destination}.")
    return "DEPLOY SUCCESSFUL"