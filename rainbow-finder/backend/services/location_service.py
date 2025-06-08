"""
Location Service

This service handles location-related operations including geocoding,
reverse geocoding, and distance calculations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import math
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from datetime import datetime

from shared.models.rainbow import Location


class LocationService:
    """Service for location-related operations including geocoding and distance calculations."""

    def __init__(self, user_agent: str = "rainbow-finder-app"):
        """Initialize the Location Service.
        
        Args:
            user_agent: User agent for geocoding service
        """
        self.logger = logging.getLogger(__name__)
        self.geolocator = Nominatim(user_agent=user_agent)
        self.logger.info("Location Service initialized")
        
    def _format_location(self, lat: float, lon: float, altitude: Optional[float] = None,
                        name: Optional[str] = None) -> Location:
        """Format location coordinates into a Location object.
        
        Args:
            lat: Latitude
            lon: Longitude
            altitude: Optional altitude in meters
            name: Optional location name
            
        Returns:
            Location object
        """
        return Location(
            latitude=lat,
            longitude=lon,
            altitude=altitude,
            name=name
        )
        
    def location_from_dict(self, location_dict: Dict[str, float]) -> Location:
        """Convert a dictionary with lat/lon to a Location object.
        
        Args:
            location_dict: Dictionary with latitude and longitude keys
            
        Returns:
            Location object
        """
        altitude = location_dict.get('altitude')
        name = location_dict.get('name') if isinstance(location_dict.get('name'), str) else None
        return self._format_location(
            location_dict['latitude'],
            location_dict['longitude'],
            altitude,
            name
        )

    def geocode(self, address: str) -> Optional[Location]:
        """Convert an address to geographic coordinates.
        
        Args:
            address: String address to geocode
            
        Returns:
            Location object with latitude and longitude, or None if not found
        """
        self.logger.info(f"Geocoding address: {address}")
        try:
            location = self.geolocator.geocode(address)
            if location:
                return self._format_location(
                    location.latitude,
                    location.longitude,
                    None,
                    location.address
                )
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.error(f"Geocoding error: {str(e)}")
            return None

    def reverse_geocode(self, location: Union[Location, Dict[str, float]]) -> Optional[Dict[str, str]]:
        """Convert geographic coordinates to an address.
        
        Args:
            location: Location object or dictionary with latitude and longitude
            
        Returns:
            Dictionary with address components, or None if not found
        """
        if isinstance(location, dict):
            lat, lon = location['latitude'], location['longitude']
        else:
            lat, lon = location.latitude, location.longitude
            
        self.logger.info(f"Reverse geocoding location: ({lat}, {lon})")
        
        try:
            location_info = self.geolocator.reverse((lat, lon))
            if location_info:
                return location_info.raw.get('address', {})
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.error(f"Reverse geocoding error: {str(e)}")
            return None

    def calculate_distance(self, point1: Union[Location, Dict[str, float]],
                           point2: Union[Location, Dict[str, float]]) -> float:
        """Calculate the distance between two geographic points using great circle distance.
        
        Args:
            point1: First location (Location object or dict with latitude, longitude)
            point2: Second location (Location object or dict with latitude, longitude)
            
        Returns:
            Distance in kilometers
        """
        # Extract coordinates from Location objects or dictionaries
        if isinstance(point1, dict):
            lat1, lon1 = point1['latitude'], point1['longitude']
        else:
            lat1, lon1 = point1.latitude, point1.longitude
            
        if isinstance(point2, dict):
            lat2, lon2 = point2['latitude'], point2['longitude']
        else:
            lat2, lon2 = point2.latitude, point2.longitude
        
        self.logger.info(f"Calculating distance between ({lat1}, {lon1}) and ({lat2}, {lon2})")
        
        # Use geopy's great_circle for accurate Earth distance calculation
        distance = great_circle((lat1, lon1), (lat2, lon2)).kilometers
        return distance
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points using the haversine formula.
        
        Args:
            lat1: Latitude of point 1 in degrees
            lon1: Longitude of point 1 in degrees
            lat2: Latitude of point 2 in degrees
            lon2: Longitude of point 2 in degrees
            
        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r

    def find_locations_in_radius(
        self,
        center: Union[Location, Dict[str, float]],
        radius_km: float,
        points_of_interest: Optional[List[Union[Location, Dict[str, Any]]]] = None
    ) -> List[Dict[str, Any]]:
        """Find locations within a specified radius of a center point.
        
        Args:
            center: Center location coordinates (Location object or dict)
            radius_km: Search radius in kilometers
            points_of_interest: Optional list of points to filter
            
        Returns:
            List of locations within the radius, each with distance from center
        """
        if isinstance(center, dict):
            center_loc = self.location_from_dict(center)
        else:
            center_loc = center
            
        self.logger.info(f"Finding locations within {radius_km}km of ({center_loc.latitude}, {center_loc.longitude})")
        
        results = []
        
        # If no points of interest provided, return empty list
        if not points_of_interest:
            self.logger.warning("No points of interest provided to filter")
            return results
            
        # Filter points of interest by distance
        for poi in points_of_interest:
            # Convert to Location object if it's a dict
            if isinstance(poi, dict):
                if 'latitude' not in poi or 'longitude' not in poi:
                    continue
                poi_loc = self.location_from_dict(poi)
            else:
                poi_loc = poi
                
            # Calculate distance
            distance = self.calculate_distance(center_loc, poi_loc)
            
            # Add to results if within radius
            if distance <= radius_km:
                results.append({
                    'location': poi_loc,
                    'distance': distance,
                    'bearing': self.calculate_bearing(center_loc, poi_loc),
                    'metadata': poi if isinstance(poi, dict) else {}
                })
                
        # Sort results by distance from center
        results.sort(key=lambda x: x['distance'])
        return results
        
    def calculate_bearing(self, point1: Union[Location, Dict[str, float]],
                          point2: Union[Location, Dict[str, float]]) -> float:
        """Calculate the bearing from point1 to point2.
        
        Args:
            point1: First location (Location object or dict with latitude, longitude)
            point2: Second location (Location object or dict with latitude, longitude)
            
        Returns:
            Bearing in degrees from North (0-360)
        """
        # Extract coordinates from Location objects or dictionaries
        if isinstance(point1, dict):
            lat1, lon1 = point1['latitude'], point1['longitude']
        else:
            lat1, lon1 = point1.latitude, point1.longitude
            
        if isinstance(point2, dict):
            lat2, lon2 = point2['latitude'], point2['longitude']
        else:
            lat2, lon2 = point2.latitude, point2.longitude
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Calculate bearing
        dlon = lon2_rad - lon1_rad
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
        bearing_rad = math.atan2(y, x)
        
        # Convert to degrees and normalize to 0-360
        bearing_deg = math.degrees(bearing_rad)
        bearing_normalized = (bearing_deg + 360) % 360
        
        return bearing_normalized
    
    def destination_point(self, start: Union[Location, Dict[str, float]],
                          bearing: float, distance_km: float) -> Location:
        """Calculate a destination point given a start point, bearing and distance.
        
        Args:
            start: Starting location (Location object or dict)
            bearing: Bearing in degrees (0 = North, 90 = East, etc)
            distance_km: Distance in kilometers
            
        Returns:
            Destination location
        """
        # Extract coordinates from Location object or dictionary
        if isinstance(start, dict):
            lat1, lon1 = start['latitude'], start['longitude']
            name = start.get('name')
        else:
            lat1, lon1 = start.latitude, start.longitude
            name = start.name
            
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        bearing_rad = math.radians(bearing)
        
        # Earth radius in kilometers
        R = 6371
        
        # Calculate destination point
        d_div_R = distance_km / R
        
        lat2_rad = math.asin(
            math.sin(lat1_rad) * math.cos(d_div_R) +
            math.cos(lat1_rad) * math.sin(d_div_R) * math.cos(bearing_rad)
        )
        
        lon2_rad = lon1_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(d_div_R) * math.cos(lat1_rad),
            math.cos(d_div_R) - math.sin(lat1_rad) * math.sin(lat2_rad)
        )
        
        # Convert back to degrees
        lat2 = math.degrees(lat2_rad)
        lon2 = math.degrees(lon2_rad)
        
        return self._format_location(lat2, lon2, None, name)