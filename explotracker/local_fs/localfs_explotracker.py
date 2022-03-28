from explotracker import ExperimentLogger
import importlib
import sys

class LocalExperimentLogger(ExperimentLogger):

    def __init__(self, root):
        SPEC_OS = importlib.util.find_spec('os')
        os1 = importlib.util.module_from_spec(SPEC_OS)
        SPEC_OS.loader.exec_module(os1)
        sys.modules['os1'] = os1
        os1.open = open
        os1.exists = lambda x: os1.path.isfile(x) or os1.path.isdir(x)
        super().__init__(os1, root)

