from dataclasses import dataclass

@dataclass
class ReleaseInfo:
    release_key: str                 # unique identifier for release
    release_date: str                # do not release before this
    approved: bool
    approved_by: str
    # todo add envs

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