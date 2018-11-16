Movebank REST API: Description of download interface to build calls to the Movebank database

Contents
- Introduction
- Security, data access and authentication
- Accessing the database using HTTP/CSV requests
	- Get a list of attribute names
	- Get descriptions of entities in the database
		- Get a list of sensor types
		- Get a list of studies
		- Get a list of studies a user is a data manager for
	- Get descriptions of entities in a study
		- Get a summary of information about the study
		- Get tag reference information from the study
		- Get animal reference information from the study
		- Get deployment reference information from the study
	- Get event data from the study
		- Get event data with all event-level attributes
		- Get event data with selected additional event-level attributes
		- Get event data for a single sensor type
		- Get event data for an individual animal
		- Get event data for a specified time period
	- Other messages you might receive
	- Accessing the database from R

- Accessing the database using JSON/JavaScript requests
	- Get public or private data
	- Get event data from the study
		- Get event data for multiple individuals
		- Get event data for a specified number of events
		- Get event data for a specified time period
		- Get event data with additional event-level attributes
		- Get event data with all of the specifications described above
	- Displaying data using Google Maps
		- Example 1: Tracks with calendar (public data)
		- Example 2: Tracks with calendar (private data)
		- Example 3: Tracks with points and density maps (public data)

## Introduction
Movebank's REST API allows access to pull data from Movebank using HTTP or JSON requests made in a web browser or through external programs such as R. Below are details, example requests, and relevant information about security and access controls.

