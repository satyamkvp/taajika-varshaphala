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

python3 taajika.py
