import supervisely_lib as sly
import functools
import globals as g
from supervisely_lib.app.widgets.compare_gallery import CompareGallery


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

    pass


def main():
    sly.logger.info("Script arguments", extra={
        "context.teamId": g.TEAM_ID
    })

    g.my_app.run()


if __name__ == "__main__":
    sly.main_wrapper("main", main)