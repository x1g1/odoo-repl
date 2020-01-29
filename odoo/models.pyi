# Instead of Union[Literal[False], ...] we use Optional[...]
# This is less correct, but mypy handles it better

# Maybe it's possible and nice to make a distinction between uni- and multi-records

import types
from typing import (
    overload,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Text,
    Tuple,
    TypeVar,
    Union,
)

from typing_extensions import TypedDict

from odoo.api import Environment
from odoo.fields import Field

T = TypeVar("T")
AnyModel = TypeVar("AnyModel")

class BaseModel:
    _fields: Dict[Text, Field]
    _table: Text
    _name: Text
    _defaults: Dict[Text, object]
    _constraint_methods: List[_Constrainer]
    env: Environment
    _ids: Sequence[int]
    id: int
    display_name: Text
    def browse(self: AnyModel, ids: Union[int, Sequence[int]]) -> AnyModel: ...
    def sudo(self: AnyModel, user: Union[int, ResUsers]) -> AnyModel: ...
    def with_context(
        self: AnyModel, ctx: Dict[Text, Any] = ..., **kwargs: Any
    ) -> AnyModel: ...
    def search(
        self: AnyModel,
        args: Sequence[Union[Text, Tuple[Text, Text, object]]],
        offset: int = ...,
        limit: Optional[int] = ...,
        order: Optional[Text] = ...,
        count: bool = ...,
    ) -> AnyModel: ...
    @overload
    def mapped(self, func: Callable[[BaseModel], T]) -> List[T]: ...
    @overload
    def mapped(self, func: Text) -> Any: ...
    def get_xml_id(self) -> Dict[int, Text]: ...
    def fields_view_get(
        self, view_id: Optional[int] = ..., view_type: Text = ...
    ) -> _FieldView: ...
    def __iter__(self: AnyModel) -> Iterator[AnyModel]: ...
    def __or__(self: AnyModel, other: AnyModel) -> AnyModel: ...
    def __len__(self) -> int: ...

class _Constrainer(types.FunctionType):
    _constrains: Tuple[Text]

class _FieldView(TypedDict):
    # Very incomplete
    arch: Text

# These don't actually live in odoo.models
class IrModelAccess(BaseModel):
    active: bool
    group_id: ResGroups
    perm_read: bool
    perm_write: bool
    perm_create: bool
    perm_unlink: bool

class IrRule(BaseModel):
    active: bool
    groups: ResGroups
    domain_force: Optional[Text]
    perm_read: bool
    perm_write: bool
    perm_create: bool
    perm_unlink: bool
    def _eval_context(self) -> Dict[Any, Any]: ...

class IrModelData(BaseModel):
    module: Text
    name: Text

class IrModelFields(BaseModel):
    ttype: Text
    name: Text
    model: Text
    relation: Optional[Text]
    field_description: Text
    modules: Text

class IrModuleModule(BaseModel):
    state: Text
    installed_version: Text

class ResGroups(BaseModel):
    name: Text

class ResUsers(BaseModel):
    login: Text
