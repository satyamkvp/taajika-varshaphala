# Build environment:

This is primarily developed and tested on Ubuntu/WSL.

# Installation:

Install essentials.
```sh
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip python3-venv
```
Install virtual environment
```sh
python3 -m venv swe_env
source swe_env/bin/activate
```
Install ephemeris package
```sh
pip install --upgrade pip
pip install pyswisseph
```

# To run the application:

Enter the virtual environment.
**If pyswisseph is not recognized, re-install it.**
```sh
python3 -m venv swe_env
source swe_env/bin/activate
```

To input details one after another one use below command. The program asks for
an optional name first; when provided, it is shown at the beginning and end of
the report.
```sh
python3 taajika.py
```

To provide all inputs in one command, use the command-line options below.
The `--name` option is optional; timezone is the offset from UTC in hours.

```sh
python3 taajika.py --name "Example Person" --year 1995 --month 5 --day 10 \
	--hour 14 --minute 30 --timezone 5.5 --latitude 28.6139 \
	--longitude 77.2090 --target-year 2026
```

Display the application version with `python3 taajika.py --version`. See
[REVISION_HISTORY.md](REVISION_HISTORY.md) for release history.

# Example
Sample report for a person born on

Date      : 30-Sep-2000  
Time      : 04:45AM  
Time zone : India (GMT + 5:30 hrs)  
Longitude : 80 E 09  
Latitude  : 16 N 23  
Varshaphala for year : 2026

