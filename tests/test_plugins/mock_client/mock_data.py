import json
import pathlib

import fca_api
import pydantic


class PydanticModel:
    @staticmethod
    def to_dict(obj: pydantic.BaseModel) -> dict:
        return {
            "type": "PydanticModel",
            "module": obj.__module__,
            "class": obj.__class__.__name__,
            "data": obj.model_dump(mode="json", by_alias=True),
        }

    @staticmethod
    def from_dict(d: dict) -> pydantic.BaseModel:
        assert d["type"] == "PydanticModel"
        module = __import__(d["module"], fromlist=[d["class"]])
        cls = getattr(module, d["class"])
        return cls.model_validate(d["data"])


class MockMultipageListLoaded:
    def __init__(self, cached_file: pathlib.Path):
        self.cached_file = cached_file
        self._data = None


class MockMultipageListReadOnly:
    data: dict
    cur_index: int = 0

    def __init__(self, data: dict):
        self.data = data
        self.cur_index = 0

    def _get_next_call(self, exp_name: str):
        if self.cur_index >= len(self.data["calls"]):
            raise IndexError(f"No more calls in cached data, expected call to {exp_name}")
        call = self.data["calls"][self.cur_index]
        assert call["call"] == exp_name, f"Expected call to {exp_name}, got call to {call['call']}"
        self.cur_index += 1
        return call

    def local_items(self):
        call = self._get_next_call("local_items")
        return [PydanticModel.from_dict(el) for el in call["out"]]


class MockMultipageListSource:
    cached_file: pathlib.Path
    src: fca_api.types.pagination.MultipageList
    data: dict

    def __init__(self, cached_file: pathlib.Path, src: fca_api.types.pagination.MultipageList):
        self.cached_file = cached_file
        self.src = src
        self.data = {"type": "MultipageList", "calls": []}

    def local_items(self):
        out = self.src.local_items()
        self.data["calls"].append({"call": "local_items", "out": [PydanticModel.to_dict(el) for el in out]})
        self.flush()
        return out

    def get_state(self):
        return self.data

    def flush(self):
        with self.cached_file.open("w") as f:
            json.dump(self.get_state(), f, indent=2, sort_keys=True)
