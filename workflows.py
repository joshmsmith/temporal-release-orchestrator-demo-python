import coloredlogs, logging
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow
import release_management

from release_dataclasses import DeployInfo, ReleaseInfo

coloredlogs.install()

# define some configurable behavior
unapproved_deploys_behavior_roll_forward_skipping = "Release Everything That's Approved"
unapproved_deploys_behavior_hold_for_signal = "Wait for Signals for Deploy Approval" # not supported todo
unapproved_deploys_behavior_stop = "If a deploy isn't approved, stop process"

dev_deploy_behavior_only_dev = "If dev is selected to deploy to, only allow Dev, and error if dev+something else is included"
dev_deploy_behavior_only_dev_warn = "If dev is selected to deploy to, only allow Dev, and warn if dev+something else is included and only do dev"
dev_deploy_behavior_dev_plus_others_is_ok = "If dev is selected to deploy to with other environments, proceed" # have good automated testing


config_unapproved_deploys_behavior = unapproved_deploys_behavior_roll_forward_skipping
config_dev_deploy_behavior = dev_deploy_behavior_dev_plus_others_is_ok

# Import activity, passing it through the sandbox without reloading the module
    # todo: import the new activities
with workflow.unsafe.imports_passed_through():
    from activities import say_hello
    from activities import collect_deploys
    from activities import collect_release_approval
    from activities import build
    from activities import testInDev
    from activities import testInTest
    from activities import testInQC
    from activities import testInProd
    from activities import deployToDev
    from activities import deployToTest
    from activities import deployToQC
    from activities import deployToProd

@workflow.defn
class DeployWorkflow:
    @workflow.run
    async def run(self, input: DeployInfo) -> str:
        logging.info(f"The Deploy for {input.deploy_key} beginning.")

        # validate - must deploy to at least one environment, can't skip environments when going to prod, can't do dev and anything else (config option)
        envs = input.envs
        if len(envs) == 0:
            return "No Environements to deploy to, stopping deploy."
        
        if  release_management.development in envs and len(envs) > 1:
            if config_dev_deploy_behavior == dev_deploy_behavior_only_dev : 
                raise RuntimeError(f"Deployment Exception: Deploy {input.deploy_key} failure: trying to do Dev and another environment and that's prohibited by configuration.")
            elif config_dev_deploy_behavior == dev_deploy_behavior_only_dev_warn : 
                logging.warning(f"Deployment Warning: {input.deploy_key} is deploying to dev with other envs, config says to warn, this is probably bad.")    
        
        if release_management.production in envs and len(envs) > 1:
            if not release_management.qualitycontrol in envs :
                raise RuntimeError(f"Deployment Exception: Deploy {input.deploy_key} failure: trying to go to production and skipping environments, this is not recommended.")

        # Serially proceed through the environments
        # for each env, deploy (artifact, config), test (ping /health, run automated tests), set ready for next env
            
        # do the needful in Dev
        if  release_management.development in envs:
            # build
            activity_output = await workflow.execute_activity(
                build, input, start_to_close_timeout=timedelta(seconds=300)
            )
            logging.info(f"Build Status for {input.deploy_key}: {activity_output}")

            # deploy to Dev
            activity_output = await workflow.execute_activity(
                deployToDev, input, start_to_close_timeout=timedelta(seconds=300)
            )
            logging.info(f"Deploy to Dev for {input.deploy_key} Status: {activity_output}")

            # test
            activity_output = await workflow.execute_activity(
                testInDev, input, start_to_close_timeout=timedelta(seconds=50)
            )
            logging.info(f"Test in Dev for {input.deploy_key} Status: {activity_output}")

        # do needful stuff in Test
        if  release_management.testing in envs:
            # deploy to test
            activity_output = await workflow.execute_activity(
                deployToTest, input, start_to_close_timeout=timedelta(seconds=300)
            )
            logging.info(f"Deploy to Test for {input.deploy_key} Status: {activity_output}")
            # test in Test
            activity_output = await workflow.execute_activity(
                testInTest, input, start_to_close_timeout=timedelta(seconds=50)
            )
            logging.info(f"Test in Test for {input.deploy_key} Status: {activity_output}")

        # do needful stuff in QC
        if  release_management.qualitycontrol in envs:
            # deploy to QC
            activity_output = await workflow.execute_activity(
                deployToQC, input, start_to_close_timeout=timedelta(seconds=300)
            )
            logging.info(f"Deploy to QC for {input.deploy_key} Status: {activity_output}")
            # test in QC
            activity_output = await workflow.execute_activity(
                testInQC, input, start_to_close_timeout=timedelta(seconds=50)
            )
            logging.info(f"Test in QC for {input.deploy_key} Status: {activity_output}")

         # do needful stuff in Production
        if  release_management.production in envs:
            # deploy to Prod
            activity_output = await workflow.execute_activity(
                deployToProd, input, start_to_close_timeout=timedelta(seconds=300)
            )
            logging.info(f"Deploy to Production for {input.deploy_key} Status: {activity_output}")
            # test in Prod
            activity_output = await workflow.execute_activity(
                testInProd, input, start_to_close_timeout=timedelta(seconds=50)
            )
            logging.info(f"Test in Production for {input.deploy_key} Status: {activity_output}")
        
        
        


        # todo: error handling:
            # if services depend on each other being new: ERROR AND ROLL FORWARD ONLY or roll back the entire thing
            # if services don't depend on new changes as a rule, roll back
            # container error, saga it, roll back with compensation?
            # config error -> we're fucked; sorry... // could make a copy but ehh
            # keep retrying for unknown errors so they can be fixed and parent can be ok.
            # notification: command line, UI, and slack
            # user input: wait for something to be fixed (josh calls this "roll forward") or roll back to last good state ( config+container) or fall down (roll over)
            #   // potentially update the container version?
        
        
        logging.info(f"The Deploy for {input.deploy_key} worked!")
        
        return f"Deploy Success: {input.deploy_key}!"



