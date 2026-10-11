
"use client";

import { useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

const CATEGORIES = [
  {
    label: "Nature",
    emoji: "🌿",
    query: "I want a nature trip",
    description: "Forests, hills & peaceful landscapes",
  },
  {
    label: "Heritage",
    emoji: "🏛️",
    query: "I want a heritage trip",
    description: "History, architecture & culture",
  },
  {
    label: "Adventure",
    emoji: "🧗",
    query: "I want an adventure trip",
    description: "Outdoor experiences & exploration",
  },
  {
    label: "Waterfalls",
    emoji: "💦",
    query: "I want waterfalls",
    description: "Waterfalls, viewpoints & monsoon escapes",
  },
  {
    label: "Wildlife",
    emoji: "🐘",
    query: "I want wildlife",
    description: "Forests, wildlife & wilderness",
  },
  {
    label: "Food & Culinary",
    emoji: "🍛",
    query: "I want local food",
    description: "Discover regional flavours",
  },
  {
    label: "Photography",
    emoji: "📷",
    query: "I want photography",
    description: "Scenic places worth capturing",
  },
  {
    label: "Peaceful",
    emoji: "🧘",
    query: "I want a peaceful trip",
    description: "Slow travel & quiet escapes",
  },
];

type Recommendation = {
  destination: {
    name: string;
    description?: string;
    category?: string;
    best_season?: string;
    image_url?: string;
    attractions?: string[];
    activities?: string[];
    food?: string[];
  };
  match_score: number;
  content_similarity?: number;
  matching_reasons: string[];
};

type Preferences = {
  location: string | null;
  duration_days: number | null;
  budget: number | null;
  interests: string[];
  activities: string[];
  travel_style: string[];
  food_preferences: string[];
  trip_type: string[];
  group_type: string[];
};

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const [recommendations, setRecommendations] = useState<
    Recommendation[]
  >([]);

  const [preferences, setPreferences] =
    useState<Preferences | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [darkMode, setDarkMode] = useState(false);

  const [textSize, setTextSize] = useState<
    "small" | "normal" | "large"
  >("normal");

  const [showTopButton, setShowTopButton] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem("hiddengem-theme");
    const savedTextSize = localStorage.getItem(
      "hiddengem-text-size"
    );

    if (savedTheme === "dark") {
      setDarkMode(true);
    } else if (savedTheme === "light") {
      setDarkMode(false);
    }

    if (
      savedTextSize === "small" ||
      savedTextSize === "normal" ||
      savedTextSize === "large"
    ) {
      setTextSize(savedTextSize);
    }

    const handleScroll = () => {
      setShowTopButton(window.scrollY > 500);
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "hiddengem-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem(
      "hiddengem-text-size",
      textSize
    );
  }, [textSize]);

  const handleDiscover = async () => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setError(
        "Tell us a little about the kind of trip you're looking for."
      );
      setRecommendations([]);
      setPreferences(null);
      return;
    }

    setLoading(true);
    setError("");
    setRecommendations([]);
    setPreferences(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/recommend`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: trimmedQuery,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Request failed with status ${response.status}`
        );
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(
          data.message || "Recommendation request failed."
        );
      }

      setPreferences(data.preferences || null);
      setRecommendations(data.recommendations || []);

      if (
        !data.recommendations ||
        data.recommendations.length === 0
      ) {
        setError(
          "We couldn't find a close match. Try adding an interest, activity, duration or location."
        );
      }
    } catch (err) {
      console.error("Recommendation error:", err);

      setError(
        "Could not connect to the recommendation service. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (
    label: string,
    categoryQuery: string
  ) => {
    const isCurrentlyActive =
      activeCategory === label;

    setActiveCategory(
      isCurrentlyActive ? null : label
    );

    if (isCurrentlyActive) {
      return;
    }

    setQuery((prev) => {
      const trimmed = prev.trim();

      if (!trimmed) {
        return categoryQuery;
      }

      return `${trimmed} ${categoryQuery
        .replace(/^I want /i, "and want ")
        .toLowerCase()}`;
    });
  };

  const preferenceItems: string[] = preferences
    ? [
        preferences.location
          ? `📍 ${preferences.location}`
          : null,

        preferences.duration_days
          ? `📅 ${preferences.duration_days} day${
              preferences.duration_days > 1
                ? "s"
                : ""
            }`
          : null,

        preferences.budget
          ? `💰 ₹${preferences.budget}`
          : null,

        ...preferences.interests.map(
          (item) => `✨ ${item}`
        ),

        ...preferences.activities.map(
          (item) => `🧗 ${item}`
        ),

        ...preferences.travel_style.map(
          (item) => `🌿 ${item}`
        ),

        ...preferences.food_preferences.map(
          (item) => `🍛 ${item}`
        ),

        ...preferences.trip_type.map(
          (item) => `🧳 ${item}`
        ),

        ...preferences.group_type.map(
          (item) => `👥 ${item}`
        ),
      ].filter(
        (item): item is string => Boolean(item)
      )
    : [];

  const textScale =
    textSize === "small"
      ? "text-[0.94rem]"
      : textSize === "large"
        ? "text-[1.06rem]"
        : "text-base";

  return (
    <main
      className={`min-h-screen transition-colors duration-300 ${
        darkMode
          ? "bg-[#101713] text-[#edf2ed]"
          : "bg-[#f7f5ef] text-[#17231c]"
      } ${textScale}`}
    >
      {/* NAVIGATION */}

      <nav
        className={`sticky left-0 right-0 top-0 z-50 border-b backdrop-blur-xl transition-colors duration-300 ${
          darkMode
            ? "border-white/10 bg-[#101713]/90"
            : "border-black/5 bg-[#f7f5ef]/90"
        }`}
      >
        <div className="hg-container flex h-16 items-center justify-between gap-4">
          <a
            href="/"
            className={`shrink-0 text-xl font-black tracking-[-0.05em] ${
              darkMode
                ? "text-white"
                : "text-[#174d35]"
            }`}
          >
            Hidden
            <span className="text-[#c8943e]">
              Gem
            </span>
          </a>

          <div
            className={`hidden items-center gap-8 text-sm font-medium md:flex ${
              darkMode
                ? "text-white/65"
                : "text-[#536057]"
            }`}
          >
            <a
              href="#discover"
              className="transition hover:text-[#c8943e]"
            >
              Discover
            </a>

            <a
              href="#explore"
              className="transition hover:text-[#c8943e]"
            >
              Explore
            </a>
          </div>

          <div className="flex items-center gap-2">
            {/* TEXT SIZE */}

            <div
              className={`hidden items-center rounded-full border p-1 sm:flex ${
                darkMode
                  ? "border-white/10 bg-white/5"
                  : "border-black/10 bg-white"
              }`}
              aria-label="Text size controls"
            >
              <button
                onClick={() =>
                  setTextSize("small")
                }
                className={`rounded-full px-2 py-1 text-xs font-bold transition ${
                  textSize === "small"
                    ? "bg-[#174d35] text-white"
                    : darkMode
                      ? "text-white/60 hover:text-white"
                      : "text-[#69736d] hover:text-[#174d35]"
                }`}
                aria-label="Decrease text size"
              >
                A−
              </button>

              <button
                onClick={() =>
                  setTextSize("normal")
                }
                className={`rounded-full px-2 py-1 text-xs font-bold transition ${
                  textSize === "normal"
                    ? "bg-[#174d35] text-white"
                    : darkMode
                      ? "text-white/60 hover:text-white"
                      : "text-[#69736d] hover:text-[#174d35]"
                }`}
                aria-label="Normal text size"
              >
                A
              </button>

              <button
                onClick={() =>
                  setTextSize("large")
                }
                className={`rounded-full px-2 py-1 text-xs font-bold transition ${
                  textSize === "large"
                    ? "bg-[#174d35] text-white"
                    : darkMode
                      ? "text-white/60 hover:text-white"
                      : "text-[#69736d] hover:text-[#174d35]"
                }`}
                aria-label="Increase text size"
              >
                A+
              </button>
            </div>

            {/* DARK MODE */}

            <button
              onClick={() =>
                setDarkMode((prev) => !prev)
              }
              className={`flex h-9 w-9 items-center justify-center rounded-full border text-sm transition hover:-translate-y-0.5 ${
                darkMode
                  ? "border-white/10 bg-white/5 text-white"
                  : "border-black/10 bg-white text-[#174d35]"
              }`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? "☀" : "☾"}
            </button>
          </div>
        </div>
      </nav>

      {/* HERO */}

      <section
        id="discover"
        className="relative overflow-hidden bg-[#163c2a]"
      >
        <div className="relative min-h-[520px]">
          <img
            src="https://karnatakatourism.org/wp-content/uploads/2024/03/Karnataka-tourism.jpg"
            alt="Karnataka landscape"
            className="absolute inset-0 h-full w-full object-cover"
            referrerPolicy="no-referrer"
          />

          <div className="absolute inset-0 bg-black/45" />

          <div className="absolute inset-0 bg-gradient-to-t from-[#102b1e] via-black/10 to-black/20" />

          <div className="relative z-10 flex min-h-[520px] items-center">
            <div className="hg-container py-16 sm:py-20">
              <div className="max-w-3xl">
                <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-[#e4b35c]">
                  Explore Karnataka
                </p>

                <h1 className="max-w-3xl text-4xl font-black leading-[0.98] tracking-[-0.055em] text-white sm:text-5xl lg:text-7xl">
                  Find the Karnataka
                  <br />
                  <span className="text-[#e5b75f]">
                    you haven't seen yet.
                  </span>
                </h1>

                <p className="mt-5 max-w-xl text-sm leading-6 text-white/80 sm:text-base">
                  Tell us what kind of trip you have
                  in mind, and discover places that fit
                  the way you want to travel.
                </p>

                {/* SEARCH */}

                <div className="hg-search mt-7 flex max-w-2xl flex-col gap-2 rounded-[20px] border border-white/20 bg-white p-2 shadow-2xl sm:flex-row">
                  <div className="flex min-w-0 flex-1 items-center px-3">
                    <span className="mr-3 text-lg text-[#174d35]">
                      ✦
                    </span>

                    <input
                      type="text"
                      value={query}
                      onChange={(e) =>
                        setQuery(e.target.value)
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleDiscover();
                        }
                      }}
                      placeholder='Try "a peaceful 2-day trip with waterfalls near Mysuru"'
                      className="min-w-0 flex-1 bg-transparent py-3 text-sm text-gray-800 outline-none placeholder:text-gray-400 sm:text-[15px]"
                      aria-label="Describe your trip"
                      disabled={loading}
                    />
                  </div>

                  <button
                    onClick={handleDiscover}
                    disabled={loading}
                    className="rounded-[14px] bg-[#174d35] px-6 py-3 text-sm font-bold text-white shadow-md transition duration-200 hover:-translate-y-0.5 hover:bg-[#103b28] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading
                      ? "Discovering..."
                      : "Discover →"}
                  </button>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {[
                    "Peaceful weekend",
                    "Waterfalls",
                    "Heritage",
                    "Wildlife",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => {
                        setQuery(suggestion);
                        setTimeout(
                          () => handleDiscover(),
                          0
                        );
                      }}
                      className="rounded-full border border-white/15 bg-black/15 px-3 py-1.5 text-[11px] font-medium text-white/75 backdrop-blur-sm transition hover:border-[#e5b75f]/50 hover:bg-black/25 hover:text-white"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* EXPLORE */}

      <section
        id="explore"
        className={`py-14 sm:py-16 ${
          darkMode
            ? "bg-[#101713]"
            : "bg-[#f7f5ef]"
        }`}
      >
        <div className="hg-container">
          <div className="mb-7 flex flex-col justify-between gap-3 md:flex-row md:items-end">
            <div>
              <p
                className={`mb-2 text-[10px] font-bold uppercase tracking-[0.2em] ${
                  darkMode
                    ? "text-[#c8943e]"
                    : "text-[#174d35]"
                }`}
              >
                Explore by interest
              </p>

              <h2
                className={`text-2xl font-black tracking-tight sm:text-3xl ${
                  darkMode
                    ? "text-white"
                    : "text-[#17231c]"
                }`}
              >
                What are you looking for?
              </h2>
            </div>

            <p
              className={`max-w-md text-sm leading-6 ${
                darkMode
                  ? "text-white/50"
                  : "text-[#68736c]"
              }`}
            >
              Pick something that catches your eye,
              or describe your perfect trip above.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
            {CATEGORIES.map(
              ({
                label,
                emoji,
                query: categoryQuery,
                description,
              }) => {
                const isActive =
                  activeCategory === label;

                return (
                  <button
                    key={label}
                    onClick={() =>
                      toggleCategory(
                        label,
                        categoryQuery
                      )
                    }
                    aria-pressed={isActive}
                    className={`group relative min-h-[135px] overflow-hidden rounded-2xl border p-4 text-left transition-all duration-300 ${
                      isActive
                        ? "border-[#174d35] bg-[#174d35] text-white shadow-lg"
                        : darkMode
                          ? "border-white/10 bg-[#18211c] hover:-translate-y-1 hover:border-[#c8943e]/40 hover:bg-[#1d2922] hover:shadow-xl"
                          : "border-black/5 bg-white hover:-translate-y-1 hover:border-[#174d35]/20 hover:shadow-lg"
                    }`}
                  >
                    <div className="text-2xl transition-transform duration-300 group-hover:scale-110">
                      {emoji}
                    </div>

                    <div className="mt-5">
                      <p
                        className={`text-xs font-bold ${
                          isActive
                            ? "text-white"
                            : darkMode
                              ? "text-white"
                              : "text-[#17231c]"
                        }`}
                      >
                        {label}
                      </p>

                      <p
                        className={`mt-1 text-[10px] leading-4 ${
                          isActive
                            ? "text-white/65"
                            : darkMode
                              ? "text-white/45"
                              : "text-[#7a837d]"
                        }`}
                      >
                        {description}
                      </p>
                    </div>
                  </button>
                );
              }
            )}
          </div>
        </div>
      </section>

      {/* ERROR */}

      {error && (
        <section className="pb-7">
          <div className="hg-container">
            <div
              className={`rounded-2xl border px-5 py-4 text-sm ${
                darkMode
                  ? "border-red-900/60 bg-red-950/30 text-red-300"
                  : "border-red-200 bg-red-50 text-red-700"
              }`}
            >
              {error}
            </div>
          </div>
        </section>
      )}

      {/* TRAVEL BRIEF */}

      {preferences &&
        preferenceItems.length > 0 && (
          <section className="pb-8">
            <div className="hg-container">
              <div
                className={`rounded-3xl border p-5 sm:p-7 ${
                  darkMode
                    ? "border-[#174d35]/40 bg-[#15231b]"
                    : "border-[#174d35]/10 bg-[#e8f0ea]"
                }`}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p
                      className={`mb-1 text-[10px] font-bold uppercase tracking-[0.18em] ${
                        darkMode
                          ? "text-[#c8943e]"
                          : "text-[#174d35]"
                      }`}
                    >
                      Your trip
                    </p>

                    <h2
                      className={`text-xl font-black tracking-tight ${
                        darkMode
                          ? "text-white"
                          : "text-[#123c29]"
                      }`}
                    >
                      Here's what we found
                    </h2>
                  </div>
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {preferenceItems.map(
                    (item, index) => (
                      <span
                        key={`${item}-${index}`}
                        className={`rounded-full border px-3.5 py-1.5 text-xs font-medium ${
                          darkMode
                            ? "border-white/10 bg-white/5 text-white/70"
                            : "border-[#174d35]/10 bg-white/75 text-[#315642]"
                        }`}
                      >
                        {item}
                      </span>
                    )
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

      {/* RECOMMENDATIONS */}

      {recommendations.length > 0 && (
        <section className="pb-16 sm:pb-20">
          <div className="hg-container">
            <div
              className={`mb-8 flex flex-col gap-2 border-b pb-6 sm:flex-row sm:items-end sm:justify-between ${
                darkMode
                  ? "border-white/10"
                  : "border-black/10"
              }`}
            >
              <div>
                <p
                  className={`mb-2 text-[10px] font-bold uppercase tracking-[0.18em] ${
                    darkMode
                      ? "text-[#c8943e]"
                      : "text-[#174d35]"
                  }`}
                >
                  Your discoveries
                </p>

                <h2
                  className={`text-2xl font-black tracking-tight sm:text-3xl ${
                    darkMode
                      ? "text-white"
                      : "text-[#17231c]"
                  }`}
                >
                  Destinations worth discovering
                </h2>
              </div>

              <span
                className={`text-xs ${
                  darkMode
                    ? "text-white/45"
                    : "text-[#68736c]"
                }`}
              >
                {recommendations.length} destination
                {recommendations.length !== 1
                  ? "s"
                  : ""}
              </span>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              {recommendations.map((item) => {
                const destination =
                  item.destination;

                const destinationId =
                  destination.name
                    .toLowerCase()
                    .replace(/\s+/g, "-");

                return (
                  <a
                    key={destination.name}
                    href={`/destination/${destinationId}`}
                    className="group block rounded-[22px] focus:outline-none focus:ring-2 focus:ring-[#174d35] focus:ring-offset-4"
                  >
                    <article
                      className={`overflow-hidden rounded-[22px] border shadow-sm transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-xl ${
                        darkMode
                          ? "border-white/10 bg-[#18211c]"
                          : "border-black/5 bg-white"
                      }`}
                    >
                      {/* IMAGE */}

                      <div className="relative h-[245px] overflow-hidden bg-[#e8f0ea]">
                        {destination.image_url ? (
                          <img
                            src={destination.image_url}
                            alt={destination.name}
                            className="h-full w-full object-cover transition duration-700 group-hover:scale-105"
                            loading="lazy"
                            referrerPolicy="no-referrer"
                          />
                        ) : (
                          <div
                            className={`flex h-full items-center justify-center text-sm ${
                              darkMode
                                ? "bg-[#18211c] text-[#c8943e]"
                                : "bg-[#e8f0ea] text-[#174d35]"
                            }`}
                          >
                            Karnataka destination
                          </div>
                        )}

                        <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />

                        <div className="absolute left-4 top-4 rounded-full border border-white/20 bg-black/20 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white backdrop-blur-md">
                          Karnataka
                        </div>

                        <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-3">
                          <div>
                            {destination.category && (
                              <p className="mb-1 text-[9px] font-bold uppercase tracking-[0.16em] text-[#e3b35d]">
                                {destination.category}
                              </p>
                            )}

                            <h3 className="text-2xl font-black tracking-tight text-white">
                              {destination.name}
                            </h3>
                          </div>

                          <div className="shrink-0 rounded-xl bg-white px-3 py-2 text-center shadow-xl">
                            <div className="text-lg font-black text-[#174d35]">
                              {item.match_score.toFixed(
                                0
                              )}
                            </div>

                            <div className="text-[8px] font-bold uppercase tracking-wider text-[#7a837d]">
                              Match
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* CONTENT */}

                      <div className="p-5">
                        {destination.description && (
                          <p
                            className={`line-clamp-3 text-sm leading-6 ${
                              darkMode
                                ? "text-white/60"
                                : "text-[#68736c]"
                            }`}
                          >
                            {destination.description}
                          </p>
                        )}

                        {item.matching_reasons.length >
                          0 && (
                          <div className="mt-5">
                            <p
                              className={`mb-2 text-[9px] font-bold uppercase tracking-[0.16em] ${
                                darkMode
                                  ? "text-white/40"
                                  : "text-[#8a948e]"
                              }`}
                            >
                              Good fit for you
                            </p>

                            <div className="flex flex-wrap gap-2">
                              {item.matching_reasons.map(
                                (reason) => (
                                  <span
                                    key={reason}
                                    className={`rounded-full px-3 py-1.5 text-[11px] font-medium ${
                                      darkMode
                                        ? "bg-[#174d35]/30 text-[#b8d1bf]"
                                        : "bg-[#e8f0ea] text-[#315642]"
                                    }`}
                                  >
                                    ✓ {reason}
                                  </span>
                                )
                              )}
                            </div>
                          </div>
                        )}

                        {destination.attractions &&
                          destination.attractions
                            .length > 0 && (
                            <div className="mt-5">
                              <p
                                className={`mb-2 text-[9px] font-bold uppercase tracking-[0.16em] ${
                                  darkMode
                                    ? "text-white/40"
                                    : "text-[#8a948e]"
                                }`}
                              >
                                Places to explore
                              </p>

                              <div className="flex flex-wrap gap-2">
                                {destination.attractions
                                  .slice(0, 4)
                                  .map(
                                    (
                                      attraction
                                    ) => (
                                      <span
                                        key={
                                          attraction
                                        }
                                        className={`rounded-full border px-3 py-1.5 text-[11px] ${
                                          darkMode
                                            ? "border-white/10 bg-white/5 text-white/60"
                                            : "border-black/5 bg-[#f7f5ef] text-[#526057]"
                                        }`}
                                      >
                                        {attraction}
                                      </span>
                                    )
                                  )}
                              </div>
                            </div>
                          )}

                        <div
                          className={`mt-6 flex items-center justify-between border-t pt-4 ${
                            darkMode
                              ? "border-white/10"
                              : "border-black/5"
                          }`}
                        >
                          <span className="text-sm font-bold text-[#174d35]">
                            Explore destination
                          </span>

                          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#174d35] text-sm text-white transition-transform duration-300 group-hover:translate-x-1">
                            →
                          </span>
                        </div>
                      </div>
                    </article>
                  </a>
                );
              })}
            </div>
          </div>
        </section>
      )}

      {/* FOOTER */}

      <footer className="bg-[#102b1e] py-10 text-white">
        <div className="hg-container">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="text-xl font-black tracking-[-0.04em]">
                Hidden
                <span className="text-[#e0ad55]">
                  Gem
                </span>
              </div>

              <p className="mt-2 max-w-sm text-xs leading-5 text-white/50">
                Find places, experiences and journeys
                worth discovering across Karnataka.
              </p>
            </div>

            <div className="text-xs text-white/35">
              Explore more. Travel differently.
            </div>
          </div>
        </div>
      </footer>

      {/* SCROLL TO TOP */}

      <button
        onClick={() =>
          window.scrollTo({
            top: 0,
            behavior: "smooth",
          })
        }
        aria-label="Scroll to top"
        className={`fixed bottom-5 right-5 z-40 flex h-11 w-11 items-center justify-center rounded-full bg-[#174d35] text-white shadow-xl transition-all duration-300 hover:-translate-y-1 hover:bg-[#103b28] ${
          showTopButton
            ? "translate-y-0 opacity-100"
            : "pointer-events-none translate-y-4 opacity-0"
        }`}
      >
        ↑
      </button>
    </main>
  );
}
