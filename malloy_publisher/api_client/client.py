"""Malloy Publisher API client.

This module provides a Python client for interacting with the Malloy Publisher API.
The client handles authentication, request formatting, and response parsing.
"""

from dataclasses import dataclass
from typing import Any, cast

import httpx
from pydantic import ValidationError

from malloy_publisher.api_client.models import (
    About,
    Database,
    Error,
    Model,
    Package,
    Project,
    QueryResult,
    Schedule,
)

# HTTP Status Codes
HTTP_ERROR_STATUS = 400
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501


@dataclass
class QueryParams:
    """Parameters for executing a query.

    Attributes:
        project_name: Name of the project to query
        package_name: Name of the package containing the model
        path: Path to the model within the package
        query: Optional query string to execute on the model
        source_name: Optional name of the source in the model
        query_name: Optional name of a query to execute on a source
        version_id: Optional version ID of the package
    """

    project_name: str
    package_name: str
    path: str
    query: str | None = None
    source_name: str | None = None
    query_name: str | None = None
    version_id: str | None = None


class APIError(Exception):
    """Exception raised for API-related errors.

    Attributes:
        status_code: HTTP status code of the error
        message: Error message from the API
    """

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class MalloyAPIClient:
    """Client for interacting with the Malloy Publisher API.

    This client provides methods for interacting with the Malloy Publisher API,
    including listing projects, packages, models, and executing queries.

    Attributes:
        base_url: Base URL of the API server
        api_key: Optional API key for authentication
        client: HTTP client for making requests
    """

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL of the API server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate errors.

        Args:
            response: HTTP response from the API

        Returns:
            Dict containing the parsed JSON response

        Raises:
            APIError: If the response indicates an error
        """
        if response.status_code >= HTTP_ERROR_STATUS:
            try:
                error = Error.model_validate(response.json())
                raise APIError(response.status_code, error.message)
            except ValidationError as e:
                raise APIError(response.status_code, str(e)) from e
        return cast(dict[str, Any], response.json())

    def list_projects(self) -> list[Project]:
        """Returns a list of the Projects hosted on this server.

        Returns:
            List of Project objects containing project names

        Raises:
            APIError: If the API request fails
        """
        response = self.client.get("/api/v0/projects")
        data = self._handle_response(response)
        return [Project.model_validate(project) for project in data]

    def get_about(self, project_name: str) -> About:
        """Returns metadata about the publisher service.

        Args:
            project_name: Name of the project

        Returns:
            About object containing service metadata

        Raises:
            APIError: If the API request fails
        """
        response = self.client.get(f"/api/v0/projects/{project_name}/about")
        data = self._handle_response(response)
        return About.model_validate(data)

    def list_packages(self, project_name: str) -> list[Package]:
        """Returns a list of the Packages hosted on this server.

        Args:
            project_name: Name of the project

        Returns:
            List of Package objects containing package information

        Raises:
            APIError: If the API request fails
        """
        response = self.client.get(f"/api/v0/projects/{project_name}/packages")
        data = self._handle_response(response)
        return [Package.model_validate(package) for package in data]

    def get_package(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> Package:
        """Returns the package metadata.

        Args:
            project_name: Name of the project
            package_name: Name of the package
            version_id: Optional version ID of the package

        Returns:
            Package object containing package metadata

        Raises:
            APIError: If the API request fails
        """
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}", params=params
        )
        data = self._handle_response(response)
        return Package.model_validate(data)

    def list_models(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Model]:
        """Returns a list of relative paths to the models in the package.

        Args:
            project_name: Name of the project
            package_name: Name of the package
            version_id: Optional version ID of the package

        Returns:
            List of Model objects containing model information

        Raises:
            APIError: If the API request fails
        """
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/models",
            params=params,
        )
        data = self._handle_response(response)
        models_data = cast(list[dict[str, Any]], data)
        for model_data in models_data:
            model_data["packageName"] = package_name
        return [Model.model_validate(model) for model in models_data]

    def get_model(self, project_name: str, package_name: str, model_name: str) -> Model:
        """Get a model by name.

        Args:
            project_name: Name of the project
            package_name: Name of the package
            model_name: Name of the model

        Returns:
            Model object containing model information

        Raises:
            APIError: If the API request fails
        """
        url_parts = [
            "/api/v0/projects",
            project_name,
            "packages",
            package_name,
            "models",
            model_name,
        ]
        url = "/".join(url_parts)
        data = self._handle_response(self.client.get(url))
        model_data = data
        model_data["path"] = model_data.pop("modelPath")
        model_data["packageName"] = package_name
        return Model.model_validate(model_data)

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
            APIError: If the API request fails with a client or server error.
        """
        if params.query and params.query_name:
            raise ValueError("Cannot specify both query and query_name parameters")
        if params.query_name and not params.source_name:
            raise ValueError("source_name is required when query_name is specified")

        request_params = {
            "versionId": params.version_id,
            "query": params.query,
            "sourceName": params.source_name,
            "queryName": params.query_name,
        }
        request_params = {k: v for k, v in request_params.items() if v is not None}

        try:
            url = (
                f"/api/v0/projects/{params.project_name}/packages/"
                f"{params.package_name}/queryResults/{params.path}"
            )
            response = self.client.get(url, params=request_params)
            data = self._handle_response(response)
            return QueryResult.model_validate(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == HTTP_BAD_REQUEST:
                msg = "Bad request - invalid query parameters"
                raise APIError(HTTP_BAD_REQUEST, msg) from e
            elif e.response.status_code == HTTP_UNAUTHORIZED:
                msg = "Unauthorized - authentication required"
                raise APIError(HTTP_UNAUTHORIZED, msg) from e
            elif e.response.status_code == HTTP_NOT_FOUND:
                msg = "Not found - project, package, or model not found"
                raise APIError(HTTP_NOT_FOUND, msg) from e
            elif e.response.status_code == HTTP_SERVER_ERROR:
                raise APIError(HTTP_SERVER_ERROR, "Internal server error") from e
            elif e.response.status_code == HTTP_NOT_IMPLEMENTED:
                raise APIError(HTTP_NOT_IMPLEMENTED, "Not implemented") from e
            raise

    def list_databases(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Database]:
        """Returns a list of relative paths to the databases embedded in the package.

        Args:
            project_name: Name of the project
            package_name: Name of the package
            version_id: Optional version ID of the package

        Returns:
            List of Database objects containing database information

        Raises:
            APIError: If the API request fails
        """
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/databases",
            params=params,
        )
        data = self._handle_response(response)
        return [Database.model_validate(db) for db in data]

    def list_schedules(
        self,
        project_name: str,
        package_name: str,
        version_id: str | None = None,
    ) -> list[Schedule]:
        """Returns a list of running schedules.

        Args:
            project_name: Name of the project
            package_name: Name of the package
            version_id: Optional version ID of the package

        Returns:
            List of Schedule objects containing schedule information

        Raises:
            APIError: If the API request fails
        """
        params = {"versionId": version_id} if version_id else {}
        response = self.client.get(
            f"/api/v0/projects/{project_name}/packages/{package_name}/schedules",
            params=params,
        )
        data = self._handle_response(response)
        return [Schedule.model_validate(schedule) for schedule in data]

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> "MalloyAPIClient":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Context manager exit."""
        self.close()
