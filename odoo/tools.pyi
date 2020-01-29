from typing import Any, Dict, Optional, Sequence, Text, Union

class _configmanager:
    options: Dict[str, Union[str, bool, int]]
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Union[str, bool, int]) -> None: ...
    def parse_config(self, args: Optional[Sequence[Text]] = ...) -> None: ...

config: _configmanager