```sh
python3 taajika.py --name abcd --year 2000 --month 9 --day 30 --hour 04 --minute 45 --timezone 5.5 --latitude 16.23 --longitude 80.09 --target-year 2026
================================================================================
           TAJIKA VARSHAPHALA & PANCHA VARGEEYA BALA 
                         Version 1.0
================================================================================

Varshaphala Report for : abcd

================================================================================
VARSHA PRAVESHA TIME (LOCAL TIME): 2026-09-30 20:35:05
VARSHA PRAVESHA TIME (UTC):        2026-09-30 15:05:05
================================================================================

+------------------------------------------------------------------------+
|                           NATAL RASHI CHART                            |
+------------------------------------------------------------------------+
| 12:Pis [-]       | 1:Ari [-]        | 2:Tau [Jup,Sat]  | 3:Gem [Rah]      |
|------------------+------------------+------------------+------------------|
| 11:Aqu [-]       |                                    | 4:Can [-]        |
|------------------|                                    |------------------|
| 10:Cap [-]       |                                    | 5:Leo [Mar,Asc]  |
|------------------+------------------+------------------+------------------|
| 9:Sag [Ket]      | 8:Sco [-]        | 7:Lib [Moo,Mer,Ven] | 6:Vir [Sun]      |
+------------------------------------------------------------------------+

+------------------------------------------------------------------------+
|                     VARSHAPHALA RASHI CHART (2026)                     |
+------------------------------------------------------------------------+
| 12:Pis [Sat]     | 1:Ari [Asc]      | 2:Tau [Moo]      | 3:Gem [-]        |
|------------------+------------------+------------------+------------------|
| 11:Aqu [Rah]     |                                    | 4:Can [Mar,Jup]  |
|------------------|                                    |------------------|
| 10:Cap [-]       |                                    | 5:Leo [Ket]      |
|------------------+------------------+------------------+------------------|
| 9:Sag [-]        | 8:Sco [-]        | 7:Lib [Mer,Ven]  | 6:Vir [Sun]      |
+------------------------------------------------------------------------+

                   POSITIONS WITH DEGREES, MINUTES & SECONDS                    
--------------------------------------------------------------------------------
Body         | Natal Position                 | Varshaphala Position          
--------------------------------------------------------------------------------
Ascendant    | Leo         24° 24' 03"        | Aries       29° 32' 47"       
Sun          | Virgo       13° 14' 27"        | Virgo       13° 14' 27"       
Moon         | Libra       10° 27' 51"        | Taurus      04° 22' 11"       
Mars         | Leo         14° 17' 26"        | Cancer      07° 14' 19"       
Mercury      | Libra       07° 51' 34"        | Libra       05° 57' 10"       
Jupiter      | Taurus      17° 22' 17"        | Cancer      25° 17' 30"       
Venus        | Libra       12° 38' 37"        | Libra       14° 07' 18"       
Saturn       | Taurus      06° 50' 33"        | Pisces      17° 22' 28"       
--------------------------------------------------------------------------------

                                MUNTHA PLACEMENT                                
--------------------------------------------------------------------------------
  Muntha Rashi : Libra (Sign 7)
  Varsha House : House 7 from Varsha Lagna
  Muntha Lord  : Venus
--------------------------------------------------------------------------------

          TAJIKA PLANETARY RELATIONSHIPS (BASED ON DRISHTI / ASPECTS)           
--------------------------------------------------------------------------------------------------------------------
Planet   | Friends (3,5,9,11)                   | Enemies (1,4,7,10)                   | Neutral (2,6,8,12)                  
--------------------------------------------------------------------------------------------------------------------
Sun      | Moon, Mars, Jupiter                  | Saturn                               | Mercury, Venus                      
Moon     | Sun, Mars, Jupiter, Saturn           | -                                    | Mercury, Venus                      
Mars     | Sun, Moon, Saturn                    | Mercury, Jupiter, Venus              | -                                   
Mercury  | -                                    | Mars, Jupiter, Venus                 | Sun, Moon, Saturn                   
Jupiter  | Sun, Moon, Saturn                    | Mars, Mercury, Venus                 | -                                   
Venus    | -                                    | Mars, Mercury, Jupiter               | Sun, Moon, Saturn                   
Saturn   | Moon, Mars, Jupiter                  | Sun                                  | Mercury, Venus                      
--------------------------------------------------------------------------------------------------------------------

         PANCHA VARGEEYA BALA (DYNAMIC BASED ON HADDA & TAJIKA DRISHTI)         
--------------------------------------------------------------------------------
Planet   | Kshetra  | Uccha  | Hadda  | Dre.  | Nav.  | Total   | Vishwa Bala
         | (Max 30) | (20)   | (15)   | (10)  | (5)   | (80)    | (Max 20)   
--------------------------------------------------------------------------------
Sun      | 15.00    | 2.97   | 7.50   | 5.00  | 3.75  | 34.22   | 8.56       
Moon     | 15.00    | 19.85  | 7.50   | 5.00  | 3.75  | 51.10   | 12.77      
Mars     | 22.50    | 2.31   | 3.75   | 2.50  | 1.25  | 32.31   | 8.08       
Mercury  | 7.50     | 17.67  | 7.50   | 5.00  | 1.25  | 38.92   | 9.73       
Jupiter  | 22.50    | 17.75  | 15.00  | 7.50  | 3.75  | 66.50   | 16.62      
Venus    | 30.00    | 1.90   | 3.75   | 5.00  | 2.50  | 43.15   | 10.79      
Saturn   | 22.50    | 3.63   | 7.50   | 7.50  | 3.75  | 44.88   | 11.22      
--------------------------------------------------------------------------------

                      PANCHA ADHIKARIS (5 OFFICE BEARERS)                       
--------------------------------------------------------------------------------
  Janma Lagna Lord      : Sun        (Vishwa Bala: 8.56)
  Varsha Lagna Lord     : Mars       (Vishwa Bala: 8.08)
  Tri-Rashi Pati        : Jupiter    (Vishwa Bala: 16.62)
  Muntha Lord           : Venus      (Vishwa Bala: 10.79)
  Dina/Ratri Pati       : Moon       (Vishwa Bala: 12.77)
--------------------------------------------------------------------------------

>>> VARSHESHWARA (YEAR LORD): JUPITER (Vishwa Bala: 16.62) <<<
================================================================================

================================================================================
             TRIPATAKA CHAKRA - ALL PLANETS (WITH MARS, RAHU, KETU)             
================================================================================
Completed Years: 26 | Calculation Figure (Age): 26

Planet     | Divisor  | Remainder  | Natal Sign      | Tripataka Sign 
--------------------------------------------------------------------------------
Moon       | 9        | 8          | Libra           | Taurus         
Sun        | 4        | 2          | Virgo           | Libra          
Mercury    | 4        | 2          | Libra           | Scorpio        
Jupiter    | 4        | 2          | Taurus          | Gemini         
Venus      | 4        | 2          | Libra           | Scorpio        
Saturn     | 4        | 2          | Taurus          | Gemini         
Mars       | 6        | 2          | Leo             | Virgo          
Rahu       | 6        | 2          | Gemini          | Cancer         
Ketu       | 6        | 2          | Sagittarius     | Capricorn      
--------------------------------------------------------------------------------
```

# Contact:

Please feel free to file issues in the github for any support.