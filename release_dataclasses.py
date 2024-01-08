from dataclasses import dataclass



# this is the deploy of an individual deployable
@dataclass
class DeployInfo:
    deploy_key: str
    container_id: str
    container_version: str
    git_url: str
    approved: bool
    approved_by: str
    envs: list[str]
    release_key: str     # Parent Release's unique ID


# this is the parent object, containing the fleet of things to deploy for a release
@dataclass
class ReleaseInfo:
    release_key: str                 # unique identifier for release
    release_date: str                # do not release before this
    approved: bool
    approved_by: str
    deploys: list[DeployInfo]
    
    