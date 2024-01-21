# For Demo
```
[ ] Enable optional connection to cloud
[ ] Implement signals to approve deploys (and releases?)
[ ] UI for approvals?
[x] move files around instead of just print logs
[ ] Implement more release and error handling rules from [workflows.py](./workflows.py)
[ ] Add simulated tests - performance, security, etc.
[ ] Add simulated config files to be deployed as well
[ ] Add more tests in [tests](./tests/)
```

# For a Real Application
```
[ ] Use Temporal Cloud instead of local
[ ] Call your build and deployment system in [release_management.py](./release_management.py)
[ ] Change the environments to match your environments
[ ] Load real releases and real deploy info in [release_management.py](./release_management.py) - perhaps from a config JSON or from an API
[ ] Call [run_workflow.py](./run_workflow.py) with a real release key from your releases matching your release info
[ ] Build a UI and Signals if you want interactivity/visibility
```