## Security, data access and authentication
Data access is defined by users for each study in Movebank following [Movebank's permissions options](https://www.movebank.org/node/43). Therefore if no username and password are provided, results will be restricted to data that users have made publicly available. If a username and password are provided, results will be restricted to data that the user has access to. To access tracking actual data, including for visualization on external websites, the username (or the public) needs permission to download data.

In addition to access permissions, for data that are made available to others, [data managers for each study in Movebank specify use conditions in the "License Terms" in the Study Details](https://www.movebank.org/node/11). If no conditions are specified, [the General Movebank Terms of Use](https://www.movebank.org/node/1934) apply.

To ensure that users are aware of the license terms for each study, we require that a user read and accept these terms of use prior to download once for each study accessed. Once a user has accepted the terms of use for a study, they will not be required to accept them again unless the study owner changes the terms of use. These requirements can cause problems with accessing data from external programs or URLs. There are a few ways to resolve these:
- Data managers can disable the requirement that users accept terms of use by unchecking the "Prompt users to accept license terms" box in [the permissions settings for a study](https://www.movebank.org/node/43).
- A user can log on to Movebank and accept the terms of use for the study/ies they want to access prior to attempting to access from an external program.

## Accessing the database using HTTP/CSV requests
The following are examples of how to access information from the Movebank database with HTTP requests. After providing a valid username and password, these calls will return CSV files containing the requested information. Note that the results will be based on the information available to the user as defined by access permissions (see above). For more information about the data model and attributes contained in the database, see Kranstauber et al. (2011) and [the Movebank Attribute Dictionary](https://www.movebank.org/node/2381).

### 1. Get a list of attribute names
`https://www.movebank.org/movebank/service/direct-read?attributes`

This will open a list of available attribute names by entity type that can be used to further specify the example queries below.

### 2. Get descriptions of entities in the database
You may want to query general information about what is contained in the database. You can obtain information about the following entity types in the database prior to specifying a specific study: study, tag_type, taxon. Note that the taxonomy in Movebank comes from [the Integrated Taxonomic Information System](https://www.itis.gov/) (ITIS).

#### 2.1 Get a list of sensor types
`https://www.movebank.org/movebank/service/direct-read?entity_type=tag_type`


Result

```
| description   | external_id              | id        | is_location_sensor   | name                     |
| ------------- | ------------------------ | --------- | -------------------- | ------------------------ |
|               | bird-ring                | 397       | TRUE                 | Bird Ring                |
|               | gps                      | 653       | TRUE                 | GPS                      |
|               | radio-transmitter        | 673       | TRUE                 | Radio Transmitter        |
|               | argos-doppler-shift      | 82798     | TRUE                 | Argos Doppler Shift      |
|               | natural-mark             | 2365682   | TRUE                 | Natural Mark             |
|               | acceleration             | 2365683   | FALSE                | Acceleration             |
|               | solar-geolocator         | 3886361   | TRUE                 | Solar Geolocator         |
|               | accessory-measurements   | 7842954   | FALSE                | Accessory Measurements   |
|               | solar-geolocator-raw     | 9301403   | FALSE                | Solar Geolocator Raw     |
```


From this you can see that the sensor type ID for GPS data is 653 and that the “accessory measurements” sensor does not include location information.

#### 2.2 Get a list of studies
`https://www.movebank.org/movebank/service/direct-read?entity_type=study`

Result


	acknowledgements,bounding_box,citation,comments,grants_used,has_quota,i_am_owner,id,license_terms,location_description,main_location_lat,main_location_long,name,number_of_deployments,number_of_events,number_of_individuals,number_of_tags,principal_investigator_address,principal_investigator_email,principal_investigator_name,study_objective,study_type,suspend_license_terms,timestamp_end,timestamp_start,i_can_see_data,there_are_data_which_i_cannot_see ...

These results provide the study name (`study`), the study ID (`id`), user-provided study details, and information about your username's access permissions. To determine your access rights, filter the list using `i_am_owner`, `i_can_see_data` and/or `there_are_data_which_i_cannot_see`. Remember that you may have permission to see only the study details, view some or all tracks but not download data, or view and download some or all data. Also, there are studies that you do not have permission to see at all—these studies will not be included in the list. Please ignore the columns with summary statistics about the studies (`number_of_deployments`, `number_of_events`, `number_of_individuals`, `number_of_tags`, `timestamp_end`, `timestamp_start`)—these columns are now obsolete.

#### 2.3 Get a list of studies a user is a data manager for
`https://www.movebank.org/movebank/service/direct-read?entity_type=study&i_am_owner=true`

Results will be the same as in the previous example, but filtered for only the studies for which `i_am_owner` contains `TRUE`.

### 3. Get descriptions of entities in a study
When you have a certain study of interest, you can access information contained in that study using the study’s Movebank ID (available in [the Study Details](https://www.movebank.org/node/1942#study_details)). You can obtain information for the following entity types: `study`, `individual`, `tag`, `deployment`, and `event`. The event entities contain actual sensor measurements, while the deployment, individual, and tag entities contain descriptive information about the animals, tags, and deployments (i.e. of tags on animals) in the study. In Movebank we refer to the latter information as "[reference data](https://www.movebank.org/2381#metadata)". For the examples that follow we will use the study "Galapagos Albatrosses" (study ID 2911040) which is fully available to the public.

#### 3.1 Get a summary of information about the study
`https://www.movebank.org/movebank/service/direct-read?entity_type=study&study_id=2911040`

Result

```
|acknowledgements            |bounding_box |citation                                                                                                                                                                                                                                                                       |comments |grants_used        |has_quota |i_am_owner |      id|license_terms                                                                                                                                              |location_description | main_location_lat| main_location_long|name                  | number_of_deployments| number_of_events| number_of_individuals| number_of_tags|principal_investigator_address |principal_investigator_email |principal_investigator_name |study_objective                                                                                                                                                      |study_type |suspend_license_terms |timestamp_end           |timestamp_start         |i_can_see_data |there_are_data_which_i_cannot_see |
|:---------------------------|:------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|:------------------|:---------|:----------|-------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------|-----------------:|------------------:|:---------------------|---------------------:|----------------:|---------------------:|--------------:|:------------------------------|:----------------------------|:---------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------|:---------------------|:-----------------------|:-----------------------|:--------------|:---------------------------------|
|Thanks for help: ECCD, GNPS |             |Dodge S, Bohrer G, Weinzierl R, Davidson SC, Kays R, Douglas D, Cruz S, Han J, Brandes D, Wikelski M (2013) The Environmental-Data Automated Track Annotation (Env-DATA) System—linking animal tracks with environmental data. Movement Ecology 1:3. doi:10.1186/2051-3933-1-3 |         |NSF and Max Planck |true      |false      | 2911040|These data have been published by the Movebank Data Repository with DOI 10.5441/001/1.3hp3s250. See www.datarepository.movebank.org/handle/10255/move.331. |                     |             -1.39|             -89.62|Galapagos Albatrosses |                    35|            16539|                    38|             35|                               |                             |                            |Tracking of Galapagos albatrosses for conservation and basic science. Waved albatrosses were tracked during breeding and non-breeding periods between 2008 and 2010. |research   |true                  |2008-11-10 10:00:00.000 |2008-05-31 13:28:43.000 |true           |false                             |
```


#### 3.2 Get tag reference information from the study
`https://www.movebank.org/movebank/service/direct-read?entity_type=tag&study_id=2911040`

Result

```
|beacon_frequency |comments |      id|local_identifier |manufacturer_name |model |processing_type |serial_no |tag_failure_comments |tag_production_date | weight|
|:----------------|:--------|-------:|:----------------|:-----------------|:-----|:---------------|:---------|:--------------------|:-------------------|------:|
|                 |         | 2911107|131              |e-obs GmbH        |      |                |          |                     |                    |     22|
|                 |         | 2911108|132              |e-obs GmbH        |      |                |          |                     |                    |     22|
|                 |         | 2911109|134              |e-obs GmbH        |      |                |          |                     |                    |     22|
|                 |         | 2911110|135              |e-obs GmbH        |      |                |          |                     |                    |     22|
|                 |         | 2911111|136              |e-obs GmbH        |      |                |          |                     |                    |     22|
```

Attributes listed in the file include tag descriptors currently in the database. Those that have not been provided by the data owner will be blank. The attribute "local_identifier" contains the user-provided tag IDs (which can be changed by the data owner), and the attribute "id" contains internal identifiers automatically created in the database.

#### 3.3 Get animal reference information from the study
`https://www.movebank.org/movebank/service/direct-read?entity_type=individual&study_id=2911040`

Result

```
|comments        |death_comments |earliest_date_born |exact_date_of_birth |      id|latest_date_born |local_identifier |ring_id |sex |taxon_canonical_name |
|:---------------|:--------------|:------------------|:-------------------|-------:|:----------------|:----------------|:-------|:---|:--------------------|
|                |               |                   |                    | 2911059|                 |4264-84830852    |        |    |                     |
|Nest stage: egg |               |                   |                    | 2911066|                 |2131-2131        |        |    |                     |
|Nest stage: egg |               |                   |                    | 2911075|                 |2368-2368        |        |    |                     |
|Nest stage: egg |               |                   |                    | 2911074|                 |3275-30662       |        |    |                     |
|Nest stage: egg |               |                   |                    | 2911078|                 |3606-30668       |        |    |                     |
```
		
#### 3.4 Get deployment reference information from the study
`https://www.movebank.org/movebank/service/direct-read?entity_type=deployment&study_id=2911040`

Result

```
|animal_life_stage |animal_mass |animal_reproductive_condition |attachment_type |behavior_according_to |comments             |data_processing_software |deploy_off_latitude |deploy_off_longitude |deploy_off_person |deploy_off_timestamp | deploy_on_latitude| deploy_on_longitude|deploy_on_person |deploy_on_timestamp |deployment_end_comments |deployment_end_type |duty_cycle                              |geolocator_calibration |geolocator_light_threshold |geolocator_sensor_comments |geolocator_sun_elevation_angle |habitat_according_to |      id|local_identifier |location_accuracy_comments |manipulation_comments |manipulation_type |partial_identifier |study_site       |tag_readout_method |
|:-----------------|:-----------|:-----------------------------|:---------------|:---------------------|:--------------------|:------------------------|:-------------------|:--------------------|:-----------------|:--------------------|------------------:|-------------------:|:----------------|:-------------------|:-----------------------|:-------------------|:---------------------------------------|:----------------------|:--------------------------|:--------------------------|:------------------------------|:--------------------|-------:|:----------------|:--------------------------|:---------------------|:-----------------|:------------------|:----------------|:------------------|
|adult             |            |                              |tape            |                      |not used in analysis |                         |                    |                     |                  |                     |              -1.58|              -81.15|                 |                    |                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 2911170|151-unbanded-151 |                           |                      |none              |                   |Isla de la Plata |other-wireless     |
|adult             |            |                              |tape            |                      |not used in analysis |                         |                    |                     |                  |                     |              -1.58|              -81.15|                 |                    |                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 2911150|153-unbanded-153 |                           |                      |none              |                   |Isla de la Plata |other-wireless     |
|adult             |            |                              |tape            |                      |not used in analysis |                         |                    |                     |                  |                     |              -1.58|              -81.15|                 |                    |                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 2911167|154-unbanded-154 |                           |                      |none              |                   |Isla de la Plata |other-wireless     |
|adult             |            |                              |tape            |                      |not used in analysis |                         |                    |                     |                  |                     |              -1.58|              -81.15|                 |                    |                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 2911168|156-unbanded-156 |                           |                      |none              |                   |Isla de la Plata |other-wireless     |
|adult             |            |                              |tape            |                      |not used in analysis |                         |                    |                     |                  |                     |              -1.58|              -81.15|                 |                    |                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 2911178|159-unbanded-159 |                           |                      |none              |                   |Isla de la Plata |other-wireless     |
```

### 4. Get event data from the study
By default, requests for event data return the event-level dataset (the “tracking data” for location sensors) limited to the variables timestamp, location_lat, location_long, individual_id, tag_id (using internal Movebank identifiers), and including locations not associated with an animal (i.e. there is now `individual_id`) and locations marked as outliers.

`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040`

Result

```
|timestamp               | location_lat| location_long| individual_id|  tag_id|
|:-----------------------|------------:|-------------:|-------------:|-------:|
|2008-05-31 13:30:02.001 |    -1.372641|     -89.74021|       2911059| 2911107|
|2008-05-31 15:00:44.998 |    -1.372894|     -89.74015|       2911059| 2911107|
|2008-05-31 16:30:39.998 |    -1.372881|     -89.74014|       2911059| 2911107|
|2008-05-31 18:00:49.998 |    -1.372891|     -89.74016|       2911059| 2911107|
|2008-05-31 19:30:18.998 |    -1.372912|     -89.74013|       2911059| 2911107|
```

However, datasets often contain additional variables, and non-location sensors (e.g. geolocators and accelerometers) do not contain location coordinates. In addition, if any filtering has been done on the study (e.g. to flag outliers) it might be important to receive the 'visible' and outlier attributes.

#### 4.1 Get event data with all event-level attributes
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&attributes=all`

Result

```
|individual_id|deployment_id| tag_id|study_id|sensor_type_id|eobs_battery_voltage|eobs_fix_battery_voltage|eobs_horizontal_accuracy_estimate|eobs_key_bin_checksum|eobs_speed_accuracy_estimate|eobs_start_timestamp   |eobs_status|eobs_temperature|eobs_type_of_fix|eobs_used_time_to_get_fix|ground_speed|heading|height_above_ellipsoid|location_lat|location_long|timestamp              |visible|event_id|
|:------------|------------:|------:|-------:|-------------:|-------------------:|-----------------------:|--------------------------------:|--------------------:|---------------------------:|----------------------:|----------:|---------------:|---------------:|------------------------:|-----------:|------:|---------------------:|-----------:|------------:|----------------------:|------:|-------:|
|      2911059|      9472219|2911107| 2911040|           653|                3686|                    3437|                            12.03|           2396171168|                        0.67|2008-05-31 13:28:48.000|"A"        |              12|               3|                       74|        0.01|  21.63|                  16.5|   -1.372641|   -89.740214|2008-05-31 13:30:02.001|true   |28192174|
|      2911059|      9472219|2911107| 2911040|           653|                3701|                    3452|                             2.82|           2700991056|                        0.24|2008-05-31 14:59:59.000|"A"        |              19|               3|                       45|         0.0|  95.68|                  12.6|  -1.3728941|  -89.7401542|2008-05-31 15:00:44.998|true   |28192175|
|      2911059|      9472219|2911107| 2911040|           653|                3701|                    3482|                             4.35|            540734184|                        2.57|2008-05-31 16:30:00.000|"A"        |              24|               3|                       39|        0.11|  13.76|                  17.4|  -1.3728809|  -89.7401401|2008-05-31 16:30:39.998|true   |28192176|
|      2911059|      9472219|2911107| 2911040|           653|                3691|                    3476|                             2.82|           2845350485|                        2.61|2008-05-31 18:00:00.000|"A"        |              18|               3|                       49|         0.2|   9.83|                  24.8|  -1.3728911|  -89.7401596|2008-05-31 18:00:49.998|true   |28192177|
|      2911059|      9472219|2911107| 2911040|           653|                3691|                    3541|                             4.61|           1429925913|                         2.7|2008-05-31 19:30:00.000|"A"        |              22|               3|                       18|        0.24|  37.36|                  19.0|  -1.3729121|   -89.740127|2008-05-31 19:30:18.998|true   |28192178|
```

This could provide more information (and data volume) than is needed for a given purpose, so it is also possible to specify which variables to include.

#### 4.2 Get event data with selected additional event-level attributes
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&attributes=individual_id,timestamp,location_long,location_lat,visible`

Result

```
| individual_id|timestamp               | location_long| location_lat|visible |
|-------------:|:-----------------------|-------------:|------------:|:-------|
|       2911059|2008-05-31 13:30:02.001 |     -89.74021|    -1.372641|true    |
|       2911059|2008-05-31 15:00:44.998 |     -89.74015|    -1.372894|true    |
|       2911059|2008-05-31 16:30:39.998 |     -89.74014|    -1.372881|true    |
|       2911059|2008-05-31 18:00:49.998 |     -89.74016|    -1.372891|true    |
|       2911059|2008-05-31 19:30:18.998 |     -89.74013|    -1.372912|true    |
```

Here you can specify the order and inclusion of specific event-level attributes. See “get a list of attribute names” above for available attributes. Note that filtering for some attributes may not work. Please contact support@movebank.org if you find an attribute that is not included in results.

#### 4.1 Get event data for a single sensor type
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&sensor_type_id=653`

Result

```
|timestamp               | location_lat| location_long| individual_id|  tag_id|
|:-----------------------|------------:|-------------:|-------------:|-------:|
|2008-05-31 13:30:02.001 |    -1.372641|     -89.74021|       2911059| 2911107|
|2008-05-31 15:00:44.998 |    -1.372894|     -89.74015|       2911059| 2911107|
|2008-05-31 16:30:39.998 |    -1.372881|     -89.74014|       2911059| 2911107|
|2008-05-31 18:00:49.998 |    -1.372891|     -89.74016|       2911059| 2911107|
|2008-05-31 19:30:18.998 |    -1.372912|     -89.74013|       2911059| 2911107|
```

If multiple sensor types are used in a study, use this to access event-level data for a specific sensor. See “get a list of sensor types” above for the `sensor_type_id` for each sensor type.

#### 4.2 Get event data for an individual animal
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&individual_id=2911059`

Result

```
|timestamp               | location_lat| location_long| individual_id|  tag_id|
|:-----------------------|------------:|-------------:|-------------:|-------:|
|2008-05-31 13:30:02.001 |    -1.372641|     -89.74021|       2911059| 2911107|
|2008-05-31 15:00:44.998 |    -1.372894|     -89.74015|       2911059| 2911107|
|2008-05-31 16:30:39.998 |    -1.372881|     -89.74014|       2911059| 2911107|
|2008-05-31 18:00:49.998 |    -1.372891|     -89.74016|       2911059| 2911107|
|2008-05-31 19:30:18.998 |    -1.372912|     -89.74013|       2911059| 2911107|
```

The individual_id refers to the internal Movebank identifier for each animal in Movebank (which does not change if the user changes the Animal ID). You can view these identifiers in [the Event Editor](https://www.movebank.org/node/42) or contact support@movebank.org for help.

#### 4.3 Get event data for a specified time period
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&timestamp_start=20080604133045000&timestamp_end=20080604133046000`

Result

```
|timestamp               |location_lat |location_long | individual_id|  tag_id|
|:-----------------------|:------------|:-------------|-------------:|-------:|
|2008-06-04 13:30:45.999 |-1.9960011   |-85.1520954   |       2911059| 2911107|
|2008-06-04 13:30:45.000 |-1.372639    |-89.7404519   |       2911060| 2911109|
|2008-06-04 13:30:45.998 |-5.8555544   |-81.2025874   |       2911064| 2911131|
|2008-06-04 13:30:45.001 |-1.3729218   |-89.7402634   |       2911065| 2911134|
|2008-06-04 13:30:45.000 |             |              |       2911059| 2911107|
|2008-06-04 13:30:45.000 |             |              |       2911060| 2911109|
|2008-06-04 13:30:45.000 |             |              |       2911064| 2911131|
|2008-06-04 13:30:45.000 |             |              |       2911065| 2911134|
```

Timestamps should be provided in the format `yyyyMMddHHmmssSSS` (see [list of letter meanings](http://fmpp.sourceforge.net/datetimepattern.html)).

### Other messages you might receive
It may happen that you see the license terms instead of getting the data you have requested. In this case you may get a result like

```html
The requested download may contain copyrighted material. You may only download it if you agree with the terms listed below. If study-specific terms have not been specified, read the "General Movebank Terms of Use".<p>
<div style="font-weight:bold;">Study License Information valid at 2013-04-12 07:25:35</div>
<br>
<span style="font-weight:bold;">Name: </span>BCI Agouti<br>
<span style="font-weight:bold;font-style:italic;">Citation: </span>No papers written<br>
<span style="font-weight:bold;font-style:italic;">Acknowledgements: </span>Field work conducted by Roland Kays and Ben Hirsch<br>
<span style="font-weight:bold;font-style:italic;">Grants Used: </span>Funding provided by the Max Plank Institute, National Science Foundation, and Smithsonian Tropical Research Institute. <br>
<span style="font-weight:bold;font-style:italic;">License Terms: </span>These data may be used for any educational or scientific purpose with proper acknowledgement.<br>
<span style="font-weight:bold;font-style:italic;">Principal Investigator Name: </span>Roland Kays<br>
<br>
</p>
```

At the same time you will get a response header `accept-license: true`. This means that you have yet to accept the license terms for the study, which data managers can optionally require users to do once for a given study as described above.

If you request data that you do not have permission to see, you will get a message

```html
<p>No data available.</p><p>Please contact the data owner for permission to access data.</p>
```

### Accessing the database from R
The HTTP/CSV requests can be used to access Movebank data from R. [The R package `move`](http://cran.r-project.org/web/packages/move/index.html) provides flexible options for browsing and visualizing data from Movebank in R. In addition, [the package source files](https://r-forge.r-project.org/scm/viewvc.php/pkg/move/R/WebImport.R?view=markup&root=move) provide information that can be used to access Movebank from R without the package.

## Accessing the database using JSON/JavaScript requests
The following are examples for how to access Movebank data using JSON requests. This is currently designed primarily to allow tracking data to be displayed on external maps using the Google Maps API (see below). You will need the relevant study ID number and sensor type description in the database to access data (see above).

### Get public or private data
In the examples below, we use URLs that do not include usernames or passwords. In order to access data from a study without providing login information, the study must be completely accessible to the public as described above. Consider [making data publicly available](https://www.movebank.org/node/43#public_full_access) so that data can be accessed without providing any login information. Remember that making data available does not give others permission to use your data, and that license terms still apply. If data are public, the http request should begin with `https://www.movebank.org/movebank/service/public/json?`, for example

`https://www.movebank.org/movebank/service/public/json?&study_id=2911040&individual_local_identifiers[]=4262-84830876&max_events_per_individual=5&sensor_type=gps`

Result

```
{"individuals":[{"study_id":2911040,"individual_local_identifier":"4262-84830876","individual_taxon_canonical_name":"Phoebastria irrorata","sensor_type_id":653,"locations":[{"timestamp":1215324043998,"location_long":-89.7400432,"location_lat":-1.3725996},{"timestamp":1215329423999,"location_long":-89.7400444,"location_lat":-1.3725973},{"timestamp":1215334824998,"location_long":-89.740062,"location_lat":-1.3725946},{"timestamp":1215340256001,"location_long":-89.7400632,"location_lat":-1.3726035},{"timestamp":1215345626998,"location_long":-89.7400716,"location_lat":-1.3726746}]}]}
If data are not public, the http request should begin with `https://www.movebank.org/movebank/service/json-auth?`, for example
```

`https://www.movebank.org/movebank/service/json-auth?&study_id=2911040&individual_local_identifiers[]=4262-84830876&max_events_per_individual=5&sensor_type=gps`

The browser will prompt you to provide your Movebank username and password before proceeding with the request. Alternatively, you can provide user credentials using PHP that can be stored on your local server. For example,

```php
<?php
$url='https://www.movebank.org/movebank/service/json-auth?study_id=16880941&individual_local_identifiers[]=Mary&individual_local_identifiers[]=Butterball&individual_local_identifiers[]=Schaumboch&&max_events_per_individual=2000&sensor_type=gps';

$user=‘username’;
$password=‘password’;

$context = stream_context_create(array(
    'http' => array(
        'header'  => "Authorization: Basic " . base64_encode("$user:$password")
    )
));
```

### Get event data from the study
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&sensor_type=gps`

Result

```
{"individuals":[{"individual_local_identifier":"4262-84830876","individual_taxon_canonical_name":"Phoebastria irrorata","locations":[
{"timestamp":1212240595000,"location_long":-89.7400582,"location_lat":-1.372675},
{"timestamp":1212240618999,"location_long":-89.740053,"location_lat":-1.3726544},
{"timestamp":1212246021998,"location_long":-89.7400575,"location_lat":-1.3726589},
{"timestamp":1212251449999,"location_long":-89.7400497,"location_lat":-1.3726499},
{"timestamp":1212256913000,"location_long":-89.7400693,"location_lat":-1.3726749},
...
```

This example contains the minimum information needed to obtain data: a study ID, an animal ID (here the user-provided name), and a sensor type. You can make several additional variations to this, described below. The timestamps are provided in milliseconds since `1970-01-01 UTC`, and coordinates are in WGS84.

#### Get event data for multiple individuals
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&individual_local_identifiers[]=1163-1163&individual_local_identifiers[]=2131-2131&sensor_type=gps`

Results will be in the same format as in the previous example, with a header like the first line in the previous example added before the first row of data for each individual. You can also use the internal Movebank animal identifiers (which cannot be changed by users) by replacing `individual_local_identifier`s with `individual_id`s.

#### Get event data for a specified number of events
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&max_events_per_individual=10&sensor_type=gps`

Results will be in the same format, but will be restricted to the most recent 10 records per individual. This can be used to reduce the page loading time.

#### Get event data for a specified time period
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&timestamp_start=1213358400000&timestamp_end=1213617600000&sensor_type=gps`

Results will be in the same format, but will be restricted to events within the specified time range. This can be used to highlight (or exclude) a certain portion of a track or to reduce the page loading time. The timestamps must be provided in milliseconds since 1970-01-01 (converters are available online). All dates in Movebank are stored in UTC. Here we obtain locations collected between `2008-6-13 12:00` and `2008-6-16 12:00`.

#### Get event data with additional event-level attributes
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&sensor_type=gps&attributes=timestamp,location_long,location_lat,ground_speed,heading`

Result

```
{"individuals":[{"individual_local_identifier":"4262-84830876","individual_taxon_canonical_name":"Phoebastria irrorata","locations":[
{"timestamp":1212240595000,"location_long":-89.7400582,"location_lat":-1.372675,"timestamp":1212240595000,"location_lat":-1.372675,"ground_speed":0,"location_long":-89.7400582,"heading":0},
{"timestamp":1212240618999,"location_long":-89.740053,"location_lat":-1.3726544,"timestamp":1212240618999,"location_lat":-1.3726544,"ground_speed":0.03,"location_long":-89.740053,"heading":357.17},
{"timestamp":1212246021998,"location_long":-89.7400575,"location_lat":-1.3726589,"timestamp":1212246021998,"location_lat":-1.3726589,"ground_speed":0.05,"location_long":-89.7400575,"heading":1.31},
{"timestamp":1212251449999,"location_long":-89.7400497,"location_lat":-1.3726499,"timestamp":1212251449999,"location_lat":-1.3726499,"ground_speed":0.06,"location_long":-89.7400497,"heading":359.14},
{"timestamp":1212256913000,"location_long":-89.7400693,"location_lat":-1.3726749,"timestamp":1212256913000,"location_lat":-1.3726749,"ground_speed":0,"location_long":-89.7400693,"heading":317.19},
…
```

Results will include additional specified attributes if they are available in the dataset. To see other available attributes that may be in the dataset, see the Movebank Attribute Dictionary (www.movebank.org/node/2381).

#### Get event data with all of the specifications described above
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers[]=4262-84830876&individual_local_identifiers[]=1163-1163&individual_local_identifiers[]=2131-2131&max_events_per_individual=10&timestamp_start=1213358400000&timestamp_end=1213617600000&sensor_type=gps&attributes=timestamp,location_long,location_lat,ground_speed,heading`

Result

```
{"individuals":[{"individual_local_identifier":"4262-84830876","individual_taxon_canonical_name":"Phoebastria irrorata","locations":[
{"timestamp":1213563618999,"location_long":-81.0542399,"location_lat":-2.480352,"timestamp":1213563618999,"location_lat":-2.480352,"ground_speed":0.38,"location_long":-81.0542399,"heading":281.8},{"timestamp":1213569055998,"location_long":-81.0604295,"location_lat":-2.4729733,"timestamp":1213569055998,"location_lat":-2.4729733,"ground_speed":0.75,"location_long":-81.0604295,"heading":337.51},{"timestamp":1213574479998,"location_long":-81.0243416,"location_lat":-2.5038063,"timestamp":1213574479998,"location_lat":-2.5038063,"ground_speed":0.16,"location_long":-81.0243416,"heading":65.54},{"timestamp":1213579820999,"location_long":-81.0270371,"location_lat":-2.4921158,"timestamp":1213579820999,"location_lat":-2.4921158,"ground_speed":0.4,"location_long":-81.0270371,"heading":7.86},{"timestamp":1213585247999,"location_long":-81.0242051,"location_lat":-2.4931081,"timestamp":1213585247999,"location_lat":-2.4931081,"ground_speed":0.5,"location_long":-81.0242051,"heading":94.37},{"timestamp":1213590668998,"location_long":-81.0211194,"location_lat":-2.5433086,"timestamp":1213590668998,"location_lat":-2.5433086,"ground_speed":0.54,"location_long":-81.0211194,"heading":21.63},
```

As shown here, the specifications provided in the examples can be combined to further define what you want to access. The following is a template summarizing everything we've just described.

`https://www.movebank.org/movebank/service/public/json?study_id=<study id>&individual_local_identifiers[]=<animal ID 1>&individual_local_identifiers[]=<animal ID 2 (optional)>&max_events_per_individual=<maximum number of records to access (optional)>&timestamp_start=<timestamp in milliseconds since 1/1/1970 (optional)>&timestamp_end=<timestamp in milliseconds since 1/1/1970 (optional)>&sensor_type=<sensor type>&attributes=<attributes to display in results (optional)>`

### Displaying data using Google Maps
The JSON/JavaScript requests were designed primarily to allow users to access and display mapped Movebank data on external web pages using the Google Maps API. See [Movebank Map Demo](https://github.com/movebank/movebank-map-demo) for example code for maps that pull data from Movebank with JSON requests as described above.