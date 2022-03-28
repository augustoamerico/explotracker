from s3fs import S3FileSystem
from xtore.explotracker import ExperimentStorage

class S3ExperimentStorage(ExperimentStorage):

    def __init__(self, s3_bucket, s3_path, kwargs={"anon": False, "default_fill_cache": False}):
        super().__init__(S3FileSystem(**kwargs), f"/{s3_bucket}/{s3_path}/")
