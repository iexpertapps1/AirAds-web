/**
 * GeoJSON Point as returned by the backend.
 * IMPORTANT: coordinates are [lng, lat] — GeoJSON standard.
 * Leaflet expects [lat, lng] — always swap when passing to Leaflet:
 *   leafletLatLng = [point.coordinates[1], point.coordinates[0]]
 */
export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [lng: number, lat: number];
}
