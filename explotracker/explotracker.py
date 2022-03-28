from typing import Optional, List, Union
import io
import gzip
import os

try:
   import cPickle as pickle
except:
   import pickle



class Experiment():
    private_properties = {'fs','fs_root','project','experiment_short','access_mode'}
    allowed_mode_chars = {'r','w','rw','wr'}

    def __init__(self, filesystem, root, project: str, experiment_short: str, mode: str = "rw"):
        if mode not in Experiment.allowed_mode_chars:
            raise Exception(f"mode can only be `r`, `w`, `rw` or `wr`")
        self.fs = filesystem
        self.fs_root = root
        self.project = project
        self.experiment_short = experiment_short
        self.access_mode = mode
        
    def __write_on_filesystem(self, key, value):
        inmem = io.BytesIO()
        with gzip.GzipFile(fileobj=inmem, mode='wb') as fh:
            pickle.dump(value, fh)

        file_path = os.path.join(self.fs_root,self.project,self.experiment_short,f"{key}.pkl.gzip")
        inmem.seek(0)

        f = self.fs.open(file_path, 'wb')
        f.write(inmem.getbuffer())
        f.close()


    def __read_from_filesystem(self, key):
        file_path = os.path.join(self.fs_root,self.project, self.experiment_short, f"{key}.pkl.gzip")
        f = self.fs.open(file_path, 'rb')
        value = pickle.load(gzip.open(f))
        f.close()
        return value

    def __list_artifacts(self) -> List[str]:
        return list(
                    map(lambda x: x.split("/")[-1].split(".pkl.gzip")[0],
                        filter(lambda x: ".pkl.gzip" in x, self.fs.find(self.fs_root, maxdepth=6))
                ))

    def __setattr__(self, key, value):
        if key not in Experiment.private_properties:
            if "w" in self.access_mode:
                self.__write_on_filesystem(key, value)
                self.__dict__[key] = value
            else:
                raise Exception(f"Cannot write attribute in experiment in {self.access_mode} mode")
        else:
            self.__dict__[key] = value

    
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            attribute = self.__read_from_filesystem(name)
            if attribute is None:
                raise AttributeError(f"'{self}' object has no attribute '{name}'")
            self.__dict__[name] = attribute
            return attribute
            
    def list_artifacts(self):
        return set(self.__list_artifacts()) - Experiment.private_properties


class ExperimentAlreadyExists(Exception):
    pass


class ExperimentNotFound(Exception):
    pass


class ExperimentLogger():

    def __init__(self, filesystem, root):
        self.fs = filesystem
        self.root = root
    
    
    def list_projects(self, like: Optional[str] = None):
        return list(
                filter(lambda x: x != '',
                        map(lambda x: f"/{x}".split(self.root)[-1], self.fs.ls(self.root)
                )))

    def list_experiments(self, like: Optional[str] = None, project: Optional[List[ Union[str, List[str]]]] = None):
        return list(
                filter(lambda x: x != '' and x.count("/")>1,
                        map(lambda x: f"/{x}".split(self.root)[-1], self.fs.find(self.root, maxdepth=3)
                )))


    def create_experiment(self, project,experiment_short, experiment_description):
        # check if project exists. If not, create folder
        project_path = os.path.join(self.root, project)
        print(f"Checking if {project_path} exists...")
        if not self.fs.exists(project_path):
            print("Creating project...")
            self.fs.mkdir(project_path)
        # check if experiment already exists. If it exists, raise ExperimentAlreadyExists exception
        experiment_path = os.path.join(project_path, experiment_short)
        if not self.fs.exists(experiment_path):
            self.fs.mkdir(experiment_path)
            f = self.fs.open(os.path.join(experiment_path, "_description"), 'wb')
            f.write(str.encode(experiment_description))
            f.close()
        else:
            raise ExperimentAlreadyExists()
        return Experiment(self.fs, self.root, project, experiment_short)

    def import_experiment(self, project, experiment_short, mode="r"):
        if self.fs.exists(os.path.join(self.root, project, experiment_short)):
            return Experiment(self.fs, self.root, project, experiment_short, mode)
        raise ExperimentNotFound()


