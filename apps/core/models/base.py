import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Optional, Any, Sequence, Union, Mapping, Dict

from sqlalchemy import Executable, util, ScalarResult
from sqlalchemy.engine import TupleResult
from sqlalchemy.orm.session import _EntityBindKey, _PKIdentityArgument
from sqlalchemy.orm._typing import OrmExecuteOptionsParameter, _O
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.selectable import ForUpdateParameter, Select
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseModel(SQLModel, ABC):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.now(tz=timezone.utc), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True))


class SoftDeleteSession(AsyncSession):
    async def exec(
        self,
        statement: Union[Select, SelectOfScalar, Executable],
        *,
        params: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]] = None,
        execution_options: Mapping[str, Any] = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> Union[TupleResult, ScalarResult]:
        if isinstance(statement, (Select, SelectOfScalar)):
            statement = statement.where(statement.columns.deleted_at.is_(None))

        results = await super().exec(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            _parent_execute_state=_parent_execute_state,
            _add_event=_add_event,
        )

        if isinstance(statement, SelectOfScalar) and hasattr(results, "scalars"):
            return results.scalars()
        return results

    async def exec_all(self, statement, *args, **kwargs):
        return await super().exec(statement, *args, **kwargs)

    async def get(
        self,
        entity: _EntityBindKey[_O],
        ident: _PKIdentityArgument,
        *,
        options: Optional[Sequence[ORMOption]] = None,
        populate_existing: bool = False,
        with_for_update: ForUpdateParameter = None,
        identity_token: Optional[Any] = None,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
    ) -> Optional[_O]:
        instance = await super().get(
            entity,
            ident,
            options=options,
            populate_existing=populate_existing,
            with_for_update=with_for_update,
            identity_token=identity_token,
            execution_options=execution_options
        )
        if instance and getattr(instance, "deleted_at", None) is None:
            return instance
        return None

    async def get_all(
        self,
        entity: _EntityBindKey[_O],
        ident: _PKIdentityArgument,
        *,
        options: Optional[Sequence[ORMOption]] = None,
        populate_existing: bool = False,
        with_for_update: Optional[ForUpdateParameter] = None,
        identity_token: Optional[Any] = None,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
    ) -> Optional[_O]:
        instance = await super().get(
            entity,
            ident,
            options=options,
            populate_existing=populate_existing,
            with_for_update=with_for_update,
            identity_token=identity_token,
            execution_options=execution_options
        )
        return instance

    async def delete(self, instance):
        instance.deleted_at = datetime.now(tz=timezone.utc)
        self.add(instance)
        await self.commit()

    async def hard_delete(self, instance):
        await super().delete(instance)
        await self.commit()
