from pathlib import Path
import yaml

import typing as t


def load_yaml_from_file(path: t.Union[str, Path], loader=yaml.Loader) -> t.Any:
    path = Path(path) if type(path) is str else path
    with path.open(encoding='utf-8') as file:
        return yaml.load(file, loader)
