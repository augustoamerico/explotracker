from s3fs import S3FileSystem
from xtore import ExperimentStorage

class S3ExperimentStorage(ExperimentStorage):

    def __init__(self, s3_bucket, s3_path):
        super().__init__(S3FileSystem(anon=False), f"/{s3_bucket}/{s3_path}/")