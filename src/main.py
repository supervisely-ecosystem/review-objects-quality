import supervisely_lib as sly
import functools
import globals as g
from create_gallery import Gallery


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


def get_first_last_page(current_page, max_pages_count):
    if current_page != 1:
        is_first_page = False
    else:
        is_first_page = True

    if current_page != max_pages_count:
        is_last_page = False
    else:
        is_last_page = True

    return is_first_page, is_last_page


def update_gallery_by_page(current_page, state):

    cols = state['cols']
    images_per_page = state['rows']
    max_pages_count = len(g.image_ids) // images_per_page
    if len(g.image_ids) % images_per_page != 0:
        max_pages_count += 1

    is_first_page, is_last_page = get_first_last_page(current_page, max_pages_count)

    full_gallery = Gallery(g.task_id, g.api, 'data.perClass', g.meta, cols)

    curr_images_names = g.images_names[images_per_page * (current_page - 1):images_per_page * current_page]
    curr_anns = g.anns[images_per_page * (current_page - 1):images_per_page * current_page]
    curr_images_urls = g.images_urls[images_per_page * (current_page - 1):images_per_page * current_page]

    for idx, (image_name, ann, image_url) in enumerate(zip(curr_images_names, curr_anns, curr_images_urls)):
        if idx == images_per_page:
            break
        full_gallery.set_item(title=image_name, ann=ann, image_url=image_url)

    full_gallery.update()

    fields = [
        {"field": "state.galleryInitialized", "payload": True},
        {"field": "state.galleryPage", "payload": current_page},
        {"field": "state.galleryIsFirstPage", "payload": is_first_page},
        {"field": "state.galleryIsLastPage", "payload": is_last_page},
        {"field": "state.galleryMaxPage", "payload": max_pages_count},
        {"field": "state.input", "payload": current_page}
    ]
    g.api.app.set_fields(g.task_id, fields)


@g.my_app.callback("next_page")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def next_page(api: sly.Api, task_id, context, state, app_logger):
    current_page = state['galleryPage']
    update_gallery_by_page(current_page + 1, state)


@g.my_app.callback("previous_page")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def next_page(api: sly.Api, task_id, context, state, app_logger):
    current_page = state['galleryPage']
    update_gallery_by_page(current_page - 1, state)


@g.my_app.callback("test_compary_gallery")
@sly.timeit
@send_error_data
def test_compary_gallery(api: sly.Api, task_id, context, state, app_logger):

    if state is None:
        images_per_page = 1
        payload = False
        current_page = 1
    else:
        go_to_page = state.get('input')
        if go_to_page is not None:
            current_page = int(go_to_page)
        else:
            current_page = state['galleryPage']
        payload = True
        images_per_page = state['rows']
        update_gallery_by_page(current_page, state)

    max_pages_count = len(g.image_ids) // images_per_page
    if len(g.image_ids) % images_per_page != 0:
        max_pages_count += 1

    is_first_page, is_last_page = get_first_last_page(current_page, max_pages_count)

    fields = [
        {"field": "state.galleryInitialized", "payload": payload},
        {"field": "state.galleryPage", "payload": current_page},
        {"field": "state.galleryIsFirstPage", "payload": is_first_page},
        {"field": "state.galleryIsLastPage", "payload": is_last_page},
        {"field": "state.galleryMaxPage", "payload": max_pages_count},
        {"field": "state.input", "payload": current_page}
    ]
    g.api.app.set_fields(g.task_id, fields)


def main():
    sly.logger.info("Script arguments", extra={
        "context.teamId": g.TEAM_ID
    })

    g.my_app.run(initial_events=[{"command": "test_compary_gallery"}])



if __name__ == "__main__":
    sly.main_wrapper("main", main)