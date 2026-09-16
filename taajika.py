import datetime
import math
import swisseph as swe

# Configure Swiss Ephemeris to use Lahiri Ayanamsa (Nirayana)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}

RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

EXALTATION_SIGNS = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7
}

DEBILITATION_SIGNS = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
    "Jupiter": 10, "Venus": 6, "Saturn": 1
}

DEBILITATION_DEGREES = {
    "Sun": 10, "Moon": 3, "Mars": 28, "Mercury": 15,
    "Jupiter": 5, "Venus": 27, "Saturn": 20
}

# -----------------------------------------------------------------------------
# TAJIKA HADDA (BOUNDS) BOUNDARY MATRIX
# Format per sign: list of tuples -> (upper_limit_degree, ruling_planet)
# -----------------------------------------------------------------------------
HADDA_TABLE = {
    0:  [(6, "Jupiter"), (12, "Venus"), (20, "Mercury"), (25, "Mars"), (30, "Saturn")],    # Aries
    1:  [(8, "Venus"), (14, "Mercury"), (22, "Jupiter"), (27, "Saturn"), (30, "Mars")],    # Taurus
    2:  [(6, "Mercury"), (12, "Venus"), (17, "Jupiter"), (24, "Mars"), (30, "Saturn")],    # Gemini
    3:  [(7, "Mars"), (13, "Venus"), (19, "Mercury"), (26, "Jupiter"), (30, "Saturn")],    # Cancer
    4:  [(6, "Jupiter"), (11, "Venus"), (18, "Saturn"), (24, "Mercury"), (30, "Mars")],    # Leo
    5:  [(7, "Mercury"), (17, "Venus"), (21, "Jupiter"), (28, "Mars"), (30, "Saturn")],    # Virgo
    6:  [(6, "Saturn"), (14, "Mercury"), (21, "Jupiter"), (28, "Venus"), (30, "Mars")],    # Libra
    7:  [(7, "Mars"), (11, "Venus"), (19, "Mercury"), (24, "Jupiter"), (30, "Saturn")],    # Scorpio
    8:  [(12, "Jupiter"), (17, "Venus"), (21, "Mercury"), (26, "Mars"), (30, "Saturn")],   # Sagittarius
    9:  [(7, "Mercury"), (14, "Jupiter"), (22, "Venus"), (26, "Saturn"), (30, "Mars")],    # Capricorn
    10: [(7, "Venus"), (13, "Mercury"), (20, "Jupiter"), (25, "Mars"), (30, "Saturn")],    # Aquarius
    11: [(12, "Venus"), (16, "Jupiter"), (19, "Mercury"), (28, "Mars"), (30, "Saturn")]     # Pisces
}

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS & TIME CONVERSIONS
# -----------------------------------------------------------------------------

def decimal_to_dms(deg_float):
    """Converts decimal degrees to Degrees, Minutes, and Seconds."""
    deg = int(deg_float)
    min_float = (deg_float - deg) * 60.0
    minutes = int(min_float)
    seconds = int(round((min_float - minutes) * 60.0))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        deg += 1
    return deg, minutes, seconds

def format_dms(deg_float):
    """Formats decimal degrees within a sign into Sign Name DD° MM' SS"."""
    sign_num = int(deg_float // 30)
    rem_deg = deg_float % 30
    d, m, s = decimal_to_dms(rem_deg)
    return f"{RASHI_NAMES[sign_num]:<11} {d:02d}° {m:02d}' {s:02d}\""

def datetime_to_jd(dt_utc):
    """Converts UTC datetime object to Julian Day (UT)."""
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )

def jd_to_datetime(jd):
    """Converts Julian Day (UT) to UTC datetime object."""
    year, month, day, hour_float = swe.revjul(jd)
    hours = int(hour_float)
    minutes_float = (hour_float - hours) * 60.0
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60.0))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        hours += 1
    return datetime.datetime(year, month, day, hours, minutes, seconds)

