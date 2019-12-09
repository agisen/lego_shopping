# Lego shopping (v2019-12)
agisen 2017–2019

Allows to add Lego parts to your shopping cart, intended to buy the LHC and ATLAS models.

WARNING! The script remotely controls your browser. The author is not responsible for any unwanted or unintended actions. 
The software is provided "as is", without warranty of any kind.

The part lists are obtained from https://build-your-own-particle-detector.org

## Usage
The script puts Lego parts (IDs and amount given in a CSV file) into your basket.
It uses the official Lego shops "Pick a Brick (PaB)" and "Steine und Teile (SuT)". A price comparision between both shops is also performed.

## Installation
Only tested on Ubuntu. It may also work somewhere else.
### Prerequisites
- Firefox
- selenium: `pip3 install selenium`
- geckodriver:
  1. Go to https://github.com/mozilla/geckodriver/releases/latest
  2. Download and unpack geckodriver (see assets)
  3. Make sure it’s in your PATH, e. g., place it in /usr/bin or /usr/local/bin


### Installation procedure
0. Check that the prerequisites are installed.
1. Download or clone this repository.
2. Excecute `lego_selenium.py`

## Running
Execute `python3 lego_selenium.py test` to see how test bricks (2x ID302001 and 3x ID300121) are placed into your basket.
Execute `python3 lego_selenium.py ATLAS_micro.csv` to perform a price research and put the bricks according to it into your basket. Supported lego-csv-files are 'ATLAS_full.csv', 'ATLAS_mid-size.csv', 'ATLAS_mini.csv', 'ATLAS_micro.csv' 'LHC_micro_full.csv'

Before you actually buy anything, please check the total amount and the total price for consistency.
