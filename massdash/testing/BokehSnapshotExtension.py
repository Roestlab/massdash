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

        BokehSnapshotExtension.compare_json(json_snapshot, json_serialized)

    def extract_bokeh_json(self, html: str) -> str:
        parser = BokehHTMLParser()
        parser.feed(html)
        return json.loads(parser.bokehJson)

    @staticmethod
    def compare_json(json1, json2):
        if isinstance(json1, dict) and isinstance(json2, dict):
            for key in json1.keys():
                if key == 'id':
                    continue
                if key not in json2 or not BokehSnapshotExtension.compare_json(json1[key], json2[key]):
                    return False
            return True
        elif isinstance(json1, list) and isinstance(json2, list):
            if len(json1) != len(json2):
                return False
            for item1, item2 in zip(json1, json2):
                if not BokehSnapshotExtension.compare_json(item1, item2):
                    return False
            return True
        else:
            return json1 == json2
 
    def _read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ):
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L139
        try:
            with open(snapshot_location, 'r') as f:
                a = f.read()
                print(a)
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