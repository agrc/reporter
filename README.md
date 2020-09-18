# agrc/reporter

![reporter](https://user-images.githubusercontent.com/325813/93257934-d8860300-f75a-11ea-83f1-89e00ce71c9c.png)

A framework for systematically and regularly creating reports.

Currently implemented reports:

1. AGOL Hosted feature service information and usage

## Installation

1. Create new environment for the project
   - `conda create --clone arcgispro-py3 --name reporter` (or an enviornment name of your choice)
1. Download reporter
   - `activate reporter`
   - `cd path/to/desired/folder`
   - `git clone https://github.com/agrc/reporter`
1. Install reporter
   - `cd reporter`
   - `pip install -e .`
1. Update the credentials file
   - Copy `src/reporter/credentials_template.py` to `src/reporter/credentials.py`
   - Add the necessary information to `credentials.py`

## Usage

1. Activate your environment
   - `activate reporter`
1. Run reporter
   - `reporter`
