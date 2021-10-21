from typing import Union
from supervisely_lib.project.project_meta import ProjectMeta
from supervisely_lib.api.api import Api
from supervisely_lib.annotation.annotation import Annotation


class CreateGallery:

    def __init__(self, task_id, api: Api, v_model, project_meta: ProjectMeta, col_number: int):
        self._task_id = task_id
        self._api = api
        self._v_model = v_model
        self._project_meta = project_meta.clone()
        self._data = {}
        self.col_number = col_number
        if not isinstance(self.col_number, int):
            raise ValueError("Columns number must be integer, not {}".format(type(self.col_number).__name__))

        self._options = {
            "enableZoom": True,
            "syncViews": True,
            "showPreview": False,
            "selectable": False,
            "opacity": 0.5,
            "showOpacityInHeader": True
        }
        self._options_initialized = False

    def update_project_meta(self, project_meta: ProjectMeta):
        self._project_meta = project_meta.clone()

    def _set_item(self, title, image_url, ann: Union[Annotation, dict] = None):

        res_ann = Annotation((1,1))
        if ann is not None:
            if type(ann) is dict:
                res_ann = Annotation.from_json(ann, self._project_meta)
            else:
                res_ann = ann.clone()

        self._data[title] = (image_url, res_ann)


    def set_item(self, title, image_url, ann: Union[Annotation, dict] = None):
        self._set_item(title, image_url, ann)

    def _get_item_annotation(self, name):
        return {
            "url": self._data[name][0],
            "figures": [label.to_json() for label in self._data[name][1].labels],
            "title": name,
        }

    def update(self, options=True):
        if len(self._data) == 0:
            raise ValueError("Items list is empty")

        gallery_json = self.to_json()
        if options is True or self._options_initialized is False:
            self._api.task.set_field(self._task_id, self._v_model, gallery_json)
            self._options_initialized = True
        else:
            self._api.task.set_field(self._task_id, f"{self._v_model}.content", gallery_json["content"])

    def to_json(self):

        annotations = {}
        layout = []
        curr_col = []
        odd_image = 0
        number_of_pairs = None

        if len(self._data) < self.col_number * 2 and len(self._data) > self.col_number:
            number_of_pairs = len(self._data) - self.col_number
            imgs_in_col = 2
        elif len(self._data) < self.col_number:
            imgs_in_col = 1
        else:
            imgs_in_col = len(self._data) // self.col_number
            odd_image = len(self._data) % self.col_number

        for curr_data_name, curr_url_ann in self._data.items():
            annotations[curr_data_name] = self._get_item_annotation(curr_data_name)
            if len(curr_col) != imgs_in_col:
                curr_col.append(curr_data_name)
            else:
                layout.append(curr_col)
                curr_col = [curr_data_name]
                if number_of_pairs:
                    number_of_pairs -= 1
                    if number_of_pairs == 0:
                        imgs_in_col = 1

        if len(curr_col) != 0 and odd_image == 0:
            layout.append(curr_col)
        else:
            layout[0].extend(curr_col)

        return {
            "content": {
                "projectMeta": self._project_meta.to_json(),
                "layout": layout,
                "annotations": annotations
            },
            "options": {
                **self._options
            }
        }