@workflow.defn
class ReleaseWorkflow:
    """ Release Workflow
    
    Collect deployment info and initiate a release for each item to release.
    """
    @workflow.run
    async def run(self, input: ReleaseInfo) -> str:
        logging.info("Beginning Release: %s ", input.release_key)

        # Release Workflow:
        # 0. if deploys are not passed in, collect them
        # 1. Collect all deploys and info 
        release = input
        if len(release.deploys) == 0:
            logging.info(f"No deployments passed in for {input.release_key}, gathering them now.")
            release = await workflow.execute_activity(
                collect_deploys, input, start_to_close_timeout=timedelta(seconds=5)
            )

        # 1.b - if any deploys are not ready to go, hold if set to hold 
            # for now just end the release if something is not approved or just don't release it
            # could potentially do a signal for deploys being approved (todo)
        deploys_all_approved = True
        for deploy in release.deploys:
            if not deploy.approved :
                deploys_all_approved = False
                break
        if not deploys_all_approved:
            if config_unapproved_deploys_behavior == unapproved_deploys_behavior_roll_forward_skipping:
                logging.info(f"Release {release.release_key} contains some non-approved deploys, proceeding but skipping unapproved deploys.")
            elif config_unapproved_deploys_behavior == unapproved_deploys_behavior_stop:
                logging.warning(f"Release {release.release_key} contains some non-approved deploys, stopping.")    
                return f"Release {release.release_key}: HALTED BECAUSE OF UNAPPROVED DEPLOYS AND CONFIG SAID TO STOP"
            elif config_unapproved_deploys_behavior == unapproved_deploys_behavior_hold_for_signal:
                #todo signals are not built for deploy-level approvals at this time.
                logging.warning(f"Release {release.release_key} contains some non-approved deploys, stopping.")    
                return f"Release {release.release_key}: HALTED BECAUSE OF UNAPPROVED DEPLOYS AND WE DON'T HAVE SIGNALS TO APPROVE THEM YET."
            

        # 2. collect approval (and eventually schedule info)
        if not release.approved:
            logging.info(f"Release {input.release_key} not yet approved, gathering approval now.")
            release = await workflow.execute_activity(
                    collect_release_approval, input, start_to_close_timeout=timedelta(seconds=5)
                )

        # 2.a eventually this could just run on a schedule so add schedule stuff
        # todo schedule stuff

        # 3. attempt to run all deploys
        for deploy in release.deploys:
            deploy_status = await workflow.execute_child_workflow( 
                DeployWorkflow.run,
                deploy,
                id=f"deploy-workflow-{deploy.deploy_key}", 
            )  

        logging.info(f"Release {release.release_key} successful!")
        return f"Release {release.release_key}: SUCCESS"
    

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

