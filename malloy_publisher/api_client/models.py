"""Malloy Publisher API models.

This module contains Pydantic models for the Malloy Publisher API.
These models handle data validation and serialization for API requests and responses.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelType(str, Enum):
    """Type of Malloy model.

    Attributes:
        SOURCE: A Malloy source model
        NOTEBOOK: A Malloy notebook model
    """

    SOURCE = "source"
    NOTEBOOK = "notebook"


class CellType(str, Enum):
    """Type of notebook cell.

    Attributes:
        MARKDOWN: A markdown cell
        CODE: A code cell
    """

    MARKDOWN = "markdown"
    CODE = "code"


class DatabaseType(str, Enum):
    """Type of database connection.

    Attributes:
        POSTGRES: PostgreSQL database
        BIGQUERY: Google BigQuery database
        SNOWFLAKE: Snowflake database
        TRINO: Trino database
    """

    POSTGRES = "postgres"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    TRINO = "trino"


class Error(BaseModel):
    """API error response.

    Attributes:
        code: Error code
        message: Error message
    """

    code: str
    message: str


class About(BaseModel):
    """Service metadata.

    Attributes:
        readme: README content
    """

    readme: str


class Project(BaseModel):
    """Project information.

    Attributes:
        name: Project name
    """

    name: str


class Package(BaseModel):
    """Package information.

    Attributes:
        name: Package name
        description: Package description
    """

    name: str
    description: str


class View(BaseModel):
    """View definition.

    Attributes:
        name: View name
        annotations: List of view annotations
    """

    name: str
    annotations: list[str] = Field(default_factory=list)


class Source(BaseModel):
    """Source definition.

    Attributes:
        name: Source name
        annotations: List of source annotations
        views: List of views in the source
    """

    name: str
    annotations: list[str] = Field(default_factory=list)
    views: list[View] = Field(default_factory=list)


class Query(BaseModel):
    """Query definition.

    Attributes:
        name: Query name
        annotations: List of query annotations
    """

    name: str
    annotations: list[str] = Field(default_factory=list)


class NotebookCell(BaseModel):
    """Notebook cell definition.

    Attributes:
        type: Type of cell (markdown or code)
        text: Cell content
        query_name: Optional name of the query in the cell
        query_result: Optional query result
    """

    type: CellType
    text: str
    query_name: str | None = Field(None, alias="queryName")
    query_result: str | None = Field(None, alias="queryResult")


class Model(BaseModel):
    """Model definition.

    Attributes:
        package_name: Name of the package containing the model
        path: Path to the model within the package
        type: Type of model (source or notebook)
    """

    package_name: str = Field(alias="packageName")
    path: str
    type: ModelType


class CompiledModel(Model):
    """Compiled model definition.

    Attributes:
        malloy_version: Version of Malloy used to compile the model
        data_styles: Data style definitions for rendering
        model_def: Compiled model definition
        sources: List of sources in the model
        queries: List of queries in the model
        notebook_cells: List of cells in the notebook (if applicable)
    """

    malloy_version: str = Field(alias="malloyVersion")
    data_styles: dict[str, Any] = Field(alias="dataStyles")
    model_def: dict[str, Any] = Field(alias="modelDef")
    sources: list[Source]
    queries: list[Query]
    notebook_cells: list[NotebookCell] = Field(alias="notebookCells")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda x: "".join(
            word.capitalize() if i > 0 else word for i, word in enumerate(x.split("_"))
        ),
    )


class QueryResult(BaseModel):
    """Query execution result.

    Attributes:
        data_styles: Data style definitions for rendering results
        model_def: Compiled model definition
        query_result: Query execution results
    """

    data_styles: str = Field(
        alias="dataStyles", description="Data style for rendering query results"
    )
    model_def: str = Field(alias="modelDef", description="Malloy model definition")
    query_result: str = Field(alias="queryResult", description="Malloy query results")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda x: "".join(
            word.capitalize() if i > 0 else word for i, word in enumerate(x.split("_"))
        ),
    )


class Database(BaseModel):
    """Database information.

    Attributes:
        path: Path to the database file
        size: Size of the database in bytes
    """

    path: str
    size: int


class Schedule(BaseModel):
    """Schedule information.

    Attributes:
        resource: Resource being scheduled
        schedule: Schedule definition
        action: Action to perform
        connection: Connection to use
        last_run_time: Timestamp of last run
        last_run_status: Status of last run
    """

    resource: str
    schedule: str
    action: str
    connection: str
    last_run_time: float = Field(alias="lastRunTime")
    last_run_status: str = Field(alias="lastRunStatus")


class PostgresConnection(BaseModel):
    """PostgreSQL connection configuration.

    Attributes:
        host: Database host
        port: Database port
        database_name: Name of the database
        user_name: Database username
        password: Database password
        connection_string: Full connection string
    """

    host: str
    port: int
    database_name: str = Field(alias="databaseName")
    user_name: str = Field(alias="userName")
    password: str
    connection_string: str = Field(alias="connectionString")


class BigqueryConnection(BaseModel):
    """BigQuery connection configuration.

    Attributes:
        default_project_id: Default project ID
        billing_project_id: Billing project ID
        location: Dataset location
        service_account_key_json: Service account key JSON
        maximum_bytes_billed: Maximum bytes to bill
        query_timeout_milliseconds: Query timeout in milliseconds
    """

    default_project_id: str = Field(alias="defaultProjectId")
    billing_project_id: str = Field(alias="billingProjectId")
    location: str
    service_account_key_json: str = Field(alias="serviceAccountKeyJson")
    maximum_bytes_billed: str = Field(alias="maximumBytesBilled")
    query_timeout_milliseconds: str = Field(alias="queryTimeoutMilliseconds")


class SnowflakeConnection(BaseModel):
    """Snowflake connection configuration.

    Attributes:
        account: Snowflake account
        username: Snowflake username
        password: Snowflake password
        warehouse: Snowflake warehouse
        database: Snowflake database
        schema_name: Snowflake schema
        response_timeout_milliseconds: Response timeout in milliseconds
    """

    account: str
    username: str
    password: str
    warehouse: str
    database: str
    schema_name: str = Field(alias="schema")
    response_timeout_milliseconds: int = Field(alias="responseTimeoutMilliseconds")


class TrinoConnection(BaseModel):
    """Trino connection configuration.

    Attributes:
        server: Trino server
        port: Trino port
        catalog: Trino catalog
        schema_name: Trino schema
        user: Trino user
        password: Trino password
    """

    server: str
    port: float
    catalog: str
    schema_name: str = Field(alias="schema")
    user: str
    password: str


class Connection(BaseModel):
    """Database connection configuration.

    Attributes:
        name: Connection name
        type: Type of database connection
        postgres_connection: PostgreSQL connection details (if applicable)
        bigquery_connection: BigQuery connection details (if applicable)
        snowflake_connection: Snowflake connection details (if applicable)
        trino_connection: Trino connection details (if applicable)
    """

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
