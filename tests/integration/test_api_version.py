import pytest
import pynautobot


class TestAPIVersioning:
    """Test API Versioning."""

    @pytest.fixture
    def nb_client_1_3(self, nb_client):
        """Setup a nb_client with API v1.3."""
        # Instantiate with a temp url and then replace
        nb_api = pynautobot.api("http://localhost", token=nb_client.token, api_version="1.3")
        nb_api.base_url = nb_client.base_url

        return nb_api

    @pytest.fixture
    def skipif_version(self, nb_client):
        """Retrieve the current Nautobot version and skip the test if less than 1.3."""
        status = nb_client.status()
        assert status
        assert status.get("nautobot-version")
        if status["nautobot-version"] < "1.3":
            pytest.skip("API versioning is only in Nautobot 1.3+")

        return status["nautobot-version"]

    @pytest.fixture
    def tag(self, nb_client):
        """Create a tag."""
        tag_name = "Test Tag"
        tag = nb_client.extras.tags.create(name=tag_name, slug=tag_name.lower().replace(" ", "_"))
        assert tag

        return tag

    def test_invalid_api_version(self, nb_client):
        """Verify Invalid api_version error response from Nautobot is handled gracefully."""
        with pytest.raises(pynautobot.core.query.RequestError) as _:
            nb_client.extras.tags.all(api_version="0.0")

    def test_tag_content_types(self, skipif_version, nb_client_1_3, tag):
        """Verify we can retrieve and update a tag's content types when using API v1.3."""
        assert skipif_version
        tag_1_3 = nb_client_1_3.extras.tags.get(id=tag.id)
        assert tag_1_3
        assert tag_1_3.content_types

        new_content_types = {"content_types": ["dcim.device"]}
        tag_1_3.update(new_content_types)
        tag_1_3 = nb_client_1_3.extras.tags.get(id=tag.id)
        assert tag_1_3.content_types == new_content_types["content_types"]
