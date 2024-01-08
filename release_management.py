import coloredlogs, logging
from dataclasses import dataclass
from release_dataclasses import DeployInfo, ReleaseInfo
import utils
coloredlogs.install()

# define some environment names
production =        "PROD"
qualitycontrol =    "QC"
testing =           "TEST"
development =       "DEV"


def gather_deployments(release_info: ReleaseInfo) -> ReleaseInfo:
    """ collect_releases: gather all releases for this deploy
    
    In a real system this could look up the info for each deploy, here it is mocked. """
    
    logging.info("Collecting Release Info for %s ", release_info.release_key)

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
         raise RuntimeError(f"Deployment Exception: At end of gathering releases for {release_info.release_key} failed!")
    
    release_info.deploys = deploys
    

    logging.info(f"Release Info for { release_info.release_key} collected.")
    return release_info
