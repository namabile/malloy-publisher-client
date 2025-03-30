"""Malloy MCP Server API client."""

from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

from malloy_mcp_server.api_client.models import (
    About,
    CompiledModel,
    Database,
    Error,
    Model,
    Package,
    Project,
    QueryResult,
    Schedule,
)

HTTP_ERROR_STATUS = 400


@dataclass
class QueryParams:
    """Parameters for executing a query."""

    project_name: str
    package_name: str
    path: str
    query: str | None = None
    source_name: str | None = None
    query_name: str | None = None
    version_id: str | None = None


class APIError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class MalloyAPIClient:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code >= HTTP_ERROR_STATUS:
            try:
                error = Error(**response.json())
                raise APIError(response.status_code, error.message)
            except ValidationError as e:
                raise APIError(response.status_code, str(e)) from e
        return response.json()

    def list_projects(self) -> list[Project]:
        """Returns a list of the Projects hosted on this server."""
        response = self.client.get("/api/v0/projects")
        data = self._handle_response(response)
        return [Project(**project) for project in data]

    def get_about(self, project_name: str) -> About:
        """Returns metadata about the publisher service."""
        response = self.client.get(f"/api/v0/projects/{project_name}/about")
        data = self._handle_response(response)
        return About(**data)

    def list_packages(self, project_name: str) -> list[Package]:
        """Returns a list of the Packages hosted on this server."""
        response = self.client.get(f"/api/v0/projects/{project_name}/packages")
        data = self._handle_response(response)
        return [Package(**package) for package in data]

    def get_package(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> Package:
        """Returns the package metadata."""
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}", params=params
        )
        data = self._handle_response(response)
        return Package(**data)

    def list_models(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Model]:
        """Returns a list of relative paths to the models in the package."""
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/models",
            params=params,
        )
        data = self._handle_response(response)
        for model in data:
            model["packageName"] = package_name
        return [Model(**model) for model in data]

    def get_model(self, project_name: str, package_name: str, model_name: str) -> Model:
        """Get a model by name."""
        data = self._handle_response(self.client.get(f"/api/v0/projects/{project_name}/packages/{package_name}/models/{model_name}"))
        data["path"] = data.pop("modelPath")
        data["packageName"] = package_name
        return Model(**data)

    def execute_query(self, params: QueryParams) -> QueryResult:
        """Returns a query and its results.
        
        Args:
            params: Query parameters containing:
                - project_name: Name of the project
                - package_name: Name of the package
                - path: Path to model within the package
                - query: Optional query string to execute on the model
                - source_name: Optional name of the source in the model
                - query_name: Optional name of a query to execute on a source
                - version_id: Optional version ID

        Returns:
            QueryResult: The query results containing:
                - data_styles: Data style for rendering query results
                - model_def: Malloy model definition
                - query_result: Malloy query results

        Raises:
            ValueError: If both query and query_name are specified, or if query_name
                is set without source_name.
            APIError: If the API request fails with a 400, 401, 404, 500, or 501 status code.
        """
        if params.query and params.query_name:
            raise ValueError("Cannot specify both query and query_name parameters")
        if params.query_name and not params.source_name:
            raise ValueError("source_name is required when query_name is specified")

        request_params = {
            "versionId": params.version_id,
            "query": params.query,
            "sourceName": params.source_name,
            "queryName": params.query_name
        }
        request_params = {k: v for k, v in request_params.items() if v is not None}

        try:
            response = self.client.get(
                f"/api/v0/projects/{params.project_name}/packages/{params.package_name}/queryResults/{params.path}",
                params=request_params
            )
            data = self._handle_response(response)
            return QueryResult(**data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise APIError(400, "Bad request - invalid query parameters") from e
            elif e.response.status_code == 401:
                raise APIError(401, "Unauthorized - authentication required") from e
            elif e.response.status_code == 404:
                raise APIError(404, "Not found - project, package, or model not found") from e
            elif e.response.status_code == 500:
                raise APIError(500, "Internal server error") from e
            elif e.response.status_code == 501:
                raise APIError(501, "Not implemented") from e
            raise

    def list_databases(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Database]:
        """Returns a list of relative paths to the databases embedded in the package."""
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/databases",
            params=params,
        )
        data = self._handle_response(response)
        return [Database(**db) for db in data]

    def list_schedules(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Schedule]:
        """Returns a list of running schedules."""
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/schedules",
            params=params,
        )
        data = self._handle_response(response)
        return [Schedule(**schedule) for schedule in data]

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> "MalloyAPIClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        self.close()
