import os
import supervisely_lib as sly
from diskcache import Cache
from supervisely_lib.io.fs import mkdir

my_app = sly.AppService()

api: sly.Api = my_app.public_api
task_id = my_app.task_id

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
DATASET_ID = int(os.environ['modal.state.slyDatasetId'])

project_info = api.project.get_info_by_id(PROJECT_ID)
meta_json = api.project.get_meta(project_info.id)
meta = sly.ProjectMeta.from_json(meta_json)
dataset_info = api.dataset.get_info_by_id(DATASET_ID)

images = api.image.get_list(dataset_info.id, sort="name")
image_ids = [image_info.id for image_info in images]
images_urls = [image_info.full_storage_url for image_info in images]
images_names = [image_info.name for image_info in images]

work_dir = os.path.join(my_app.data_dir, "work_dir")
mkdir(work_dir, True)
cache_dir = os.path.join(work_dir, "diskcache")
mkdir(cache_dir)
cache = Cache(directory=cache_dir)
cache_item_expire_time = 600  # seconds

images_on_page = 30
columns_on_page = 5
first_page = 1
old_input = None
old_rows = None
with_info = True
full_gallery = None
curr_images_ids = None
curr_anns = None