import mousebender.simple
import pytest

from simpleindex.routes import PathRoute, URLRoute


@pytest.mark.asyncio
async def test_path_route_directory(tmp_path):
    """An HTML document is built from a local directory."""
    directory = tmp_path.joinpath("my-package")
    directory.mkdir()

    # This should not match since it is from another project.
    directory.joinpath("other_package-2.0-py2.py3-none-any.whl").touch()

    # These should match.
    project_files = [
        "my-package-1.0.tar.gz",
        "my_package-1.0-py2.py3-none-any.whl",
    ]
    for name in project_files:
        directory.joinpath(name).touch()

    route = PathRoute(to=f"{directory.parent}/{{project}}")
    resp = await route.get("my-package", {"project": "my-package"})
    assert resp.status_code == 200

    links = mousebender.simple.parse_archive_links(resp.text)
    assert [link.filename for link in links] == project_files
    assert [link.url for link in links] == [f"./{n}" for n in project_files]


@pytest.mark.asyncio
async def test_path_route_file(tmp_path):
    """A local file route simply serves the file as-is."""
    html_file = tmp_path.joinpath("project.html")
    html_file.write_text("<body>test content</body>")

    route = PathRoute(to=f"{html_file.parent}/{{project}}.html")
    resp = await route.get("project", {"project": "project"})
    assert resp.status_code == 200
    assert resp.text == "<body>test content</body>"


@pytest.mark.asyncio
async def test_path_route_invalid(tmp_path):
    """404 is returned if the path does not point to a file or directory.
    """
    route = PathRoute(to=f"{tmp_path}/does-not-exist")
    resp = await route.get("does-not-exist", {})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_url_route(httpx_mock):
    httpx_mock.add_response(
        url="http://example.com/simple/package/",
        data=b"<body>test content</body>",
    )
    route = URLRoute(to="http://example.com/simple/{project}/")
    resp = await route.get("package", {"project": "package"})
    assert resp.text == "<body>test content</body>"
