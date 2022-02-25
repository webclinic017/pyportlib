from ..utils import files_utils

if not files_utils.check_dir("client_data/outputs/"):
    files_utils.make_dir("client_data/outputs/")