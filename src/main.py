import supervisely_lib as sly
import functools
import globals as g
from create_gallery import CreateGallery


def send_error_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = None
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            request_id = kwargs["context"]["request_id"]
            g.my_app.send_response(request_id, data={"error": repr(e)})
        return value

    return wrapper


@g.my_app.callback("test_compary_gallery")
@sly.timeit
@send_error_data
def test_compary_gallery(api: sly.Api, task_id, context, state, app_logger):

    project_info = api.project.get_info_by_id(g.PROJECT_ID)
    meta_json = api.project.get_meta(project_info.id)
    meta = sly.ProjectMeta.from_json(meta_json)
    dataset_info = api.dataset.get_info_by_id(g.DATASET_ID)

    images = api.image.get_list(dataset_info.id)
    image_ids = [image_info.id for image_info in images]
    images_urls = [image_info.full_storage_url for image_info in images]
    images_names = [image_info.name for image_info in images]
    ann_infos = api.annotation.download_batch(g.DATASET_ID, image_ids)
    anns = [sly.Annotation.from_json(ann_info.annotation, meta) for ann_info in ann_infos]

    full_gallery = CreateGallery(g.task_id, g.api, 'data.perClass', meta, g.col_number)
    for image_name, ann, image_url in zip(images_names, anns, images_urls):
        full_gallery.set_item(title=image_name, ann=ann, image_url=image_url)

    full_gallery.update()


def main():
    sly.logger.info("Script arguments", extra={
        "context.teamId": g.TEAM_ID
    })

    g.my_app.run(initial_events=[{"command": "test_compary_gallery"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)