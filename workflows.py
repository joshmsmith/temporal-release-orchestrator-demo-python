import coloredlogs, logging
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

from release_dataclasses import DeployInfo, ReleaseInfo

coloredlogs.install()



# Import activity, passing it through the sandbox without reloading the module
    # todo: import the new activities
with workflow.unsafe.imports_passed_through():
    from activities import say_hello
    from activities import collect_releases

@workflow.defn
class DeployWorkflow:
    @workflow.run
    async def run(self, input: DeployInfo) -> str:
        # todo: so much to do here

        name = "Josh"
        activity_output = await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=5)
        )
        logging.info("%s The Deploy worked!", activity_output)
        
        return f"Deploy Success: {input.deploy_key}!"



@workflow.defn
class ReleaseWorkflow:
    """ Release Workflow
    
    Collect deployment info and initiate a release for each item to release.
    """
    @workflow.run
    async def run(self, input: ReleaseInfo) -> str:
        logging.info("Beginning Deploy: %s ", input.release_key)

        
        # todo lots to do here
        # Release Workflow:
        # 1. Collect all deploys and info - if any of them are not ready to go, hold
        release_with_deployments = await workflow.execute_activity(
            collect_releases, input, start_to_close_timeout=timedelta(seconds=5)
        )

        # 2. collect approval (and eventually schedule info)

        # todo loop over releases here
        
        # 3. attempt to run all deploys
        # 4. eventually this could just run on a schedule so add schedule stuff
        deploy_status = await workflow.execute_child_workflow( 
            DeployWorkflow.run,
            DeployInfo(deploy_key = input.release_key+":sbstore", 
                        container_id = "sbstore", 
                        container_version="", 
                        git_url = "https://github.com/mysampleorg/sbstore.git", 
                        approved = True, 
                        approved_by = "Bob Johnson", 
                        envs = ["Production"], 
                        release_key = input.release_key,
                        ),
            id="release-workflow-child-id", # todo probably should change this
        )

        logging.info("The Deploy worked!")
       
        

        logging.info("%s: Release success", deploy_status)
        return deploy_status
    

### Notes about process
# Build:
    # Trigger: ready to be built
    # containers
    # new version of container
    # new version of main/checkin
    # need old version and old dates?
    # Build done after tests or mark it somewhere or after container is versioned or set somewhere if there's a release overlord
    # need something to tie container versions to scans - need scan output and connect them somehow
    #   // pdfs or something you can link to
    # set build done in database
# Deploy:
    # choose which environments to deploy to: [dev, IQ, Prod] - no skipping but could only go to lower envs
    # need to know that it already was in a lower environment, so Dev->IQ, IQ->prod, or Dev->IQ->prod
    # // pick up config and containers from lower, so like conf from dev and myapp-1.72:dev
    # OK to deploy: secure, tested, approved, and scheduled has arrived
    #   // approved: for Dev: always yes or tech lead says yes
    #   // secure: passed tests
    #   // tested: passed automated tests (for dev, may want approvals for higher envs)
    #   //  at the time of release XYZ
    # Get container from build process
    # install/update container and get from config in git:
    #   // go get config for env and replace from git by /env folder
    # Validate health, if good, yay done, ping /health
    # indicate deploy is done in database
# error handling:
    # if services depend on each other being new: ERROR AND ROLL FORWARD ONLY or roll back the entire thing
    # if services don't depend on new changes as a rule, roll back
    # container error, saga it, roll back with compensation?
    # config error -> we're fucked; sorry... // could make a copy but ehh
    # keep retrying for unknown errors so they can be fixed and parent can be ok.
    # notification: command line, UI, and slack
    # user input: wait for something to be fixed (josh calls this "roll forward") or roll back to last good state ( config+container) or fall down (roll over)
    #   // potentially update the container version?

# dev teams: job is to make it "ok to deploy"
# QA Team: yeah it's good
# release approver: verifies and says go
    
# release
    # whatever existed at time of release that's "ok to deploy" is good to go
    # for now, just do "now"
    # 1. Collect all deploys and info - if any of them are not ready to go, hold
    # 2. collect approval (and eventually schedule info)
    # 3. attempt to run all deploys
    # 4. eventually this could just run on a schedule

