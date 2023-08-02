# Cityscape Generator

This repository contains code that procedurally generates 3D cityscape environments by packing randomized building models.

## Contents

The repository includes the following key components:

- `buildings/` - Folder containing raw 3D building STL models
- `tools/` - Python scripts for some useful tools
  - `match_scale.py` - Matches model scales between groups
- `building_model_preprocess.py` - Preprocesses building STL models
- `city_generator.py` - Generates cityscape scenes by packing models
- `requirements.txt` - Python package dependencies

## Usage

The overall workflow is:

1. Prepare building model library in `buildings/`
2. Run `building_model_preprocess.py` to standardize models
3. (Optional) Run `match_scale.py` to match the scale of different groups of models
4. Run `city_generator.py` to create cityscapes
5. Generated cityscapes are placed in `output/` (or any folder the user preferred)

Key parameters like city dimensions and building density can be configured in `city_generator.py`.

## Installation

Clone the repository:

```
git clone https://github.com/DreamCatcher096/random-city-generator.git
```

Install dependencies:

```
pip install -r requirements.txt
```

## Credits

The rectangle packing algorithm used in this project is provided by [Rectpack](https://github.com/secnot/rectpack).
