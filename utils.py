import random
import coloredlogs, logging
from dataclasses import dataclass
from release_dataclasses import DeployInfo, ReleaseInfo
coloredlogs.install()

def isErrorRarely() -> bool:
    if random.randint(1, 10) > 9 :
        return True
    
    return False

def isErrorSometimes() -> bool:
    if random.randint(1, 10) > 7 :
        return True
    
    return False


def isErrorALot() -> bool:
    if random.randint(1, 10) > 4 :
        return True
    
    return False