// src/hooks/useLocation.ts
import { useState, useCallback } from "react";
import API_BASE from "../config";

export type LocationStatus =
  | "idle"
  | "requesting"
  | "gps_success"
  | "gps_denied"
  | "address_success"
  | "error";

export interface LocationState {
  lat: number | null;
  lng: number | null;
  address: string;
  status: LocationStatus;
}

const INITIAL: LocationState = {
  lat: null,
  lng: null,
  address: "",
  status: "idle",
};

export function useLocation() {
  const [loc, setLoc] = useState<LocationState>(INITIAL);

  // Attempt to get GPS coordinates from the browser.
  // On HTTPS (Vercel production) this triggers the native permission prompt.
  // On desktop or if denied, status becomes "gps_denied" — handle in UI.
  const requestGPS = useCallback(() => {
    if (!navigator.geolocation) {
      setLoc((l) => ({ ...l, status: "gps_denied" }));
      return;
    }
    setLoc((l) => ({ ...l, status: "requesting" }));
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLoc({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          address: "GPS location detected",
          status: "gps_success",
        });
      },
      () => {
        // Permission denied or unavailable — caller should show address input
        setLoc((l) => ({ ...l, status: "gps_denied" }));
      },
      { timeout: 10000, maximumAge: 60000 }
    );
  }, []);

  // Geocode a free-text address via our FastAPI /geocode proxy.
  // Returns true on success, false if address not found.
  const geocodeAddress = useCallback(
    async (query: string): Promise<boolean> => {
      if (!query.trim()) return false;
      try {
        const res = await fetch(
          `${API_BASE}/geocode?q=${encodeURIComponent(query)}`
        );
        const data = await res.json();
        if (data.found) {
          setLoc({
            lat: data.lat,
            lng: data.lng,
            address: data.display_name,
            status: "address_success",
          });
          return true;
        }
        setLoc((l) => ({ ...l, status: "error" }));
        return false;
      } catch {
        setLoc((l) => ({ ...l, status: "error" }));
        return false;
      }
    },
    []
  );

  const reset = useCallback(() => setLoc(INITIAL), []);

  return { loc, requestGPS, geocodeAddress, reset };
}
