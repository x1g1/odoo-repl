from typing import Any, Dict, Optional, Text

def load_information_from_description_file(module: Text) -> Dict[Text, Any]: ...
def get_module_path(
    module: Text, downloaded: bool = ..., display_warning: bool = ...
) -> Optional[Text]: ...
