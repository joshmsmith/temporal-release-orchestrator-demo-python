from dataclasses import dataclass



# this is the deploy of an individual deployable
@dataclass
class DeployInfo:
    deploy_key: str
    container_id: str
    container_version: str
    git_url: str
    approved: bool      # typically: dev, QA, release management, change board have all signed off if needed; 
                        # could do this with multiple variables but keeping it simple for demo
                        # functions as "ready to be built" if deploying to dev
    approved_by: str    # for auditing
    envs: list[str]
    release_key: str    # Parent Release's unique ID


# this is the parent object, containing the fleet of things to deploy for a release
@dataclass
class ReleaseInfo:
    release_key: str                # unique identifier for release
    release_date: str               # do not release before this
    approved: bool                  # approved by change management authority
    approved_by: str                # for auditing
    deploys: list[DeployInfo]       # list of things to deploy as part of this release- can be gathered as part of release flow
    
    