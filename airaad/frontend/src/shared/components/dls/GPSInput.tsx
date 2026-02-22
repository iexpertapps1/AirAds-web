import { useState, useCallback } from 'react';
import { MapPin, Crosshair, AlertCircle } from 'lucide-react';
import { Button } from '@/shared/components/dls/Button';
import { GPSMap } from '@/shared/components/dls/GPSMap';
import type { GeoJSONPoint } from '@/shared/types/geo';
import { logger } from '@/shared/utils/logger';
import styles from './GPSInput.module.css';

interface GPSInputProps {
  label: string;
  value: GeoJSONPoint | null;
  onChange: (point: GeoJSONPoint | null) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  id: string;
}

export function GPSInput({ label, value, onChange, error, required, disabled, id }: GPSInputProps) {
  const [locating, setLocating] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);

  const lat = value ? value.coordinates[1] : '';
  const lng = value ? value.coordinates[0] : '';

  function handleLatChange(raw: string) {
    const parsed = parseFloat(raw);
    if (!isNaN(parsed) && value) {
      onChange({ type: 'Point', coordinates: [value.coordinates[0], parsed] });
    } else if (!isNaN(parsed)) {
      onChange({ type: 'Point', coordinates: [0, parsed] });
    }
  }

  function handleLngChange(raw: string) {
    const parsed = parseFloat(raw);
    if (!isNaN(parsed) && value) {
      onChange({ type: 'Point', coordinates: [parsed, value.coordinates[1]] });
    } else if (!isNaN(parsed)) {
      onChange({ type: 'Point', coordinates: [parsed, 0] });
    }
  }

  const handleMapDrag = useCallback(
    (latLng: [number, number]) => {
      // Leaflet gives [lat, lng] — convert to GeoJSON [lng, lat]
      onChange({ type: 'Point', coordinates: [latLng[1], latLng[0]] });
    },
    [onChange],
  );

  function handleUseMyLocation() {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser.');
      return;
    }
    setLocating(true);
    setGeoError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        // GeoJSON: [lng, lat]
        onChange({ type: 'Point', coordinates: [pos.coords.longitude, pos.coords.latitude] });
        setLocating(false);
      },
      (err) => {
        logger.warn('Geolocation error:', err.message);
        setGeoError('Could not get your location. Please enter coordinates manually.');
        setLocating(false);
      },
      { timeout: 10_000 },
    );
  }

  const errorId = `${id}-error`;
  const displayError = error ?? geoError;

  return (
    <div className={styles.wrapper}>
      <div className={styles.labelRow}>
        <label className={styles.label}>
          <MapPin size={14} strokeWidth={1.5} aria-hidden="true" />
          {label}
          {required && <span className={styles.required} aria-hidden="true"> *</span>}
        </label>
        <Button
          variant="secondary"
          size="compact"
          leftIcon={<Crosshair size={14} strokeWidth={1.5} />}
          onClick={handleUseMyLocation}
          loading={locating}
          disabled={disabled}
          type="button"
        >
          Use my location
        </Button>
      </div>

      <div className={styles.coordRow}>
        <div className={styles.coordField}>
          <label htmlFor={`${id}-lat`} className={styles.coordLabel}>
            Latitude
          </label>
          <input
            id={`${id}-lat`}
            type="number"
            step="any"
            min={-90}
            max={90}
            className={[styles.coordInput, displayError ? styles.hasError : ''].join(' ')}
            value={lat}
            onChange={(e) => handleLatChange(e.target.value)}
            disabled={disabled}
            aria-describedby={displayError ? errorId : undefined}
            aria-invalid={displayError ? 'true' : undefined}
            placeholder="e.g. 24.8607"
          />
        </div>
        <div className={styles.coordField}>
          <label htmlFor={`${id}-lng`} className={styles.coordLabel}>
            Longitude
          </label>
          <input
            id={`${id}-lng`}
            type="number"
            step="any"
            min={-180}
            max={180}
            className={[styles.coordInput, displayError ? styles.hasError : ''].join(' ')}
            value={lng}
            onChange={(e) => handleLngChange(e.target.value)}
            disabled={disabled}
            placeholder="e.g. 67.0011"
          />
        </div>
      </div>

      {displayError && (
        <span id={errorId} className={styles.error} role="alert">
          <AlertCircle size={12} strokeWidth={1.5} aria-hidden="true" />
          {displayError}
        </span>
      )}

      {value && (
        <div className={styles.mapWrapper}>
          <GPSMap
            point={value}
            onDrag={disabled ? undefined : handleMapDrag}
            draggable={!disabled}
          />
        </div>
      )}
    </div>
  );
}
