import os
import supervisely_lib as sly

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
ann_infos = api.annotation.download_batch(DATASET_ID, image_ids)
anns = [sly.Annotation.from_json(ann_info.annotation, meta) for ann_info in ann_infos]

images_on_page = 10
columns_on_page = 2
first_page = 1