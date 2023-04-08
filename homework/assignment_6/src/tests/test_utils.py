"""
Tests for utilities.
"""
from raytape.utils import get_waypoints


class TestGetWayPoints:
    """Tests for getting waypoints between two points."""

    def test_npts(self):
        """Ensure get_waypoints works."""
        latlon1 = (44, -110)
        latlon2 = (45, -115)
        out = get_waypoints(latlon1, latlon2, 10)
        assert out.shape[0] == 10
