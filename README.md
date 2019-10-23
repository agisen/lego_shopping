# LEGO Scraping (v2019-09)
agisen 2017–2019

Allows to add LEGO parts to your shopping cart, intended to buy the LHC and ATLAS models.

The script remotely controls your browser. The author is not responsible for any unwanted or unintended actions. 
The software is provided "as is", without warranty of any kind.

The part lists are obtained from https://build-your-own-particle-detector.org

## Usage
The script puts LEGO parts (IDs and amount given in a CSV file) into your basket.
It uses the official LEGO shops "Pick a Brick (PaB)" and "Steine und Teile (SuT)". A comparision between both shops is also possible.

## Installation
### Prerequisites
Firefox.
selenium: pip3 install selenium
geckodriver: 
1. Go to https://github.com/mozilla/geckodriver/releases/latest
2. Download and unpack geckodriver (see assets)
3. Make sure it’s in your PATH, e. g., place it in /usr/bin or /usr/local/bin


### Installation procedure
0. Check that the prerequisites are installed.
1. Download or clone this repository.
2. `python3 lego_selenium.py`

## Running
Execute `python3 lego_selenium.py test` to see run a test brick (ID302001) is putted into your basket.
Execute `python3 lego_selenium.py ATLAS_micro.csv` 
