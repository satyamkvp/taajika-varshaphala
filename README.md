Installation:
-------------
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip python3-venv

python3 -m venv swe_env
source swe_env/bin/activate

pip install --upgrade pip

pip install pyswisseph

To run the application:
-----------------------
python3 -m venv swe_env
source swe_env/bin/activate

To input details one after another one use
```sh
python3 taajika.py
```

To provide all inputs in one command, use the command-line options below. The
`--name` option is optional; timezone is the offset from UTC in hours.

```sh
python3 taajika.py --name "Example Person" --year 1995 --month 5 --day 10 \
	--hour 14 --minute 30 --timezone 5.5 --latitude 28.6139 \
	--longitude 77.2090 --target-year 2026
```
