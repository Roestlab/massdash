from typing import Any
from bokeh.embed import file_html
import json
from syrupy.data import SnapshotCollection
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.types import SerializableData
from bokeh.resources import CDN
from html.parser import HTMLParser

class BokehHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording = False # boolean flag to indicate if we are currently recording the data
        self.bokehJson = None # data to extract

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and self.bokehJson is None:
            attrs_dict = dict(attrs)
            if attrs_dict.get('type') == 'application/json':
                self.recording = True

    def handle_endtag(self, tag):
        if tag == 'script' and self.recording:
            self.recording = False

    def handle_data(self, data):
        if self.recording and self.bokehJson is None:
            self.bokehJson = data

class BokehSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension = "html"

    def matches(self, *, serialized_data, snapshot_data):
        json_snapshot = self.extract_bokeh_json(snapshot_data)
        json_serialized = self.extract_bokeh_json(serialized_data)
        
        # get the keys which store the json
        # NOTE: keys are unique identifiers and are not supposed to be equal 
        # but the json objects they contain should be equal
        key_json_snapshot = list(json_snapshot.keys())[0] 
        key_json_serialized = list(json_serialized.keys())[0] 

        return BokehSnapshotExtension.compare_json(json_snapshot[key_json_snapshot], json_serialized[key_json_serialized])

    def extract_bokeh_json(self, html: str) -> str:
        parser = BokehHTMLParser()
        parser.feed(html)
        return json.loads(parser.bokehJson)

    @staticmethod
    def compare_json(json1, json2):
        if isinstance(json1, dict) and isinstance(json2, dict):
            for key in json1.keys():
                if key not in json2:
                    print(f'Key {key} not in second json')
                    return False
                elif key not in ['id', 'root_ids']: # add keys to ignore here
                    pass
                elif not BokehSnapshotExtension.compare_json(json1[key], json2[key]):
                    print(f'Values for key {key} not equal')
                    return False
            return True
        elif isinstance(json1, list) and isinstance(json2, list):
            if len(json1) != len(json2):
                print('Lists have different lengths')
                return False
            # lists are unordered so we need to compare every element one by one
            for i in json1:
                if isinstance(i, dict):
                    # find the corresponding dictionary in json2
                    for j in json2:
                        if j['type'] == i['type']:
                            if not BokehSnapshotExtension.compare_json(i, j):
                                print(f'Element {i} not equal to {j}')
                                return False
                            return True
                    print(f'Element {i} not in second list')
                    return False
                else:
                    return json1[i] == json2[i]
            return True
        else:
            if json1 != json2:
                print(f'Values not equal: {json1} != {json2}')
            return json1 == json2

    def _read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ):
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L139
        try:
            with open(snapshot_location, 'r') as f:
                a = f.read()
                return a
        except OSError:
            return None

    @classmethod
    def _write_snapshot_collection(
        cls, *, snapshot_collection: SnapshotCollection
    ) -> None:
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L161
        
        filepath, data = (
            snapshot_collection.location,
            next(iter(snapshot_collection)).data,
        )
        with open(filepath, 'w') as f:
            f.write(data)

    def serialize(self, data: SerializableData, **kwargs: Any) -> str:
        return file_html(data, CDN)