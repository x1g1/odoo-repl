from typing import overload, Any, Dict, Text

from typing_extensions import Literal

from odoo import models
from odoo.sql_db import Cursor

class Environment:
    cr: Cursor
    prefetch: Dict[Any, Any]  # Only some versions
    user: models.BaseModel
    uid: int
    registry: Dict[Text, Any]
    def __init__(
        self, cursor: Cursor, uid: int, context: Dict[Text, object]
    ) -> None: ...
    @overload
    def __getitem__(self, key: Literal["ir.model.access"]) -> models.IrModelAccess: ...
    @overload
    def __getitem__(self, key: Literal["ir.rule"]) -> models.IrRule: ...
    @overload
    def __getitem__(self, key: Literal["ir.model.data"]) -> models.IrModelData: ...
    @overload
    def __getitem__(self, key: Literal["ir.model.fields"]) -> models.IrModelFields: ...
    @overload
    def __getitem__(
        self, key: Literal["ir.module.module"]
    ) -> models.IrModuleModule: ...
    @overload
    def __getitem__(self, key: Literal["res.groups"]) -> models.ResGroups: ...
    @overload
    def __getitem__(self, key: Literal["res.users"]) -> models.ResUsers: ...
    @overload
    def __getitem__(self, key: Text) -> models.BaseModel: ...
    def ref(self, key: Text) -> models.BaseModel: ...
