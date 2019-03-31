There is currently no central, up-to-date demographics dataset for Chicago wards. This repository attempts to fill this need. Census block groups are mapped to Chicago wards using their boundaries. Block group census data is then aggregated by ward. All census information comes from the 2017 ACS 5-year estimates.

**block_group_ward_mapping.csv** contains the mapping of census block groups to Chicago wards.

**ward_demographics.csv** contains demographic information for each ward. The following variables are included in the dataset (all as percentages of total ward population):

* Race: White; Black; Asian

* Ethnicity: Hispanic

* Household income: <$24,999; $25,000-49,999; $50,000-99,999; $100,000-149,999; $150,000+

**ward_demographics_boundaries.csv** contains all the information in **ward_demographics.csv**, along with the boundaries of the wards for ease of constructing maps.

An interactive map of the data can be found at https://www.pauldouglasinstitute.org/chicago-data

# Data Sources:
ACS data: https://factfinder.census.gov 

* Guided Search -> I'm looking for information about people. -> *Select topic* -> Add one or more geographic areas (states, cities, towns, etc.) to Your Selections. Click Next.: Block Group/Illinois/Cook/All Block Groups within Cook County, Illinois -> *Select dataset*

Census block group boundaries shapefile: https://www.census.gov/geo/maps-data/data/tiger-line.html

Chicago ward boundaries shapefile: https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Wards-2015-/sp34-6z76