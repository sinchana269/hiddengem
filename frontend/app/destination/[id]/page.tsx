"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type Attraction = {
  id?: string;
  name: string;
  category?: string;
  description?: string;
  image_url?: string;
  opening_time?: string;
  closing_time?: string;
  latitude?: number;
  longitude?: number;
};

type Destination = {
  id?: string;
  name: string;
  state?: string;
  description?: string;
  best_time?: string;
  image_url?: string;
  source_url?: string;
  attractions?: (Attraction | string)[];
  activities?: string[];
  food?: string[];
};

type ItineraryItem = {
  type: string;
  name: string;
  start_time?: string;
  end_time?: string;
  distance_from_previous_km?: number;
  travel_minutes?: number;
};

type ItineraryDay = {
  day: number;
  items: ItineraryItem[];
  distance_km?: number;
  travel_minutes?: number;
};

type ItineraryData = {
  days?: ItineraryDay[];
  total_distance_km?: number;
  total_travel_minutes?: number;
  maps_url?: string;
};

function formatMinutes(minutes?: number) {
  if (!minutes) return "0 min";

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours} hr`;

  return `${hours} hr ${mins} min`;
}

function getTimeLabel(time?: string) {
  if (!time) return "";

  const [hourString, minuteString] = time.split(":");
  const hour = Number(hourString);
  const minute = Number(minuteString || 0);

  if (Number.isNaN(hour)) return time;

  const suffix = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;

  return `${displayHour}:${String(minute).padStart(2, "0")} ${suffix}`;
}

function getItemIcon(type: string) {
  if (type === "meal") return "🍽️";
  if (type === "attraction") return "📍";
  return "🧭";
}

function ImageWithFallback({
  src,
  alt,
  className,
  darkMode,
}: {
  src?: string;
  alt: string;
  className: string;
  darkMode: boolean;
}) {
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setFailed(false);
  }, [src]);

  if (!src || failed) {
    return (
      <div
        className={`${className} flex items-center justify-center ${darkMode
          ? "bg-[#18211c] text-[#c8943e]"
          : "bg-[#e8f0ea] text-[#174d35]"
          } text-4xl`}
      >
        🏞️
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setFailed(true)}
      loading="lazy"
      referrerPolicy="no-referrer"
    />
  );
}

export default function DestinationPage() {
  const params = useParams();
  const router = useRouter();

  const destinationId = Array.isArray(params.id)
    ? params.id[0]
    : params.id;

  const [destination, setDestination] = useState<Destination | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [darkMode, setDarkMode] = useState(false);

  const [itineraryQuery, setItineraryQuery] = useState("");
  const [itineraryLoading, setItineraryLoading] = useState(false);
  const [itineraryError, setItineraryError] = useState("");
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null);

  /* ---------------- THEME ---------------- */

  useEffect(() => {
    const savedTheme = localStorage.getItem("hiddengem-theme");

    if (savedTheme === "dark") {
      setDarkMode(true);
    } else if (savedTheme === "light") {
      setDarkMode(false);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "hiddengem-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  /* ---------------- LOAD DESTINATION ---------------- */

  useEffect(() => {
    if (!destinationId) return;

    const id: string = destinationId;

    async function loadDestination() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/api/destination/${encodeURIComponent(id)}`
        );

        if (!response.ok) {
          throw new Error("Destination could not be loaded.");
        }

        const data = await response.json();
        const loadedDestination = data.destination || data;

        setDestination(loadedDestination);
      } catch (err) {
        console.error(err);
        setError("Unable to load this destination.");
      } finally {
        setLoading(false);
      }
    }

    loadDestination();
  }, [destinationId]);

  /* ---------------- NORMALIZED DATA ---------------- */

  const attractions = useMemo<Attraction[]>(() => {
    const raw = destination?.attractions || [];

    return raw
      .map((item, index) => {
        if (typeof item === "string") {
          const name = item.trim();

          if (!name) return null;

          return {
            id: `attraction-${index}`,
            name,
          };
        }

        if (item?.name?.trim()) {
          return {
            ...item,
            name: item.name.trim(),
          };
        }

        return null;
      })
      .filter((item): item is Attraction => Boolean(item));
  }, [destination]);

  const activities = useMemo(
    () =>
      Array.from(
        new Set(
          (destination?.activities || [])
            .map((item) => item?.trim())
            .filter(Boolean)
        )
      ),
    [destination]
  );

  const foods = useMemo(
    () =>
      Array.from(
        new Set(
          (destination?.food || [])
            .map((item) => item?.trim())
            .filter(Boolean)
        )
      ),
    [destination]
  );

  /* ---------------- ITINERARY ---------------- */

  async function buildItinerary(queryOverride?: string) {
    if (!destination) return;

    const typedQuery = queryOverride ?? itineraryQuery;

    const finalQuery = typedQuery.trim()
      ? `${typedQuery.trim()} in ${destination.name}`
      : `1 day in ${destination.name}`;

    try {
      setItineraryLoading(true);
      setItineraryError("");

      const response = await fetch(`${API_BASE_URL}/api/itinerary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: finalQuery,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not build itinerary.");
      }

      const data = await response.json();

      if (data?.itinerary) {
        setItinerary(data.itinerary);
      } else {
        setItinerary(data);
      }
    } catch (err) {
      console.error(err);
      setItineraryError(
        "I couldn't build the itinerary right now. Please try again."
      );
    } finally {
      setItineraryLoading(false);
    }
  }

  /* ---------------- LOADING ---------------- */

  if (loading) {
    return (
      <main
        className={`min-h-screen ${darkMode
          ? "bg-[#101713] text-white"
          : "bg-[#f7f5ef] text-[#17231c]"
          }`}
      >
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8">
          <div className="animate-pulse space-y-6">
            <div
              className={`h-10 w-64 rounded-xl ${darkMode ? "bg-[#18211c]" : "bg-[#e8f0ea]"
                }`}
            />
            <div
              className={`h-80 rounded-[2rem] ${darkMode ? "bg-[#18211c]" : "bg-[#e8f0ea]"
                }`}
            />
            <div
              className={`h-8 w-80 rounded-xl ${darkMode ? "bg-[#18211c]" : "bg-[#e8f0ea]"
                }`}
            />
            <div
              className={`h-24 rounded-2xl ${darkMode ? "bg-[#18211c]" : "bg-[#e8f0ea]"
                }`}
            />
          </div>
        </div>
      </main>
    );
  }

  /* ---------------- ERROR ---------------- */

  if (error || !destination) {
    return (
      <main
        className={`min-h-screen ${darkMode
          ? "bg-[#101713] text-white"
          : "bg-[#f7f5ef] text-[#17231c]"
          }`}
      >
        <div className="mx-auto max-w-3xl px-6 py-20 text-center">
          <div className="mb-5 text-5xl">🏞️</div>

          <h1 className="text-3xl font-black">
            Destination not found
          </h1>

          <p
            className={`mt-3 ${darkMode ? "text-white/60" : "text-[#68736c]"
              }`}
          >
            {error || "We could not find this destination."}
          </p>

          <button
            type="button"
            onClick={() => router.back()}
            className="mt-8 rounded-xl bg-[#174d35] px-6 py-3 font-bold text-white shadow-lg transition hover:bg-[#103b28]"
          >
            ← Go back
          </button>
        </div>
      </main>
    );
  }

  const googleMapsUrl =
    itinerary?.maps_url ||
    `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
      destination.name
    )}`;

  return (
    <main
      className={`min-h-screen transition-colors duration-300 ${darkMode
        ? "bg-[#101713] text-[#edf2ed]"
        : "bg-[#f7f5ef] text-[#17231c]"
        }`}
    >
      {/* NAVBAR */}

      <nav
        className={`sticky top-0 z-50 border-b backdrop-blur-xl ${darkMode
          ? "border-white/10 bg-[#101713]/90"
          : "border-black/5 bg-[#f7f5ef]/90"
          }`}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
          <button
            type="button"
            onClick={() => router.back()}
            className={`rounded-xl border px-4 py-2 text-sm font-semibold transition ${darkMode
              ? "border-white/10 bg-white/5 text-white hover:bg-white/10"
              : "border-black/5 bg-white text-[#17231c] shadow-sm hover:bg-[#e8f0ea]"
              }`}
          >
            ← Back
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                document.documentElement.style.fontSize = "18px";
              }}
              className={`rounded-xl border px-3 py-2 text-sm font-bold ${darkMode
                ? "border-white/10 bg-white/5 text-white"
                : "border-black/5 bg-white text-[#17231c]"
                }`}
              aria-label="Increase text size"
            >
              A+
            </button>

            <button
              type="button"
              onClick={() => setDarkMode((value) => !value)}
              className={`rounded-xl border px-3 py-2 text-sm ${darkMode
                ? "border-white/10 bg-white/5 text-white"
                : "border-black/5 bg-white text-[#17231c]"
                }`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? "☀️" : "🌙"}
            </button>
          </div>
        </div>
      </nav>

      {/* HERO */}

      <section className="mx-auto max-w-7xl px-5 pt-8 sm:px-8">
        <div className="relative overflow-hidden rounded-[2rem] bg-[#163c2a] shadow-2xl">
          <div className="relative h-[440px] sm:h-[500px]">
            <ImageWithFallback
              src={destination.image_url}
              alt={destination.name}
              className="absolute inset-0 h-full w-full object-cover"
              darkMode={darkMode}
            />

            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-black/10" />

            <div className="absolute inset-x-0 bottom-0 p-6 sm:p-10">
              <div className="max-w-4xl">
                <p className="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-[#e4b35c]">
                  Karnataka Tourism
                </p>

                <h1 className="text-4xl font-black leading-tight text-white drop-shadow-lg sm:text-6xl">
                  {destination.name}
                </h1>

                {destination.state && (
                  <p className="mt-3 text-base font-medium text-white/90 sm:text-lg">
                    📍 {destination.state}
                  </p>
                )}

                {destination.description && (
                  <p className="mt-5 max-w-3xl text-base leading-7 text-white sm:text-lg sm:leading-8">
                    {destination.description}
                  </p>
                )}

                {destination.best_time && (
                  <div className="mt-5 inline-flex rounded-full border border-white/20 bg-black/40 px-4 py-2 text-sm font-medium text-white backdrop-blur">
                    Best time: {destination.best_time}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* QUICK FACTS */}

      <section className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            {
              icon: "📍",
              label: "Places to go",
              value: attractions.length,
            },
            {
              icon: "🧭",
              label: "Things to do",
              value: activities.length,
            },
            {
              icon: "🍴",
              label: "What to eat",
              value: foods.length,
            },
          ].map((item) => (
            <div
              key={item.label}
              className={`rounded-2xl border p-5 ${darkMode
                ? "border-white/10 bg-[#18211c]"
                : "border-black/5 bg-white shadow-sm"
                }`}
            >
              <div className="text-2xl">{item.icon}</div>

              <p
                className={`mt-2 text-sm font-medium ${darkMode ? "text-white/55" : "text-[#68736c]"
                  }`}
              >
                {item.label}
              </p>

              <p
                className={`mt-1 text-2xl font-black ${darkMode ? "text-white" : "text-[#17231c]"
                  }`}
              >
                {item.value}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ABOUT */}

      {destination.description && (
        <section className="mx-auto max-w-5xl px-5 pb-10 sm:px-8">
          <div
            className={`rounded-3xl border p-6 sm:p-8 ${darkMode
              ? "border-white/10 bg-[#18211c]"
              : "border-black/5 bg-white shadow-sm"
              }`}
          >
            <p
              className={`text-sm font-bold uppercase tracking-[0.18em] ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                }`}
            >
              Discover {destination.name}
            </p>

            <h2
              className={`mt-2 text-3xl font-black ${darkMode ? "text-white" : "text-[#17231c]"
                }`}
            >
              About this place
            </h2>

            <p
              className={`mt-4 text-base leading-8 ${darkMode ? "text-white/70" : "text-[#4f5b53]"
                }`}
            >
              {destination.description}
            </p>
          </div>
        </section>
      )}

      {/* PLACES TO GO — TEXT ONLY */}

      {attractions.length > 0 && (
        <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
          <div className="mb-6">
            <p
              className={`text-xs font-bold uppercase tracking-[0.18em] ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                }`}
            >
              Explore the destination
            </p>

            <h2
              className={`mt-2 text-3xl font-black tracking-tight sm:text-4xl ${darkMode ? "text-white" : "text-[#17231c]"
                }`}
            >
              Places to go
            </h2>

            <p
              className={`mt-2 max-w-2xl text-sm leading-6 ${darkMode ? "text-white/55" : "text-[#68736c]"
                }`}
            >
              Places and attractions worth exploring during your visit.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            {attractions.map((place, index) => (
              <div
                key={place.id || `${place.name}-${index}`}
                className={`rounded-2xl border px-5 py-4 ${darkMode
                  ? "border-white/10 bg-[#18211c]"
                  : "border-black/5 bg-white shadow-sm"
                  }`}
              >
                <h3
                  className={`text-sm font-bold ${darkMode ? "text-white" : "text-[#17231c]"
                    }`}
                >
                  {place.name}
                </h3>

                {place.category && (
                  <p
                    className={`mt-1 text-xs font-semibold ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                      }`}
                  >
                    {place.category}
                  </p>
                )}

                {place.description && (
                  <p
                    className={`mt-2 max-w-md text-xs leading-5 ${darkMode ? "text-white/50" : "text-[#68736c]"
                      }`}
                  >
                    {place.description}
                  </p>
                )}

                {(place.opening_time || place.closing_time) && (
                  <p
                    className={`mt-2 text-xs ${darkMode ? "text-white/40" : "text-[#68736c]"
                      }`}
                  >
                    🕒{" "}
                    {getTimeLabel(place.opening_time) ||
                      "Opening time unavailable"}
                    {place.closing_time
                      ? ` – ${getTimeLabel(place.closing_time)}`
                      : ""}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* THINGS TO DO */}

      {activities.length > 0 && (
        <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
          <div
            className={`rounded-3xl border p-6 sm:p-8 ${darkMode
              ? "border-white/10 bg-[#18211c]"
              : "border-black/5 bg-white shadow-sm"
              }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🧭</span>

              <div>
                <p
                  className={`text-xs font-bold uppercase tracking-[0.16em] ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                    }`}
                >
                  Experience
                </p>

                <h2
                  className={`text-2xl font-black ${darkMode ? "text-white" : "text-[#17231c]"
                    }`}
                >
                  Things to do
                </h2>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              {activities.map((activity, index) => (
                <span
                  key={`${activity}-${index}`}
                  className={`rounded-full border px-4 py-2.5 text-sm font-semibold ${darkMode
                    ? "border-[#c8943e]/20 bg-[#c8943e]/10 text-[#e5b75f]"
                    : "border-[#174d35]/10 bg-[#e8f0ea] text-[#174d35]"
                    }`}
                >
                  {activity}
                </span>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* WHAT TO EAT */}

      {foods.length > 0 && (
        <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
          <div className="mb-5 flex items-center gap-3">
            <span className="text-2xl">🍴</span>

            <div>
              <p
                className={`text-xs font-bold uppercase tracking-[0.16em] ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                  }`}
              >
                Local flavours
              </p>

              <h2
                className={`text-2xl font-black ${darkMode ? "text-white" : "text-[#17231c]"
                  }`}
              >
                What to eat
              </h2>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            {foods.map((food, index) => (
              <span
                key={`${food}-${index}`}
                className={`rounded-full border px-4 py-2.5 text-sm font-medium ${darkMode
                  ? "border-white/10 bg-[#18211c] text-white/75"
                  : "border-black/5 bg-white text-[#4f5b53] shadow-sm"
                  }`}
              >
                {food}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* BUILD ITINERARY */}

      <section
        id="itinerary"
        className="mx-auto max-w-6xl px-5 py-12 sm:px-8"
      >
        <div
          className={`overflow-hidden rounded-3xl border shadow-2xl ${darkMode
            ? "border-[#174d35]/50 bg-[#18211c]"
            : "border-[#174d35]/10 bg-white shadow-xl"
            }`}
        >
          <div
            className={`border-b p-6 sm:p-8 ${darkMode
              ? "border-white/10 bg-[#15231b]"
              : "border-[#174d35]/10 bg-[#e8f0ea]"
              }`}
          >
            <p
              className={`text-sm font-bold uppercase tracking-[0.18em] ${darkMode ? "text-[#c8943e]" : "text-[#174d35]"
                }`}
            >
              Plan your trip
            </p>

            <h2
              className={`mt-2 text-3xl font-black sm:text-4xl ${darkMode ? "text-white" : "text-[#17231c]"
                }`}
            >
              Build my itinerary
            </h2>

            <p
              className={`mt-3 max-w-2xl ${darkMode ? "text-white/65" : "text-[#4f5b53]"
                }`}
            >
              Tell HiddenGem how you want to travel and it will build a
              destination-focused plan using the available tourism data.
            </p>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <input
                value={itineraryQuery}
                onChange={(event) =>
                  setItineraryQuery(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    buildItinerary();
                  }
                }}
                placeholder="e.g. 1 day, heritage and local food"
                className={`min-h-12 flex-1 rounded-xl border px-4 outline-none ${darkMode
                  ? "border-white/10 bg-[#101713] text-white placeholder:text-white/30 focus:border-[#c8943e]"
                  : "border-black/10 bg-white text-[#17231c] placeholder:text-[#68736c] focus:border-[#174d35]"
                  }`}
              />

              <button
                type="button"
                onClick={() => buildItinerary()}
                disabled={itineraryLoading}
                className="min-h-12 rounded-xl bg-[#174d35] px-6 font-black text-white shadow-lg transition hover:bg-[#103b28] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {itineraryLoading ? "Building..." : "Build itinerary"}
              </button>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {[
                "1 day, heritage and local food",
                "1 day, nature and photography",
                "2 days, peaceful and local food",
              ].map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => {
                    setItineraryQuery(prompt);
                    buildItinerary(prompt);
                  }}
                  className={`rounded-full border px-3 py-2 text-xs font-medium transition ${darkMode
                    ? "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
                    : "border-black/5 bg-white text-[#4f5b53] hover:bg-[#f7f5ef]"
                    }`}
                >
                  {prompt}
                </button>
              ))}
            </div>

            {itineraryError && (
              <p className="mt-4 rounded-xl border border-red-300/30 bg-red-500/10 px-4 py-3 text-sm text-red-500">
                {itineraryError}
              </p>
            )}
          </div>

          {itinerary && (
            <div className="p-6 sm:p-8">
              {/* SUMMARY */}

              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  {
                    label: "Days",
                    value: itinerary.days?.length || 0,
                  },
                  {
                    label: "Distance",
                    value: `${itinerary.total_distance_km?.toFixed(1) || "0"} km`,
                  },
                  {
                    label: "Travel time",
                    value: formatMinutes(
                      itinerary.total_travel_minutes
                    ),
                  },
                ].map((item) => (
                  <div
                    key={item.label}
                    className={`rounded-2xl p-4 ${darkMode
                      ? "bg-[#101713]"
                      : "bg-[#e8f0ea]"
                      }`}
                  >
                    <p
                      className={`text-xs font-medium ${darkMode
                        ? "text-white/45"
                        : "text-[#68736c]"
                        }`}
                    >
                      {item.label}
                    </p>

                    <p
                      className={`mt-1 text-2xl font-black ${darkMode
                        ? "text-white"
                        : "text-[#17231c]"
                        }`}
                    >
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* DAYS */}

              <div className="mt-8 space-y-6">
                {itinerary.days?.map((day) => (
                  <div key={day.day}>
                    <div className="mb-4 flex items-center justify-between">
                      <h3
                        className={`text-xl font-black ${darkMode
                          ? "text-white"
                          : "text-[#17231c]"
                          }`}
                      >
                        Day {day.day}
                      </h3>

                      <span
                        className={`text-sm ${darkMode
                          ? "text-white/45"
                          : "text-[#68736c]"
                          }`}
                      >
                        {day.distance_km?.toFixed(1) || "0"} km
                      </span>
                    </div>

                    <div className="space-y-3">
                      {day.items?.map((item, index) => (
                        <div
                          key={`${item.name}-${index}`}
                          className={`flex gap-4 rounded-2xl border p-4 ${darkMode
                            ? "border-white/10 bg-[#101713]"
                            : "border-black/5 bg-[#f7f5ef]"
                            }`}
                        >
                          <div
                            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-lg ${darkMode
                              ? "bg-[#174d35]/30"
                              : "bg-[#e8f0ea]"
                              }`}
                          >
                            {getItemIcon(item.type)}
                          </div>

                          <div className="min-w-0 flex-1">
                            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                              <h4
                                className={`font-bold ${darkMode
                                  ? "text-white"
                                  : "text-[#17231c]"
                                  }`}
                              >
                                {item.name}
                              </h4>

                              {(item.start_time ||
                                item.end_time) && (
                                  <span
                                    className={`text-sm font-medium ${darkMode
                                      ? "text-[#e5b75f]"
                                      : "text-[#174d35]"
                                      }`}
                                  >
                                    {getTimeLabel(item.start_time)}
                                    {item.end_time
                                      ? ` – ${getTimeLabel(
                                        item.end_time
                                      )}`
                                      : ""}
                                  </span>
                                )}
                            </div>

                            {item.distance_from_previous_km !==
                              undefined &&
                              item.distance_from_previous_km >
                              0 && (
                                <p
                                  className={`mt-1 text-xs ${darkMode
                                    ? "text-white/40"
                                    : "text-[#68736c]"
                                    }`}
                                >
                                  {item.distance_from_previous_km.toFixed(
                                    1
                                  )}{" "}
                                  km ·{" "}
                                  {item.travel_minutes || 0} min
                                  travel
                                </p>
                              )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* GOOGLE MAPS */}

              <div className="mt-8">
                <a
                  href={googleMapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex min-h-14 w-full items-center justify-center gap-3 rounded-2xl bg-[#174d35] px-6 py-4 text-center font-black text-white shadow-xl transition hover:bg-[#103b28] hover:shadow-2xl"
                >
                  <span className="text-xl text-white">🗺️</span>
                  <span className="text-white">Open route in Google Maps</span>
                  <span className="text-white" aria-hidden="true">
                    ↗
                  </span>
                </a>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* SOURCE */}

      <section className="mx-auto max-w-6xl px-5 pb-12 sm:px-8">
        <div
          className={`rounded-2xl border p-5 ${darkMode
            ? "border-white/10 bg-[#18211c]"
            : "border-black/5 bg-white shadow-sm"
            }`}
        >
          <p
            className={`text-sm ${darkMode ? "text-white/55" : "text-[#68736c]"
              }`}
          >
            Tourism information is based on Karnataka Tourism
            source content.
          </p>

          {destination.source_url && (
            <a
              href={destination.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className={`mt-3 inline-block font-semibold underline underline-offset-4 ${darkMode ? "text-[#e5b75f]" : "text-[#174d35]"
                }`}
            >
              View official Karnataka Tourism source ↗
            </a>
          )}
        </div>
      </section>

      {/* FOOTER */}

      <footer className="border-t border-white/10 bg-[#102b1e] px-5 py-8 text-center text-sm text-white/60">
        HiddenGem · Karnataka Tourism Discovery
      </footer>

      {/* SCROLL TOP */}

      <button
        type="button"
        onClick={() =>
          window.scrollTo({
            top: 0,
            behavior: "smooth",
          })
        }
        className="fixed bottom-5 right-5 z-40 flex h-11 w-11 items-center justify-center rounded-full bg-[#174d35] text-lg text-white shadow-xl transition hover:bg-[#103b28]"
        aria-label="Scroll to top"
      >
        ↑
      </button>
    </main>
  );
}