from portofolio.utils import files_utils
from portofolio.utils.config_utils import make_config_dir, create_default_config

make_config_dir()
create_default_config()

# making sure the correct directories exist
if not files_utils.check_dir('client_data/data/prices'):
    files_utils.make_dir('client_data/data/prices')

if not files_utils.check_dir('client_data/data/fx'):
    files_utils.make_dir('client_data/data/fx')

if not files_utils.check_dir('client_data/data/statements'):
    files_utils.make_dir('client_data/data/statements')