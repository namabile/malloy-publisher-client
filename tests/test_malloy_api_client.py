"""Tests for the Malloy API client."""

import pytest
from typing import Generator
from malloy_mcp_server.api_client.client import MalloyAPIClient, QueryParams
from malloy_mcp_server.api_client.models import ModelType


@pytest.fixture
def client() -> Generator[MalloyAPIClient, None, None]:
    """Create a Malloy API client instance."""
    with MalloyAPIClient("http://localhost:4000") as client:
        yield client


def test_list_projects(client: MalloyAPIClient) -> None:
    """Test listing projects."""
    projects = client.list_projects()
    assert isinstance(projects, list)
    # At least one project should exist
    assert len(projects) > 0
    # Each project should have a name
    for project in projects:
        assert hasattr(project, "name")
        assert isinstance(project.name, str)
    # The home project should exist
    assert any(project.name == "home" for project in projects)


def test_get_about(client: MalloyAPIClient) -> None:
    """Test getting about information."""
    about = client.get_about("home")
    assert hasattr(about, "readme")
    assert isinstance(about.readme, str)


def test_list_packages(client: MalloyAPIClient) -> None:
    """Test listing packages."""
    packages = client.list_packages("home")
    assert isinstance(packages, list)
    # Each package should have a name and description
    for package in packages:
        assert hasattr(package, "name")
        assert hasattr(package, "description")
        assert isinstance(package.name, str)
        assert isinstance(package.description, str)


def test_get_package(client: MalloyAPIClient) -> None:
    """Test getting package details."""
    packages = client.list_packages("home")
    assert len(packages) > 0
    package_name = packages[0].name

    package = client.get_package("home", package_name)
    assert hasattr(package, "name")
    assert hasattr(package, "description")
    assert isinstance(package.name, str)
    assert isinstance(package.description, str)


def test_list_models(client: MalloyAPIClient) -> None:
    """Test listing models."""
    packages = client.list_packages("home")
    assert len(packages) > 0
    package_name = packages[0].name

    models = client.list_models("home", package_name)
    assert isinstance(models, list)
    # Each model should have required attributes
    for model in models:
        assert hasattr(model, "package_name")
        assert hasattr(model, "path")
        assert hasattr(model, "type")
        assert isinstance(model.package_name, str)
        assert isinstance(model.path, str)


def test_get_model(client: MalloyAPIClient) -> None:
    """Test getting model details."""
    packages = client.list_packages("home")
    assert len(packages) > 0
    package_name = packages[0].name

    models = client.list_models("home", package_name)
    assert len(models) > 0
    model_path = models[0].path

    model = client.get_model("home", package_name, model_path)
    assert hasattr(model, "package_name")
    assert hasattr(model, "path")
    assert hasattr(model, "type")
    assert isinstance(model.package_name, str)
    assert isinstance(model.path, str)
    assert isinstance(model.type, ModelType)


def test_execute_query(client: MalloyAPIClient) -> None:
    """Test executing a query."""
    # Test with a named query
    query_params = QueryParams(
        project_name="home",
        package_name="faa",
        path="flights.malloy",
        source_name="flights",
        query_name="top_carriers"
    )

    result = client.execute_query(query_params)
    assert hasattr(result, "data_styles")
    assert hasattr(result, "model_def")
    assert hasattr(result, "query_result")
    assert isinstance(result.data_styles, str)
    assert isinstance(result.model_def, str)
    assert isinstance(result.query_result, str)

    # Test error cases
    with pytest.raises(ValueError, match="Cannot specify both query and query_name parameters"):
        client.execute_query(QueryParams(
            project_name="home",
            package_name="faa",
            path="flights.malloy",
            query="test query",
            query_name="test_query"
        ))

    with pytest.raises(ValueError, match="source_name is required when query_name is specified"):
        client.execute_query(QueryParams(
            project_name="home",
            package_name="faa",
            path="flights.malloy",
            query_name="test_query"
        ))


def test_list_databases(client: MalloyAPIClient) -> None:
    """Test listing databases."""
    packages = client.list_packages("home")
    assert len(packages) > 0
    package_name = packages[0].name

    databases = client.list_databases("home", package_name)
    assert isinstance(databases, list)
    # Each database should have required attributes
    for database in databases:
        assert hasattr(database, "path")
        assert hasattr(database, "size")
        assert isinstance(database.path, str)
        assert isinstance(database.size, int)


def test_list_schedules(client: MalloyAPIClient) -> None:
    """Test listing schedules."""
    packages = client.list_packages("home")
    assert len(packages) > 0
    package_name = packages[0].name

    schedules = client.list_schedules("home", package_name)
    assert isinstance(schedules, list)
    # Each schedule should have required attributes
    for schedule in schedules:
        assert hasattr(schedule, "resource")
        assert hasattr(schedule, "schedule")
        assert hasattr(schedule, "action")
        assert hasattr(schedule, "connection")
        assert hasattr(schedule, "last_run_time")
        assert hasattr(schedule, "last_run_status")
        assert isinstance(schedule.resource, str)
        assert isinstance(schedule.schedule, str)
        assert isinstance(schedule.action, str)
        assert isinstance(schedule.connection, str)
        assert isinstance(schedule.last_run_time, float)
        assert isinstance(schedule.last_run_status, str) 