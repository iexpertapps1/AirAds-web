import { useEffect, useRef } from 'react';
import type { GeoJSONPoint } from '@/shared/types/geo';
import styles from './GPSMap.module.css';

interface GPSMapProps {
  point: GeoJSONPoint;
  onDrag?: ((latLng: [number, number]) => void) | undefined;
  draggable?: boolean | undefined;
  height?: string | undefined;
  zoom?: number | undefined;
}

export function GPSMap({ point, onDrag, draggable = false, height = '240px', zoom = 15 }: GPSMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import('leaflet').Map | null>(null);
  const markerRef = useRef<import('leaflet').Marker | null>(null);

  // GeoJSON [lng, lat] → Leaflet [lat, lng]
  const leafletLat = point.coordinates[1];
  const leafletLng = point.coordinates[0];

  useEffect(() => {
    if (!containerRef.current) return;
    if (mapRef.current) return; // already initialised

    let cancelled = false;

    void import('leaflet').then((L) => {
      if (cancelled || !containerRef.current) return;

      // Leaflet CSS must be loaded
      const existing = document.getElementById('leaflet-css');
      if (!existing) {
        const link = document.createElement('link');
        link.id = 'leaflet-css';
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }

      const map = L.map(containerRef.current, {
        center: [leafletLat, leafletLng],
        zoom,
        zoomControl: true,
        attributionControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      }).addTo(map);

      const marker = L.marker([leafletLat, leafletLng], {
        draggable,
        title: 'Vendor location',
        alt: 'Vendor location pin',
      }).addTo(map);

      if (draggable && onDrag) {
        marker.on('dragend', () => {
          const pos = marker.getLatLng();
          onDrag([pos.lat, pos.lng]);
        });
      }

      mapRef.current = map;
      markerRef.current = marker;
    });

    return () => {
      cancelled = true;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update marker + view when point changes
  useEffect(() => {
    const map = mapRef.current;
    const marker = markerRef.current;
    if (!map || !marker) return;
    const latLng: [number, number] = [leafletLat, leafletLng];
    marker.setLatLng(latLng);
    map.setView(latLng, map.getZoom());
  }, [leafletLat, leafletLng]);

  // Update draggable state
  useEffect(() => {
    const marker = markerRef.current;
    if (!marker) return;
    if (draggable) {
      marker.dragging?.enable();
    } else {
      marker.dragging?.disable();
    }
  }, [draggable]);

  // Cleanup
  useEffect(() => {
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={styles.map}
      style={{ ['--map-height' as string]: height } as React.CSSProperties}
      aria-label={`Map showing location at latitude ${leafletLat.toFixed(6)}, longitude ${leafletLng.toFixed(6)}`}
      role="img"
    />
  );
}
