"""Malloy MCP Server API models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelType(str, Enum):
    SOURCE = "source"
    NOTEBOOK = "notebook"


class CellType(str, Enum):
    MARKDOWN = "markdown"
    CODE = "code"


class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    TRINO = "trino"


class Error(BaseModel):
    code: str
    message: str


class About(BaseModel):
    readme: str


class Project(BaseModel):
    name: str


class Package(BaseModel):
    name: str
    description: str


class View(BaseModel):
    name: str
    annotations: list[str] = Field(default_factory=list)


class Source(BaseModel):
    name: str
    annotations: list[str] = Field(default_factory=list)
    views: list[View] = Field(default_factory=list)


class Query(BaseModel):
    name: str
    annotations: list[str] = Field(default_factory=list)


class NotebookCell(BaseModel):
    type: CellType
    text: str
    query_name: str | None = Field(None, alias="queryName")
    query_result: str | None = Field(None, alias="queryResult")


class Model(BaseModel):
    package_name: str = Field(alias="packageName")
    path: str
    type: ModelType


class CompiledModel(Model):
    malloy_version: str = Field(alias="malloyVersion")
    data_styles: Any = Field(alias="dataStyles")
    model_def: Any = Field(alias="modelDef")
    sources: list[Source]
    queries: list[Query]
    notebook_cells: list[NotebookCell] = Field(alias="notebookCells")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda x: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(x.split("_"))
        ),
    )


class QueryResult(BaseModel):
    """A Malloy query's results, its model def, and its data styles.
    
    Attributes:
        data_styles: Data style for rendering query results (opaque JSON string)
        model_def: Malloy model definition (opaque JSON string)
        query_result: Malloy query results (opaque JSON string)
    """
    data_styles: str = Field(alias="dataStyles", description="Data style for rendering query results")
    model_def: str = Field(alias="modelDef", description="Malloy model definition")
    query_result: str = Field(alias="queryResult", description="Malloy query results")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda x: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(x.split("_"))
        ),
    )


class Database(BaseModel):
    path: str
    size: int


class Schedule(BaseModel):
    resource: str
    schedule: str
    action: str
    connection: str
    last_run_time: float = Field(alias="lastRunTime")
    last_run_status: str = Field(alias="lastRunStatus")


class PostgresConnection(BaseModel):
    host: str
    port: int
    database_name: str = Field(alias="databaseName")
    user_name: str = Field(alias="userName")
    password: str
    connection_string: str = Field(alias="connectionString")


class BigqueryConnection(BaseModel):
    default_project_id: str = Field(alias="defaultProjectId")
    billing_project_id: str = Field(alias="billingProjectId")
    location: str
    service_account_key_json: str = Field(alias="serviceAccountKeyJson")
    maximum_bytes_billed: str = Field(alias="maximumBytesBilled")
    query_timeout_milliseconds: str = Field(alias="queryTimeoutMilliseconds")


class SnowflakeConnection(BaseModel):
    account: str
    username: str
    password: str
    warehouse: str
    database: str
    schema_name: str = Field(alias="schema")
    response_timeout_milliseconds: int = Field(alias="responseTimeoutMilliseconds")


class TrinoConnection(BaseModel):
    server: str
    port: float
    catalog: str
    schema_name: str = Field(alias="schema")
    user: str
    password: str


class Connection(BaseModel):
    name: str
    type: DatabaseType
    postgres_connection: PostgresConnection | None = Field(
        None, alias="postgresConnection"
    )
    bigquery_connection: BigqueryConnection | None = Field(
        None, alias="bigqueryConnection"
    )
    snowflake_connection: SnowflakeConnection | None = Field(
        None, alias="snowflakeConnection"
    )
    trino_connection: TrinoConnection | None = Field(None, alias="trinoConnection")