def get_planet_sidereal_lon(jd, planet_id):
    """Calculates planet's sidereal longitude (Lahiri Ayanamsa)."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    res = swe.calc_ut(jd, planet_id, flags)
    return res[0][0] % 360.0

def get_chart_positions(jd, lat, lon):
    """Calculates positions of Ascendant and 7 Classical Planets."""
    positions = {}
    for p_name, p_id in PLANETS.items():
        positions[p_name] = get_planet_sidereal_lon(jd, p_id)

    # Ascendant Calculation
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    positions["Ascendant"] = ascmc[0] % 360.0
    return positions

# -----------------------------------------------------------------------------
# TAJIKA DRISHTI (ASPECT & RELATIONSHIP) ENGINE
# -----------------------------------------------------------------------------

def calculate_tajika_relationships(positions):
    """Computes Friends, Enemies, and Neutrals based on Tajika Aspects (Drishti)."""
    relationships = {}
    planet_list = list(PLANETS.keys())

    for p1 in planet_list:
        p1_sign = int(positions[p1] // 30)
        friends, enemies, neutrals = [], [], []

        for p2 in planet_list:
            if p1 == p2:
                continue
            p2_sign = int(positions[p2] // 30)
            house_diff = ((p2_sign - p1_sign) % 12) + 1

            if house_diff in [3, 5, 9, 11]:
                friends.append(p2)
            elif house_diff in [1, 4, 7, 10]:
                enemies.append(p2)
            else:
                neutrals.append(p2)

        relationships[p1] = {
            "Friends_List": friends,
            "Enemies_List": enemies,
            "Neutrals_List": neutrals,
            "Friends": ", ".join(friends) if friends else "-",
            "Enemies": ", ".join(enemies) if enemies else "-",
            "Neutrals": ", ".join(neutrals) if neutrals else "-"
        }

    return relationships

def get_relationship_status(planet, target_lord, relationships):
    """Determines if target_lord is Own, Friend, Neutral, or Enemy to planet."""
    if planet == target_lord:
        return "Own"
    rel_info = relationships[planet]
    if target_lord in rel_info["Friends_List"]:
        return "Friend"
    elif target_lord in rel_info["Neutrals_List"]:
        return "Neutral"
    else:
        return "Enemy"

def get_hadda_lord(sign_idx, deg_in_sign):
    """Finds the Hadda Lord for a given degree within a sign using Tajika table."""
    for limit, lord in HADDA_TABLE[sign_idx]:
        if deg_in_sign <= limit:
            return lord
    return HADDA_TABLE[sign_idx][-1][1]

# -----------------------------------------------------------------------------
# PANCHA VARGEEYA BALA ENGINE
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# TAJIKA DREKKANA LOOKUP TABLE
# Map each sign index (0-11) to its 3 Drekkana lords: [1st (0-10°), 2nd (10-20°), 3rd (20-30°)]
# -----------------------------------------------------------------------------
DREKKANA_TABLE = {
    0:  ["Mars", "Sun", "Venus"],         # Aries
    1:  ["Mercury", "Moon", "Saturn"],    # Taurus
    2:  ["Jupiter", "Mars", "Sun"],       # Gemini
    3:  ["Venus", "Mercury", "Moon"],      # Cancer
    4:  ["Saturn", "Jupiter", "Mars"],       # Leo
    5:  ["Sun", "Venus", "Mercury"],   # Virgo
    6:  ["Moon", "Saturn", "Jupiter"],   # Libra
    7:  ["Mars", "Sun", "Venus"],      # Scorpio
    8:  ["Mercury", "Moon", "Saturn"],       # Sagittarius
    9:  ["Jupiter", "Mars", "Sun"],   # Capricorn
    10: ["Venus", "Mercury", "Moon"],   # Aquarius
    11: ["Saturn", "Jupiter", "Mars"]       # Pisces
}

def get_drekkana_lord(sign_idx, deg_in_sign):
    """Finds the Drekkana Lord for a given degree within a sign using the Drekkana table."""
    drekkana_num = int(deg_in_sign // 10)  # 0 for 0-10°, 1 for 10-20°, 2 for 20-30°
    if drekkana_num > 2:
        drekkana_num = 2  # Guard edge case at exactly 30°
    return DREKKANA_TABLE[sign_idx][drekkana_num]

def calculate_pancha_vargeeya_bala(positions, relationships):
    """Calculates 5-fold strengths (Pancha Vargeeya Bala) & Vishwa Bala accurately."""
    balas = {}
    
    # Base Max Multipliers for [Own, Friend, Neutral, Enemy]
    SCORES = {
        "Kshetra":   {"Own": 30.0, "Friend": 22.5,  "Neutral": 15.0, "Enemy": 7.5},
        "Hadda":     {"Own": 15.0, "Friend": 11.25, "Neutral": 7.5,  "Enemy": 3.75},
        "Dreshkana": {"Own": 10.0, "Friend": 7.5,   "Neutral": 5.0,  "Enemy": 2.5},
        "Navamsha":  {"Own": 5.0,  "Friend": 3.75,  "Neutral": 2.5,  "Enemy": 1.25}
    }

    for p_name in PLANETS.keys():
        deg = positions[p_name]
        sign_idx = int(deg // 30)
        deg_in_sign = deg % 30

        # 1. KSHETRA BALA
        rashi_lord = RASHI_LORDS[sign_idx]
        k_status = get_relationship_status(p_name, rashi_lord, relationships)
        kshetra = SCORES["Kshetra"][k_status]

        # 2. UCCHA BALA (UPDATED NO-ABS LOGIC)
        deb_sign = DEBILITATION_SIGNS[p_name]
        deb_deg = (deb_sign - 1) * 30 + DEBILITATION_DEGREES[p_name]  # Deep debilitation degree
        
        # Direction-aware difference: add 360 if negative
        dist_from_deb = deg - deb_deg
        if dist_from_deb < 0:
            dist_from_deb += 360.0
            
        # Ensure shortest arc distance relative to exaltation (max 180 degrees)
        if dist_from_deb > 180.0:
            dist_from_deb = 360.0 - dist_from_deb
            
        uccha = dist_from_deb / 9.0  # Max 20 points

        # 3. HADDA BALA
        hadda_lord = get_hadda_lord(sign_idx, deg_in_sign)
        h_status = get_relationship_status(p_name, hadda_lord, relationships)
        hadda = SCORES["Hadda"][h_status]

       # 4. DRESHKANA BALA (LOOKUP TABLE)
        dreshkana_lord = get_drekkana_lord(sign_idx, deg_in_sign)
        d_status = get_relationship_status(p_name, dreshkana_lord, relationships)
        dreshkana = SCORES["Dreshkana"][d_status]

        # 5. NAVAMSHA BALA
        navamsha_sign = int((deg * 9) // 30) % 12
        nav_lord = RASHI_LORDS[navamsha_sign]
        n_status = get_relationship_status(p_name, nav_lord, relationships)
        navamsha = SCORES["Navamsha"][n_status]

        total_pvb = kshetra + uccha + hadda + dreshkana + navamsha
        vishwa_bala = total_pvb / 4.0

        balas[p_name] = {
            "Kshetra": kshetra,
            "Uccha": uccha,
            "Hadda": hadda,
            "Dreshkana": dreshkana,
            "Navamsha": navamsha,
            "Total_PVB": total_pvb,
            "Vishwa_Bala": vishwa_bala
        }
    return balas

# -----------------------------------------------------------------------------
# VARSHESHWARA & SOLAR RETURN ENGINE
# -----------------------------------------------------------------------------

def calculate_varsha_pravesha(natal_dt_utc, target_year):
    """Calculates the exact UTC instant of Transit Sun matching Natal Sun longitude."""
    natal_jd = datetime_to_jd(natal_dt_utc)
    natal_sun_lon = get_planet_sidereal_lon(natal_jd, swe.SUN)

    approx_dt = datetime.datetime(
        target_year, natal_dt_utc.month, natal_dt_utc.day,
        natal_dt_utc.hour, natal_dt_utc.minute
    )
    jd_start = datetime_to_jd(approx_dt) - 3.0

    low, high = jd_start, jd_start + 6.0
    for _ in range(50):
        mid = (low + high) / 2.0
        current_sun_lon = get_planet_sidereal_lon(mid, swe.SUN)
        diff = (current_sun_lon - natal_sun_lon + 180) % 360 - 180
        if diff > 0:
            high = mid
        else:
            low = mid

    vp_jd = (low + high) / 2.0
    return vp_jd, jd_to_datetime(vp_jd)

def determine_varsheshwara(natal_pos, varsha_pos, pv_balas, vp_dt_utc, local_tz_offset):
    """Determines the Varsheshwara (Year Lord) among the 5 Office Bearers (Pancha Adhikaris)."""
    j_asc_sign = int(natal_pos["Ascendant"] // 30)
    janma_lagna_lord = RASHI_LORDS[j_asc_sign]

    v_asc_sign = int(varsha_pos["Ascendant"] // 30)
    varsha_lagna_lord = RASHI_LORDS[v_asc_sign]

    local_vp_dt = vp_dt_utc + datetime.timedelta(hours=local_tz_offset)
    is_day = 6 <= local_vp_dt.hour < 18
    
    trirashi_map = {
        0: ("Sun", "Jupiter"),     # Aries
        1: ("Venus", "Moon"),      # Taurus
        2: ("Saturn", "Mercury"),   # Gemini
        3: ("Venus", "Mars"),      # Cancer
        4: ("Jupiter", "Sun"),     # Leo
        5: ("Moon", "Venus"),      # Virgo
        6: ("Mercury", "Saturn"),  # Libra
        7: ("Mars", "Venus"),      # Scorpio
        8: ("Saturn", "Saturn"),   # Sagittarius
        9: ("Mars", "Mars"),       # Capricorn
        10: ("Jupiter", "Jupiter"),# Aquarius
        11: ("Moon", "Moon")       # Pisces
    }
    tri_rashi_lord = trirashi_map[v_asc_sign][0 if is_day else 1]

    target_year = vp_dt_utc.year
    natal_year = natal_pos.get("birth_year", target_year)
    muntha_sign = (j_asc_sign + (target_year - natal_year)) % 12
    muntha_lord = RASHI_LORDS[muntha_sign]

    # House occupied by Muntha in Varshaphala Chart (1-indexed)
    muntha_house = ((muntha_sign - v_asc_sign) % 12) + 1
    
    dina_ratri_lord = "Sun" if is_day else "Moon"

    candidates = {
        "Janma Lagna Lord": janma_lagna_lord,
        "Varsha Lagna Lord": varsha_lagna_lord,
        "Tri-Rashi Pati": tri_rashi_lord,
        "Muntha Lord": muntha_lord,
        "Dina/Ratri Pati": dina_ratri_lord
    }

    best_lord = None
    max_bala = -1.0

    for role, planet in candidates.items():
        bala = pv_balas[planet]["Vishwa_Bala"]
        if bala > max_bala:
            max_bala = bala
            best_lord = planet

    muntha_info = {
        "sign_name": RASHI_NAMES[muntha_sign],
        "sign_num": muntha_sign + 1,
        "house": muntha_house,
        "lord": muntha_lord
    }

    return candidates, best_lord, max_bala, muntha_info

def get_chart_positions(jd, lat, lon):
    """Calculates positions of Ascendant, 7 Classical Planets, plus Rahu and Ketu."""
    positions = {}
    for p_name, p_id in PLANETS.items():
        positions[p_name] = get_planet_sidereal_lon(jd, p_id)

    # Add Rahu (Mean Node) and Ketu (180 degrees opposite)
    rahu_lon = get_planet_sidereal_lon(jd, swe.MEAN_NODE)
    positions["Rahu"] = rahu_lon
    positions["Ketu"] = (rahu_lon + 180.0) % 360.0

    # Ascendant Calculation
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    positions["Ascendant"] = ascmc[0] % 360.0
    return positions

def calculate_all_tripataka_positions(natal_positions, target_year):
    """
    Calculates Tripataka Chakra progressed positions for all planets:
    - Figure = Completed Years + 1
    - Moon: Divisor 9, counted forward from Natal Moon sign
    - Sun, Mercury, Jupiter, Venus, Saturn: Divisor 4, counted forward from respective Natal sign
    - Mars: Divisor 6, counted forward from Natal Mars sign
    """
    birth_year = natal_positions.get("birth_year", target_year)
    completed_years = target_year - birth_year
    figure = completed_years

    tripataka_results = {}

    # 1. Moon (Divisor 9)
    rem_moon = figure % 9
    if rem_moon == 0:
        rem_moon = 9
    nat_moon_sign = int(natal_positions["Moon"] // 30)
    tripataka_results["Moon"] = (nat_moon_sign + (rem_moon - 1)) % 12

    # 2. Sun, Mercury, Jupiter, Venus, Saturn (Divisor 4)
    group_4_planets = ["Sun", "Mercury", "Jupiter", "Venus", "Saturn"]
    rem_4 = figure % 4
    if rem_4 == 0:
        rem_4 = 4

    for p in group_4_planets:
        if p in natal_positions:
            nat_sign = int(natal_positions[p] // 30)
            tripataka_results[p] = (nat_sign + (rem_4 - 1)) % 12

    # 3. Mars, Rahu, Ketu (Divisor 6)
    rem_6 = figure % 6
    if rem_6 == 0: rem_6 = 6
    for p in ["Mars", "Rahu", "Ketu"]:
        if p in natal_positions:
            nat_sign = int(natal_positions[p] // 30)
            tripataka_results[p] = (nat_sign + (rem_6 - 1)) % 12

    return figure, tripataka_results


def display_full_tripataka_chakra(natal_positions, target_year):
    """Displays Tripataka Chakra table including Mars, Rahu, and Ketu."""
    figure, tp_positions = calculate_all_tripataka_positions(natal_positions, target_year)
    completed_years = target_year - natal_positions.get("birth_year", target_year)

    print("\n" + "=" * 80)
    print(f"{'TRIPATAKA CHAKRA - ALL PLANETS (WITH MARS, RAHU, KETU)':^80}")
    print("=" * 80)
    print(f"Completed Years: {completed_years} | Calculation Figure (Age + 1): {figure}\n")
    print(f"{'Planet':<10} | {'Divisor':<8} | {'Remainder':<10} | {'Natal Sign':<15} | {'Tripataka Sign':<15}")
    print("-" * 80)

    # Moon
    rem_m = figure % 9
    if rem_m == 0: rem_m = 9
    print(f"{'Moon':<10} | {'9':<8} | {rem_m:<10} | {RASHI_NAMES[int(natal_positions['Moon']//30)]:<15} | {RASHI_NAMES[tp_positions['Moon']]:<15}")

    # Group 4
    rem_4 = figure % 4
    if rem_4 == 0: rem_4 = 4
    for p in ["Sun", "Mercury", "Jupiter", "Venus", "Saturn"]:
        print(f"{p:<10} | {'4':<8} | {rem_4:<10} | {RASHI_NAMES[int(natal_positions[p]//30)]:<15} | {RASHI_NAMES[tp_positions[p]]:<15}")

    # Group 6 (Mars, Rahu, Ketu)
    rem_6 = figure % 6
    if rem_6 == 0: rem_6 = 6
    for p in ["Mars", "Rahu", "Ketu"]:
        print(f"{p:<10} | {'6':<8} | {rem_6:<10} | {RASHI_NAMES[int(natal_positions[p]//30)]:<15} | {RASHI_NAMES[tp_positions[p]]:<15}")

    print("-" * 80)

def is_between_zodiacally(point, start, end):
    """Checks if 'point' lies zodiacally between 'start' and 'end' (moving forward 0-360°)."""
    dist_total = (end - start) % 360.0
    dist_point = (point - start) % 360.0
    return dist_point <= dist_total


def calculate_all_50_sahams(positions, is_day):
    """
    Computes all 50 classical Tajika Sahams without wrapping raw longitudes,
    keeping absolute cumulative degree totals for sign formatting.
    """
    asc = positions["Ascendant"]
    sun = positions["Sun"]
    moon = positions["Moon"]
    mars = positions["Mars"]
    mercury = positions["Mercury"]
    jupiter = positions["Jupiter"]
    venus = positions["Venus"]
    saturn = positions["Saturn"]
    
    houses = positions.get("cusps", [asc + i*30 for i in range(12)])
    h2 = houses[1] if len(houses) > 1 else (asc + 30)
    h8 = houses[7] if len(houses) > 7 else (asc + 210)
    h9 = houses[8] if len(houses) > 8 else (asc + 240)

    sahams_registry = {
        "Punya (Fortune/Virtue)":           (moon, sun, False),
        "Vidya (Education/Learning)":       (sun, moon, False),
        "Yasas (Fame/Renown)":              (jupiter, sun, False),
        "Mitra (Friends)":                  (venus, moon, False),
        "Mahatmya (Greatness)":             (mars, moon, False),
        "Asha (Desires/Hope)":              (saturn, mars, False),
        "Samartha (Enterprise/Ability)":    (mars, saturn, False),
        "Bhratri (Brothers/Co-borns)":      (jupiter, saturn, True),
        "Gaurava (Respect/Regard)":         (jupiter, moon, False),
        "Pitri (Father)":                   (saturn, sun, False),
        "Rajya (Kingdom/Authority/Career)": (saturn, sun, False),
        "Matri (Mother)":                   (moon, venus, False),
        "Putra (Children/Progeny)":         (jupiter, moon, False),
        "Jeeva (Life/Longevity)":           (saturn, jupiter, False),
        "Karma (Action/Work)":              (mars, mercury, False),
        "Roga (Disease/Sickness)":          (saturn, moon, True),
        "Kali (Misfortune)":                (jupiter, mars, False),
        "Sastra (Sciences)":                (jupiter, saturn, False),
        "Bandhu (Relatives)":               (mercury, moon, False),
        "Mrityu (Death)":                   (h8, moon, True),
        "Paradesa (Foreign Travel)":        (h9, mercury, True),
        "Artha (Wealth/Money)":             (h2, saturn, True),
        "Paradara (Adultery/Scandal)":      (venus, sun, False),
        "Bandhana (Imprisonment)":          (saturn, mars, False),
        "Vivaha (Marriage)":                (venus, saturn, False),
        "Santapa (Grief/Sorrow)":           (saturn, moon, False),
        "Sanchita (Accumulation)":          (jupiter, sun, False),
        "Jalapatha (Water Travel)":         (moon, saturn, False),
        "Yuddha (War/Conflict)":            (mars, sun, False),
        "Shatru (Enemies)":                 (mars, saturn, False),
        "Vitta (Financial Prosperity)":     (jupiter, sun, False),
        "Vijaya (Victory)":                 (saturn, mars, False),
        "Bhagya (Fortune/Luck)":            (sun, jupiter, False),
        "Karya Siddhi (Success in Tasks)":  (mars, sun, False),
        "Vyapara (Business/Trade)":         (mercury, saturn, False),
        "Moha (Delusion/Attachment)":       (venus, moon, False),
        "Durga (Protection/Safety)":        (mars, sun, False),
        "Arogya (Health/Wellbeing)":        (moon, mars, False),
        "Tapas (Spiritual Practice)":       (jupiter, sun, False),
        "Preeti (Love/Affection)":          (venus, jupiter, False),
        "Sukha (Happiness/Comforts)":       (moon, mercury, False),
        "Duhkha (Misery/Pain)":             (saturn, mars, False),
        "Bhaya (Fear/Danger)":              (mars, saturn, False),
        "Shoka (Lamentation)":              (saturn, sun, False),
        "Labha (Gains)":                    (jupiter, mercury, False),
        "Vyaya (Expenditure)":              (saturn, jupiter, False),
        "Asuya (Jealousy)":                 (mars, venus, False),
        "Mada (Intoxication/Arrogance)":    (venus, mars, False),
        "Chinta (Anxiety/Worry)":           (mercury, saturn, False),
        "Siddhi (Accomplishment)":          (jupiter, mars, False)
    }

    computed_sahams = {}
    
    for name, (subtrahend, minuend, fixed) in sahams_registry.items():
        if fixed:
            p1, p2 = subtrahend, minuend
        else:
            p1, p2 = (subtrahend, minuend) if is_day else (minuend, subtrahend)

        base_deg = p1 - p2 + asc

        if p1 < asc < p2 or p2 < asc < p1:
            base_deg += 0
        else:
            base_deg += 30.0

            
        computed_sahams[name] = {
            "deg": base_deg,
            "p1": p1,
            "p2": p2
        }

    return computed_sahams


def display_all_sahams_report(sahams_data, positions):
    """
    Formats and prints all 50 Sahams displaying both normal absolute degrees 
    (0-360°) and Rashi sign/degree format.
    """
    asc = positions["Ascendant"]
    
    print("\n" + "=" * 135)
    print(f"{'COMPLETE TAJIKA 50 SAHAMS REPORT (DEGREES & RASHI)':^135}")
    print("=" * 135)
    print(f"{'No.':<4} | {'Saham Name':<30} | {'P1 Position':<22} | {'P2 Position':<22} | {'Ascendant':<20} | {'Saham Position':<24}")
    print("-" * 135)
    
    for idx, (name, item) in enumerate(sahams_data.items(), start=1):
        deg = item["deg"]
        p1 = item["p1"]
        p2 = item["p2"]
        
        # Helper to format both absolute normal degrees and Rashi representation
        def format_deg_and_rashi(val):
            norm_val = val % 360.0
            rashi_idx = int(norm_val // 30)
            rem_deg = norm_val % 30
            return f"{norm_val:6.2f}° ({RASHI_NAMES[rashi_idx]} {rem_deg:4.2f}°)"
        
        p1_str = format_deg_and_rashi(p1)
        p2_str = format_deg_and_rashi(p2)
        asc_str = format_deg_and_rashi(asc)
        saham_str = format_deg_and_rashi(deg)
        
        print(f"{idx:<4} | {name:<30} | {p1_str:<22} | {p2_str:<22} | {asc_str:<20} | {saham_str:<24}")
        
    print("-" * 135)

# -----------------------------------------------------------------------------
# VISUAL DISPLAY FUNCTIONS
# -----------------------------------------------------------------------------

def display_chart_grid(title, positions):
    """Generates a text-based South Indian style Rashi Grid."""
    grid = [[] for _ in range(12)]
    
    for name, deg in positions.items():
        if name == "birth_year":
            continue
        sign_idx = int(deg // 30)
        short_name = "Asc" if name == "Ascendant" else name[:3]
        grid[sign_idx].append(short_name)

    def get_sign_str(idx):
        pl = ",".join(grid[idx]) if grid[idx] else "-"
        return f"{idx+1}:{RASHI_NAMES[idx][:3]} [{pl}]"

    print(f"\n+------------------------------------------------------------------------+")
    print(f"| {title.center(70)} |")
    print(f"+------------------------------------------------------------------------+")
    print(f"| {get_sign_str(11):<16} | {get_sign_str(0):<16} | {get_sign_str(1):<16} | {get_sign_str(2):<16} |")
    print(f"|------------------+------------------+------------------+------------------|")
    print(f"| {get_sign_str(10):<16} |                                    | {get_sign_str(3):<16} |")
    print(f"|------------------|                                    |------------------|")
    print(f"| {get_sign_str(9):<16} |                                    | {get_sign_str(4):<16} |")
    print(f"|------------------+------------------+------------------+------------------|")
    print(f"| {get_sign_str(8):<16} | {get_sign_str(7):<16} | {get_sign_str(6):<16} | {get_sign_str(5):<16} |")
    print(f"+------------------------------------------------------------------------+")

# -----------------------------------------------------------------------------
# MAIN INTERACTIVE INPUT & WORKFLOW
# -----------------------------------------------------------------------------

def main():
    print("=" * 80)
    print("      TAJIKA VARSHAPHALA & PANCHA VARGEEYA BALA ENGINE")
    print("=" * 80)
    
    # 1. Interactive Inputs
    print("\n--- ENTER NATAL BIRTH DETAILS ---")
    year = int(input("Birth Year (e.g. 1995): "))
    month = int(input("Birth Month (1-12): "))
    day = int(input("Birth Day (1-31): "))
    hour = int(input("Birth Hour (0-23): "))
    minute = int(input("Birth Minute (0-59): "))
    tz_offset = float(input("Timezone Offset from UTC in hours (e.g. 5.5 for IST, -5 for EST): "))

    print("\n--- ENTER BIRTH PLACE GEOGRAPHY ---")
    lat = float(input("Latitude in decimal degrees (e.g. 28.6139 for North, -23.5 for South): "))
    lon = float(input("Longitude in decimal degrees (e.g. 77.2090 for East, -74.0 for West): "))

    print("\n--- VARSHAPHALA TARGET YEAR ---")
    target_year = int(input("Target Year for Annual Horoscope (e.g. 2026): "))

    # 2. Convert Natal Local Time to UTC
    natal_local_dt = datetime.datetime(year, month, day, hour, minute)
    natal_utc_dt = natal_local_dt - datetime.timedelta(hours=tz_offset)

    # 3. Calculate Natal Chart
    natal_jd = datetime_to_jd(natal_utc_dt)
    natal_positions = get_chart_positions(natal_jd, lat, lon)
    natal_positions["birth_year"] = year

    # 4. Calculate Varsha Pravesha Time & Solar Return Positions
    vp_jd, vp_dt_utc = calculate_varsha_pravesha(natal_utc_dt, target_year)
    vp_local_dt = vp_dt_utc + datetime.timedelta(hours=tz_offset)
    varsha_positions = get_chart_positions(vp_jd, lat, lon)

    # 5. Compute Balas, Tajika Relationships & Varsheshwara
    tajika_rel = calculate_tajika_relationships(varsha_positions)
    pv_balas = calculate_pancha_vargeeya_bala(varsha_positions, tajika_rel)
    adhikaris, varsheshwara, v_bala, muntha_info = determine_varsheshwara(
        natal_positions, varsha_positions, pv_balas, vp_dt_utc, tz_offset
    )

    # 6. PRINT RESULTS
    print("\n" + "=" * 80)
    print(f"VARSHA PRAVESHA TIME (LOCAL TIME): {vp_local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"VARSHA PRAVESHA TIME (UTC):        {vp_dt_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Print Visual Grids
    display_chart_grid("NATAL RASHI CHART", natal_positions)
    display_chart_grid(f"VARSHAPHALA RASHI CHART ({target_year})", varsha_positions)

    # Detailed Longitude Table (DMS)
    print(f"\n{'POSITIONS WITH DEGREES, MINUTES & SECONDS':^80}")
    print("-" * 80)
    print(f"{'Body':<12} | {'Natal Position':<30} | {'Varshaphala Position':<30}")
    print("-" * 80)
    for body in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        natal_str = format_dms(natal_positions[body])
        varsha_str = format_dms(varsha_positions[body])
        print(f"{body:<12} | {natal_str:<30} | {varsha_str:<30}")
    print("-" * 80)

    # PRINT MUNTHA DETAILS
    print(f"\n{'MUNTHA PLACEMENT':^80}")
    print("-" * 80)
    print(f"  Muntha Rashi : {muntha_info['sign_name']} (Sign {muntha_info['sign_num']})")
    print(f"  Varsha House : House {muntha_info['house']} from Varsha Lagna")
    print(f"  Muntha Lord  : {muntha_info['lord']}")
    print("-" * 80)

    # TAJIKA PLANETARY RELATIONSHIPS (DRISHTI BASED)
    print(f"\n{'TAJIKA PLANETARY RELATIONSHIPS (BASED ON DRISHTI / ASPECTS)':^80}")
    print("-" * 80)
    print(f"{'Planet':<8} | {'Friends (3,5,9,11)':<22} | {'Enemies (1,4,7,10)':<22} | {'Neutral (2,6,8,12)':<20}")
    print("-" * 80)
    for p_name, rel in tajika_rel.items():
        print(f"{p_name:<8} | {rel['Friends']:<22} | {rel['Enemies']:<22} | {rel['Neutrals']:<20}")
    print("-" * 80)

    # ACCURATE PANCHA VARGEEYA BALA TABLE
    print(f"\n{'PANCHA VARGEEYA BALA (DYNAMIC BASED ON HADDA & TAJIKA DRISHTI)':^80}")
    print("-" * 80)
    print(f"{'Planet':<8} | {'Kshetra':<8} | {'Uccha':<6} | {'Hadda':<6} | {'Dre.':<5} | {'Nav.':<5} | {'Total':<7} | {'Vishwa Bala':<11}")
    print(f"{'':<8} | {'(Max 30)':<8} | {'(20)':<6} | {'(15)':<6} | {'(10)':<5} | {'(5)':<5} | {'(80)':<7} | {'(Max 20)':<11}")
    print("-" * 80)
    for p_name, b in pv_balas.items():
        print(
            f"{p_name:<8} | {b['Kshetra']:<8.2f} | {b['Uccha']:<6.2f} | {b['Hadda']:<6.2f} | "
            f"{b['Dreshkana']:<5.2f} | {b['Navamsha']:<5.2f} | {b['Total_PVB']:<7.2f} | {b['Vishwa_Bala']:<11.2f}"
        )
    print("-" * 80)

    # Varsheshwara Summary
    print(f"\n{'PANCHA ADHIKARIS (5 OFFICE BEARERS)':^80}")
    print("-" * 80)
    for role, lord in adhikaris.items():
        print(f"  {role:<22}: {lord:<10} (Vishwa Bala: {pv_balas[lord]['Vishwa_Bala']:.2f})")
    print("-" * 80)
    print(f"\n>>> VARSHESHWARA (YEAR LORD): {varsheshwara.upper()} (Vishwa Bala: {v_bala:.2f}) <<<")
    print("=" * 80)

    # PRINT TRIPATAKA CHAKRA
    display_full_tripataka_chakra(natal_positions, target_year)

    # Determine Day/Night status
    local_vp_dt = vp_dt_utc + datetime.timedelta(hours=tz_offset)
    is_day = 6 <= local_vp_dt.hour < 18

    # Generate and print all 50 Sahams
    all_sahams = calculate_all_50_sahams(varsha_positions, is_day)
    display_all_sahams_report(all_sahams, varsha_positions)

if __name__ == "__main__":
    main()
