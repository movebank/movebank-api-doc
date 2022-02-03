Movebank REST API: Description of download interface to build calls to the Movebank database

Contents
- [Introduction](#introduction)
- [Security, data access and authentication](#security-data-access-and-authentication)
    - [Read and accept license terms using curl](#read-and-accept-license-terms-using-curl)
- [Accessing the database using HTTP/CSV requests](#accessing-the-database-using-httpcsv-requests)
	- [Get a list of attribute names](#get-a-list-of-attribute-names)
	- [Get descriptions of entities in the database](#get-descriptions-of-entities-in-the-database)
		- [Get a list of sensor types](#get-a-list-of-sensor-types)
		- [Get a list of studies](#get-a-list-of-studies)
		- [Get a list of studies a user is data manager for](#get-a-list-of-studies-a-user-is-data-manager-for)
	- [Get descriptions of entities in a study](#get-descriptions-of-entities-in-a-study)
		- [Get a description about a study](#get-a-description-about-a-study)
		- [Get information about tags in a study](#get-information-about-tags-in-a-study)
		- [Get information about animals in a study](#get-information-about-animals-in-a-study)
		- [Get information about deployments in a study](#get-information-about-deployments-in-a-study)
		- [Get information about tag sensors in a study](#get-information-about-tag-sensors-in-a-study)
		- [Get study attributes for a sensor in a study](#get-study-attributes-for-a-sensor-in-a-study)
	- [Get event data from a study](#get-event-data-from-a-study)
		- [Get event data with all event-level attributes](#get-event-data-with-all-event-level-attributes)
		- [Get event data with select additional event-level attributes](#get-event-data-with-select-additional-event-level-attributes)
		- [Get event data for a single sensor type](#get-event-data-for-a-single-sensor-type)
		- [Get event data for an individual animal](#get-event-data-for-an-individual-animal)
		- [Get event data for a specified time period](#get-event-data-for-a-specified-time-period)
	- [Other messages you might receive](#other-messages-you-might-receive)
	- [Accessing the database from R](#accessing-the-database-from-r)

- [Accessing the database using JSON/JavaScript requests](#accessing-the-database-using-jsonjavascript-requests)
	- [Get public or private data](#get-public-or-private-data)
	- [Get event data from the study](#get-event-data-from-the-study)
		- [Get event data for multiple individuals](#get-event-data-for-multiple-individuals)
		- [Get event data for a specified number of events](#get-event-data-for-a-specified-number-of-events)
		- [Get event data for a specified time period](#get-event-data-for-a-specified-time-period)
		- [Get event data with additional event-level attributes](#get-event-data-with-additional-event-level-attributes)
		- [Get event data with all of the specifications described above](#get-event-data-with-all-of-the-specifications-described-above)
	- [Displaying data using Google Maps](#displaying-data-using-google-maps)

## Introduction
Movebank's REST API allows access to pull data from [Movebank](https://www.movebank.org) using HTTP or JSON requests made in a web browser or through external programs such as R. All users of data accessed from Movebank must abide by Movebank's [general terms of use](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use) and [data policy](https://www.movebank.org/cms/movebank-content/data-policy). See Movebank's [citation guidelines](https://www.movebank.org/cms/movebank-content/citation-guidelines) for guidance on how to cite data use. Below are details, example requests, and relevant information about security and access controls.

### Understanding data from Movebank
Movebank's data model is described in the [user manual](https://www.movebank.org/cms/movebank-content/mb-data-model) and [Kranstauber et al. (2011)](https://doi.org/10.1016/j.envsoft.2010.12.005). Definitions of data attributes are provided in the [Movebank Attribute Dictionary](https://www.movebank.org/cms/movebank-content/movebank-attribute-dictionary). A machine-readable, persistent version of this vocabulary is published at http://vocab.nerc.ac.uk/collection/MVB. Use of the REST API to access data you are not already familiar with can lead to the download of data that excludes information that can be critical to understanding the data. 

The following key concepts and attributes are important to be aware of. Also read about [defining deployments and outliers](https://www.movebank.org/cms/movebank-content/deployments-and-outliers) in Movebank.

**Animal, tag, and deployment identifiers:** Movebank's data model associates each measurement (e.g. a GPS fix) with a tag, and tag measurements can be further associated with animals via deployments. Each animal, tag, and deployment has a 
- a user-defined name: the animal, tag, and deployment IDs in Movebank, also referred to as the `individual_local_identifier`, `deployment_local_identifier` or `tag_local_identifier`.
- an internal database identifier, not typically shown in Movebank: the `individual_id`, `deployment_id` and `tag_id`.
 
We do not encourage treating the internal database identifiers as a stable external reference to data, as these can change over time for various technical reasons. For example, new entities may be created and new internal identifiers assigned when
- the data owner deletes and re-creates animals, deployments, or tags. 
- the data owner uploads reference data that re-creates animals, deployments, or tags. 
- the data owner deletes and re-imports tags from live feeds.
- a data provider pushes updates to reference data that re-create animals, deployments or tags.

We advise obtaining the identifiers via the REST API using the examples below, matching the entities you are interested in by `individual_local_identifier`, `deployment_local_identifier` or `tag_local_identifier`, and then using the corresponding `individual_id`, `deployment_id` and `tag_id` where necessary.

For data owners, it is best practice to keep the `individual_local_identifier`, `deployment_local_identifier` or `tag_local_identifier` identifiers—i.e., the animal, tag and deployment IDs—stable if you want to refer to these entities from outside of Movebank.

Local identifiers are unique within but not across studies. If you are combining data from multiple studies from Movebank using the REST API, we suggest referring to entities using a combination of the local identifier and study ID or name.

**Outliers:** Event records, most commonly location estimates, can be assigned as outliers in Movebank by data owners and providers using several different tools and data attributes. The results of all outlier management steps are summarized in the [`visible`](http://vocab.nerc.ac.uk/collection/MVB/current/MVB000209/) attribute. We recommend including the `visible` attribute in event-level requests using the examples below, in order to retain this information and the ability to exclude flagged outliers from subsequent use if desired.

## Security, data access and authentication
Access to data is defined by data owners for each study in Movebank following [Movebank's permissions options](https://www.movebank.org/cms/movebank-content/permissions-and-sharing). If no username and password are provided, results will be restricted to data that owners have made publicly available. If a username and password are provided, results will be restricted to data that the user has access to. To access tracking actual data, including for visualization on external websites, the user (or the public) needs permission to download data.

For data that are made available to others, the owners of each study in Movebank specify use conditions in the "License Terms" in the [Study Details](https://www.movebank.org/cms/movebank-content/studies-page#study_details). In addition to user-specified conditions, the [General Movebank Terms of Use](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use) apply.

To ensure that users are aware of the license terms for each study, users may be required to read and accept these terms of use prior to first downloading the data for a study. Once a user has accepted the terms of use for a study, they will not be required to accept them again unless the study owner changes the terms. These requirements can cause confusion when accessing data using the API. Options for accepting license terms include
- A user can log in to Movebank and accept the license terms for the study by initiating a [data download](https://www.movebank.org/cms/movebank-content/access-data#download_data_in_movebank_format) prior to attempting to access through the API.
- Data managers can disable the requirement that users accept terms of use by unchecking the "Prompt users to accept license terms" box in the [permissions settings](https://www.movebank.org/cms/movebank-content/permissions-and-sharing#set_permissions) for the study.
- Read and accept license terms using the API, as in the following example.

### Read and accept license terms using curl
This example uses curl commands in Terminal on a Mac to accept license terms and access data from the published study [Galapagos Albatrosses](https://www.movebank.org/cms/webapp?gwt_fragment=page=studies,path=study2911040) ([Cruz et al. 2013](https://www.doi.org/10.5441/001/1.3hp3s250)).

1. Submit an http request as described below for a study and user requiring license terms be accepted, saving the terms as license_terms.txt (in html, search for "License Terms:") and specifying cookies to maintain a session in consecutive calls:
`curl -v -u username:password -c cookies.txt -o license_terms.txt "https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040"`

2. Create and print an md5sum:
`md5 -r license_terms.txt`

3. Submit an http request for the same study and user again, sending the cookie and including the md5sum (replace ### with the value from step 2):
`curl -v -u username:password -b cookies.txt -o event_data.csv "https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&license-md5=###"`

Also see an example in Python [added to this repository](https://github.com/movebank/movebank-api-doc/blob/master/mb_Meschenmoser.py).

## Accessing the database using HTTP/CSV requests
The following are examples of how to access information from the Movebank database with HTTP requests. After providing valid credentials, these calls will return CSV files containing the requested information. Note that the results will be based on the information available to the user as defined by access permissions (see above). If downloaded files have no extension and you are unable to open them, add ".csv" to the filename.

### Get a list of attribute names
`https://www.movebank.org/movebank/service/direct-read?attributes`

This will open a list of available attribute names by entity type that can be used to further specify the example queries below.

### Get descriptions of entities in the database
You may want to query general information about what is contained in Movebank. You can obtain information about the following entity types in the database prior to specifying a specific study: study, tag_type, taxon. Note that the taxonomy in Movebank comes from [the Integrated Taxonomic Information System](https://www.itis.gov/) (ITIS).

#### Get a list of sensor types
`https://www.movebank.org/movebank/service/direct-read?entity_type=tag_type`

Result

```
| description   | external_id               | id         | is_location_sensor   | name                      |
| ------------- | ------------------------- | ---------- | -------------------- | ------------------------- |
|               | bird-ring                 | 397        | TRUE                 | Bird Ring                 |
|               | gps                       | 653        | TRUE                 | GPS                       |
|               | radio-transmitter         | 673        | TRUE                 | Radio Transmitter         |
|               | argos-doppler-shift       | 82798      | TRUE                 | Argos Doppler Shift       |
|               | natural-mark              | 2365682    | TRUE                 | Natural Mark              |
|               | acceleration              | 2365683    | FALSE                | Acceleration              |
|               | solar-geolocator          | 3886361    | TRUE                 | Solar Geolocator          |
|               | accessory-measurements    | 7842954    | FALSE                | Accessory Measurements    |
|               | solar-geolocator-raw      | 9301403    | FALSE                | Solar Geolocator Raw      |
|               | barometer                 | 77740391   | FALSE                | Barometer                 |
|               | magnetometer              | 77740402   | FALSE                | Magnetometer              |
|               | orientation               | 819073350  | FALSE                | Orientation               |
|               | solar-geolocator-twilight | 914097241  | FALSE                | Solar Geolocator Twilight |
|               | acoustic-telemetry        | 1239574236 | FALSE                | Acoustic Telemetry        |
|               | gyroscope                 | 1297673380 | FALSE                | Gyroscope                 |
```

From this you can see that the sensor type ID for GPS data is 653 and that the “accessory measurements” sensor does not include location information.

#### Get a list of studies
`https://www.movebank.org/movebank/service/direct-read?entity_type=study`

Result header

`acknowledgements,citation,go_public_date,grants_used,has_quota,i_am_owner,id,is_test,license_terms,license_type,main_location_lat,main_location_long,name,number_of_deployments,number_of_individuals,number_of_tags,principal_investigator_address,principal_investigator_email,principal_investigator_name,study_objective,study_type,suspend_license_terms,i_can_see_data,there_are_data_which_i_cannot_see,i_have_download_access,i_am_collaborator,study_permission,timestamp_first_deployed_location,timestamp_last_deployed_location,number_of_deployed_locations,taxon_ids,sensor_type_ids,contact_person_name`

These results provide the study name (`study`), the study's database ID (`id`), owner-provided study details, calculated study statistics, and information about the access [permissions](https://www.movebank.org/cms/movebank-content/permissions-and-sharing) of the user credentials used for the request. Summary statistics about the studies (contained in `number_of_deployments`, `number_of_individuals`, `number_of_tags`, `timestamp_first_deployed_location`, `timestamp_last_deployed_location`, `number_of_deployed_locations`, `taxon_ids`, `sensor_type_ids`) are updated approximately once per day. To determine your access rights, filter the list using `i_am_owner`, `i_can_see_data`, `i_have_download_access`,
`i_am_collaborator`, `study_permission`, and/or `there_are_data_which_i_cannot_see`. Here 'see' refers to your rights to view tracks in [Movebank](https://www.movebank.org/cms/webapp?gwt_fragment=page=search_map) and not to download data—you will be able to view all studies you can download but not download all studies you can view. You might have permission to see only the study details, view some or all tracks but not download data, or view and download some or all data. Studies you do not have permission to see at all will not be included in the list. You can [contact data owners](https://www.movebank.org/cms/movebank-content/access-data#obtain_access_to_movebank_data) directly to propose data uses and request data sharing.

#### Get a list of studies for which a user is data manager
`https://www.movebank.org/movebank/service/direct-read?entity_type=study&i_am_owner=true`

Results will be the same as in the previous example, but filtered for only the studies for which `i_am_owner` contains `TRUE`.

### Get descriptions of entities in a study
When you have a certain study of interest, you can access information contained in that study using the study’s Movebank ID (available in [the Study Details](https://www.movebank.org/cms/movebank-content/studies-page#study_details)). You can obtain information for the following entity types: `study`, `individual`, `tag`, `deployment`, `sensor`, `study_attribute` and `event`. The event entity contains actual sensor measurements stored in study attributes, and one or more sensors can be associated with each tag. The deployment, individual, and tag entities contain descriptive information about the animals, tags, and deployments (i.e., periods over which tags are attached to animals) in the study. In Movebank we refer to the latter information as [reference data](https://www.movebank.org/cms/movebank-content/mb-data-model#reference_data). Important information about understanding these data are provided [above](#understanding-data-from-movebank).

For the examples that follow we will use the study [Galapagos Albatrosses](https://www.movebank.org/cms/webapp?gwt_fragment=page=studies,path=study2911040) (study ID 2911040; [Cruz et al. 2013](https://doi.org/10.5441/001/1.3hp3s250)) which is fully available to the public.

#### Get a description about a study
`https://www.movebank.org/movebank/service/direct-read?entity_type=study&study_id=2911040`

Result

```
|acknowledgements            |citation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |go_public_date|go_public_license_type|grants_used        |has_quota |i_am_owner |      id|is_test|license_terms |license_type | main_location_lat| main_location_long|name                  | number_of_deployments| number_of_individuals| number_of_tags|principal_investigator_address |principal_investigator_email |principal_investigator_name |study_objective                                                                                                                                                      |study_type |suspend_license_terms |i_can_see_data |there_are_data_which_i_cannot_see |i_have_download_access|i_am_collaborator|study_permission| timestamp_first_deployed_location| timestamp_last_deployed_location| number_of_deployed_locations|taxon_ids            |sensor_type_ids |contact_person_name      |
|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------:|---------------------:|:------------------|:---------|:----------|-------:|:------|:-------------|:------------|-----------------:|------------------:|:---------------------|---------------------:|---------------------:|--------------:|:------------------------------|:----------------------------|:---------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------|:---------------------|:--------------|:---------------------------------|:---------------------|:----------------|:---------------|---------------------------------:|--------------------------------:|----------------------------:|:--------------------|:---------------|:------------------------|
|Thanks for help: ECCD, GNPS |Cruz S, Proaño CB, Anderson D, Huyvaert K, Wikelski M. 2013. Data from: The Environmental-Data Automated Track Annotation (Env-DATA) System: Linking animal tracks with environmental data. Movebank Data Repository. <a href=""https://www.doi.org/10.5441/001/1.3hp3s250"" target=""_blank"">https://www.doi.org/10.5441/001/1.3hp3s250</a><br><br>Dodge S, Bohrer G, Weinzierl R, Davidson SC, Kays R, Douglas D, Cruz S, Han J, Brandes D, Wikelski M. 2013. The Environmental-Data Automated Track Annotation (Env-DATA) System—linking animal tracks with environmental data. Movement Ecology 1:3. https://doi.org/10.1186/2051-3933-1-3 |              |                      |NSF and Max Planck |true      |false      | 2911040|false  |              |CC_0         |             -1.39|             -89.62|Galapagos Albatrosses |                    28|                    28|             28|                               |                             |                            |Tracking of Galapagos albatrosses for conservation and basic science. Waved albatrosses were tracked during breeding and non-breeding periods between 2008 and 2010. |research   |true                  |true           |false                             |true                  |false            |na              |           2008-05-31 13:29:31.998|          2008-11-06 18:00:55.998|                        16028|Phoebastria irrorata |GPS,Acceleration|sebas (Sebastian M. Cruz)|
```

#### Get information about tags in a study
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
...
```

#### Get information about animals in a study
`https://www.movebank.org/movebank/service/direct-read?entity_type=individual&study_id=2911040`

Result

```
|comments        |death_comments |earliest_date_born |exact_date_of_birth |      id|latest_date_born |local_identifier |nick_name |ring_id |sex |taxon_canonical_name |        timestamp_start|          timestamp_end| number_of_events| number_of_deployments|sensor_type_ids |taxon_detail |
|:---------------|:--------------|:------------------|:-------------------|-------:|:----------------|:----------------|:---------|:-------|:---|:--------------------|----------------------:|----------------------:|----------------:|---------------------:|:---------------|:------------|
|                |               |                   |                    | 2911059|                 |4264-84830852    |          |        |    |Phoebastria irrorata |2008-06-23 16:28:31.999|2008-06-26 13:30:43.001|               48|                     1|GPS,Acceleration|             |
|Nest stage: egg |               |                   |                    | 2911066|                 |2131-2131        |          |        |    |Phoebastria irrorata |2008-06-23 17:58:02.998|2008-07-11 10:32:29.001|              182|                     1|GPS,Acceleration|             |
|Nest stage: egg |               |                   |                    | 2911075|                 |2368-2368        |          |        |    |Phoebastria irrorata |2008-06-23 17:58:01.998|2008-09-28 13:31:13.999|             1503|                     1|GPS,Acceleration|             |
|Nest stage: egg |               |                   |                    | 2911074|                 |3275-30662       |          |        |    |Phoebastria irrorata |2008-06-23 19:28:30.999|2008-08-03 10:30:43.998|              647|                     1|GPS,Acceleration|             |
|Nest stage: egg |               |                   |                    | 2911078|                 |3606-30668       |          |        |    |Phoebastria irrorata |2008-06-23 17:57:56.998|2008-06-25 15:00:14.000|               32|                     1|GPS,Acceleration|             |
...
```		

#### Get information about deployments in a study

`https://www.movebank.org/movebank/service/direct-read?entity_type=deployment&study_id=2911040`

Result

```
|alt_project_id |animal_life_stage |animal_mass |animal_reproductive_condition |attachment_type |behavior_according_to |comments                               |data_processing_software |deploy_off_latitude |deploy_off_longitude |deploy_off_person |deploy_off_timestamp | deploy_on_latitude| deploy_on_longitude|deploy_on_person |     deploy_on_timestamp|deployment_end_comments |deployment_end_type |duty_cycle                              |geolocator_calibration |geolocator_light_threshold |geolocator_sensor_comments |geolocator_sun_elevation_angle |habitat_according_to |      id|local_identifier |location_accuracy_comments |manipulation_comments |manipulation_type |partial_identifier |study_site     |tag_readout_method |
|:--------------|:-----------------|:-----------|:-----------------------------|:---------------|:---------------------|:--------------------------------------|:------------------------|:-------------------|:--------------------|:-----------------|:--------------------|------------------:|-------------------:|:----------------|-----------------------:|:-----------------------|:-------------------|:---------------------------------------|:----------------------|:--------------------------|:--------------------------|:------------------------------|:--------------------|-------:|:----------------|:--------------------------|:---------------------|:-----------------|:------------------|:--------------|:------------------|
|               |adult             |            |                              |tape            |                      |not used in analysis                   |                         |                    |                     |                  |                     |              -1.39|              -89.62|                 | 2008-06-23 06:00:00.000|                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 9472204|                 |                           |                      |none              |                   |Punta Cevallos |other-wireless     |
|               |adult             |            |                              |tape            |                      |not used in analysis                   |                         |                    |                     |                  |                     |              -1.39|              -89.62|                 | 2008-06-23 06:00:00.000|                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 9472205|                 |                           |                      |none              |                   |Punta Cevallos |other-wireless     |
|               |adult             |            |                              |tape            |                      |not used in analysis                   |                         |                    |                     |                  |                     |              -1.38|              -89.75|                 | 2008-05-31 06:00:00.000|                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 9472206|                 |                           |                      |none              |                   |Punta Suarez   |other-wireless     |
|               |adult             |            |                              |tape            |                      |used in analysis                       |                         |                    |                     |                  |                     |              -1.38|              -89.75|                 | 2008-05-31 06:00:00.000|                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 9472207|                 |                           |                      |none              |                   |Punta Suarez   |other-wireless     |
|               |adult             |            |                              |tape            |                      |used in analysis and shown in Figs 7-8 |                         |                    |                     |                  |                     |              -1.39|              -89.62|                 | 2008-06-23 06:00:00.000|                        |                    |GPS locations recorded every 90 minutes |                       |                           |                           |                               |                     | 9472208|                 |                           |                      |none              |                   |Punta Cevallos |other-wireless     |
...
```

#### Get information about tag sensors in a study
`https://www.movebank.org/movebank/service/direct-read?entity_type=sensor&tag_study_id=2911040`

Result

```
|      id| sensor_type_id|  tag_id|
|-------:|--------------:|-------:|
| 2911205|            653| 2911112|
| 2911206|            653| 2911125|
| 2911207|            653| 2911109|
| 2911208|            653| 2911113|
| 2911209|            653| 2911131|
...
```

Tags can contain event data for more than one sensor type. Here you can see what sensor data are provided by each tag. Keep in mind that in Movebank, all attribute values for each imported event record (i.e., a row containing a timestamp in the original data file) are assigned to one sensor type. In some cases measurements for multiple sensors are contained in one line, in which case all of those measurements will be associated with the primary sensor as chosen by the user. For example, GPS units commonly provide tabular data that include a temperature measurement in the same line of data with each GPS fix. In this case both the temperature and location coordinates will have the sensor type GPS (sensor_type_id 653). To more thoroughly evaluate what kinds sensor information are contained in a study, you'll want to see what event data attributes are present.

#### Get study attributes for a sensor in a study
`https://www.movebank.org/movebank/service/direct-read?entity_type=study_attribute&study_id=2911040&sensor_type_id=653`

Result

```
| study_id| sensor_type_id|short_name                          |data_type  |
|--------:|--------------:|:-----------------------------------|:----------|
|  2911040|            653|"eobs_battery_voltage"              |"integer"  |
|  2911040|            653|"eobs_fix_battery_voltage"          |"integer"  |
|  2911040|            653|"eobs_horizontal_accuracy_estimate" |"decimal"  |
|  2911040|            653|"eobs_key_bin_checksum"             |"integer"  |
|  2911040|            653|"eobs_speed_accuracy_estimate"      |"decimal"  |
|  2911040|            653|"eobs_start_timestamp"              |"datetime" |
|  2911040|            653|"eobs_status"                       |"string"   |
|  2911040|            653|"eobs_temperature"                  |"integer"  |
|  2911040|            653|"eobs_type_of_fix"                  |"integer"  |
|  2911040|            653|"eobs_used_time_to_get_fix"         |"integer"  |
|  2911040|            653|"ground_speed"                      |"decimal"  |
|  2911040|            653|"heading"                           |"decimal"  |
|  2911040|            653|"height_above_ellipsoid"            |"decimal"  |
|  2911040|            653|"location_lat"                      |"decimal"  |
|  2911040|            653|"location_long"                     |"decimal"  |
|  2911040|            653|"timestamp"                         |"datetime" |
|  2911040|            653|"update_ts"                         |"datetime" |
|  2911040|            653|"visible"                           |"boolean"  |
```

These are the event-level attributes associated with the sensor in this study. This information can help you evaluate whether a study might be relevant to a given research question, or which event attributes to include in requests for event data.

### Get event data from a study
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
...
```

By default, requests for event data return the event-level dataset (the “tracking data” for location sensors) limited to the variables timestamp, location_lat, location_long, individual_id, and tag_id. This default request **does not include**
- Local identifiers specified by the data owner; 
- The "visible" attribute, which is used to identify records that have been flagged as outliers; 
- Additional data attributes often contained within the study, including for sensors that do not contain location coordinates (e.g. geolocators and accelerometers). 

We recommend including individual_local_identifier, tag_local_identifier, and visible in event-level requests, as shown in the following examples, to include identifiers and outlier flags as managed by the data owner. Read more about [understanding data from Movebank](#understanding-data-from-movebank) above.

#### Get event data with all event-level attributes
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&attributes=all`

Result

```
|individual_id|deployment_id| tag_id|study_id|sensor_type_id|individual_local_identifier|tag_local_identifier|individual_taxon_canonical_name|eobs_battery_voltage|eobs_fix_battery_voltage|eobs_horizontal_accuracy_estimate|eobs_key_bin_checksum|eobs_speed_accuracy_estimate|eobs_start_timestamp   |eobs_status|eobs_temperature|eobs_type_of_fix|eobs_used_time_to_get_fix|ground_speed|heading|height_above_ellipsoid|location_lat|location_long|timestamp              |visible|event_id|
|------------:|------------:|------:|-------:|-------------:|:--------------------------|:-------------------|:------------------------------|-------------------:|-----------------------:|--------------------------------:|--------------------:|---------------------------:|:----------------------|:----------|---------------:|---------------:|------------------------:|-----------:|------:|---------------------:|-----------:|------------:|:----------------------|:------|-------:|
|      2911059|      9472219|2911107| 2911040|           653|"4264-84830852"            |"131"               |           Phoebastria irrorata|                3686|                    3437|                            12.03|           2396171168|                        0.67|2008-05-31 13:28:48.000|"A"        |              12|               3|                       74|        0.01|  21.63|                  16.5|   -1.372641|   -89.740214|2008-05-31 13:30:02.001|true   |28192174|
|      2911059|      9472219|2911107| 2911040|           653|"4264-84830852"            |"131"               |           Phoebastria irrorata|                3701|                    3452|                             2.82|           2700991056|                        0.24|2008-05-31 14:59:59.000|"A"        |              19|               3|                       45|         0.0|  95.68|                  12.6|  -1.3728941|  -89.7401542|2008-05-31 15:00:44.998|true   |28192175|
|      2911059|      9472219|2911107| 2911040|           653|"4264-84830852"            |"131"               |           Phoebastria irrorata|                3701|                    3482|                             4.35|            540734184|                        2.57|2008-05-31 16:30:00.000|"A"        |              24|               3|                       39|        0.11|  13.76|                  17.4|  -1.3728809|  -89.7401401|2008-05-31 16:30:39.998|true   |28192176|
|      2911059|      9472219|2911107| 2911040|           653|"4264-84830852"            |"131"               |           Phoebastria irrorata|                3691|                    3476|                             2.82|           2845350485|                        2.61|2008-05-31 18:00:00.000|"A"        |              18|               3|                       49|         0.2|   9.83|                  24.8|  -1.3728911|  -89.7401596|2008-05-31 18:00:49.998|true   |28192177|
|      2911059|      9472219|2911107| 2911040|           653|"4264-84830852"            |"131"               |           Phoebastria irrorata|                3691|                    3541|                             4.61|           1429925913|                         2.7|2008-05-31 19:30:00.000|"A"        |              22|               3|                       18|        0.24|  37.36|                  19.0|  -1.3729121|   -89.740127|2008-05-31 19:30:18.998|true   |28192178|
...
```

This could provide more information (and data volume) than necessary, so it is also possible to specify which attributes to include and in what order. The following example is a good minimum default set for location events. See “get a list of attribute names” above for available attributes. Note that filtering for some attributes may not work. Please contact support@movebank.org if you find an attribute that is not included in results.

#### Get event data with select additional event-level attributes
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&attributes=individual_local_identifier,tag_local_identifier,timestamp,location_long,location_lat,visible,individual_taxon_canonical_name`

Result

```
|individual_local_identifier |tag_local_identifier |timestamp               | location_long| location_lat|visible |individual_taxon_canonical_name |
|:---------------------------|:--------------------|:-----------------------|-------------:|------------:|:-------|:-------------------------------|
|"4264-84830852"             |"131"                |2008-05-31 13:30:02.001 |     -89.74021|    -1.372641|true    |Phoebastria irrorata            |
|"4264-84830852"             |"131"                |2008-05-31 15:00:44.998 |     -89.74015|    -1.372894|true    |Phoebastria irrorata            |
|"4264-84830852"             |"131"                |2008-05-31 16:30:39.998 |     -89.74014|    -1.372881|true    |Phoebastria irrorata            |
|"4264-84830852"             |"131"                |2008-05-31 18:00:49.998 |     -89.74016|    -1.372891|true    |Phoebastria irrorata            |
|"4264-84830852"             |"131"                |2008-05-31 19:30:18.998 |     -89.74013|    -1.372912|true    |Phoebastria irrorata            |
...
```

#### Get event data for a single sensor type
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
...
```

If multiple sensor types are used in a study, use this to access event-level data for a specific sensor. See “get a list of sensor types” above for the `sensor_type_id` for each sensor type.

#### Get event data for an individual animal
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&individual_local_identifier=4264-84830852`

Result

```
|timestamp               |  location_lat|   location_long| individual_id|  tag_id|
|:-----------------------|-------------:|---------------:|-------------:|-------:|
|2008-05-31 13:30:02.001 |     -1.372641|      -89.740214|       2911059| 2911107|
|2008-05-31 15:00:44.998 |    -1.3728941|     -89.7401542|       2911059| 2911107|
|2008-05-31 16:30:39.998 |    -1.3728809|     -89.7401401|       2911059| 2911107|
|2008-05-31 18:00:49.998 |    -1.3728911|     -89.7401596|       2911059| 2911107|
|2008-05-31 19:30:18.998 |    -1.3729121|      -89.740127|       2911059| 2911107|
...
```  

#### Get event data for a specified time period
`https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id=2911040&timestamp_start=20080604133045000&timestamp_end=20080604133046000`

Result

```
|timestamp               | location_lat| location_long| individual_id|  tag_id|
|:-----------------------|------------:|-------------:|-------------:|-------:|
|2008-06-04 13:30:45.999 |   -1.9960011|   -85.1520954|       2911059| 2911107|
|2008-06-04 13:30:45.000 |    -1.372639|   -89.7404519|       2911060| 2911109|
|2008-06-04 13:30:45.998 |   -5.8555544|   -81.2025874|       2911064| 2911131|
|2008-06-04 13:30:45.001 |   -1.3729218|   -89.7402634|       2911065| 2911134|
|2008-06-04 13:30:45.000 |             |              |       2911059| 2911107|
|2008-06-04 13:30:45.000 |             |              |       2911060| 2911109|
|2008-06-04 13:30:45.000 |             |              |       2911064| 2911131|
|2008-06-04 13:30:45.000 |             |              |       2911065| 2911134|
...
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
The HTTP/CSV requests can be used to access Movebank data from R. [The R package `move`](http://cran.r-project.org/web/packages/move/index.html) provides flexible options for browsing and visualizing data from Movebank in R using the REST API. In addition, [the package source files](https://r-forge.r-project.org/scm/viewvc.php/pkg/move/R/WebImport.R?view=markup&root=move) provide information that can be used to access Movebank from R without the package.

## Accessing the database using JSON/JavaScript requests
The following are examples for how to access Movebank data using JSON requests. This is currently designed primarily to allow tracking data to be displayed on external maps using the Google Maps API (see below). You will need the relevant study ID number and sensor type description in the database to access data (see above).

### Get public or private data
In the examples below, we use URLs that do not include usernames or passwords. In order to access data from a study without providing login information, the study must be completely accessible to the public as described above. Consider [making data publicly available](https://www.movebank.org/cms/movebank-content/permissions-and-sharing#examples) so that data can be accessed without providing any login information. Remember that making data available does not give others permission to use your data, and that terms of use still apply as described [above](#introduction). If data are public, the http request should begin with `https://www.movebank.org/movebank/service/public/json?`, for example

`https://www.movebank.org/movebank/service/public/json?&study_id=2911040&individual_local_identifiers=4262-84830876&max_events_per_individual=5&sensor_type=gps`

If data are not public, the http request should begin with `https://www.movebank.org/movebank/service/json-auth?`, for example

`https://www.movebank.org/movebank/service/json-auth?&study_id=2911040&individual_local_identifiers=4262-84830876&max_events_per_individual=5&sensor_type=gps`

The browser will prompt you to provide your Movebank credentials before proceeding with the request. Alternatively, you can provide user credentials using PHP that can be stored on your local server. For example,

```php
<?php
$url='https://www.movebank.org/movebank/service/json-auth?study_id=16880941&individual_local_identifiers=Mary&individual_local_identifiers=Butterball&individual_local_identifiers=Schaumboch&max_events_per_individual=2000&sensor_type=gps';

$user=‘username’;
$password=‘password’;

$context = stream_context_create(array(
    'http' => array(
        'header'  => "Authorization: Basic " . base64_encode("$user:$password")
    )
));
```

For non-public data, use the example above to modify your requests that use the examples below.

### Get event data from the study
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&sensor_type=gps`

Result

```
{"individuals":[{"study_id":2911040,"individual_local_identifier":"1094-1094","individual_taxon_canonical_name":"Phoebastria irrorata","sensor_type_id":653,"sensor_id":2911314,"individual_id":2911080,"locations":[
{"timestamp":1214238511999,"location_long":-89.6210002,"location_lat":-1.3895437},
{"timestamp":1214238608998,"location_long":-89.6210024,"location_lat":-1.3895456},
{"timestamp":1214244055998,"location_long":-89.6209386,"location_lat":-1.3895534},
{"timestamp":1214249444001,"location_long":-89.6209727,"location_lat":-1.38957},
{"timestamp":1214254820001,"location_long":-89.6210144,"location_lat":-1.38957}
...
```

This example contains the minimum information needed to obtain data: a study ID, the animal ID defined by the data owner, and a sensor type. You can make several additional variations to this, described below. The timestamps are provided in milliseconds since `1970-01-01 UTC`, and coordinates are in WGS84.

#### Get event data for multiple individuals
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&individual_local_identifiers=1163-1163&individual_local_identifiers=2131-2131&sensor_type=gps`

Results will be in the same format as in the previous example, with a header like the first line in the previous example added before the first row of data for each individual. 

#### Get event data for a specified number of events
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&max_events_per_individual=10&sensor_type=gps`

Results will be in the same format, but will be restricted to the most recent 10 records per individual. This can be used to reduce the page loading time.

#### Get event data for a specified time period
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&timestamp_start=1213358400000&timestamp_end=1213617600000&sensor_type=gps`

Results will be in the same format, but will be restricted to events within the specified time range. This can be used to highlight (or exclude) a certain portion of a track or to reduce the page loading time. The timestamps must be provided in milliseconds since 1970-01-01 (converters are available online). All dates in Movebank are stored in UTC. Here we obtain locations collected between `2008-6-13 12:00` and `2008-6-16 12:00`.

#### Get event data with additional event-level attributes
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&sensor_type=gps&attributes=timestamp,location_long,location_lat,ground_speed,heading`

Result

```
{"individuals":[{"study_id":2911040,"individual_local_identifier":"1094-1094","individual_taxon_canonical_name":"Phoebastria irrorata","sensor_type_id":653,"sensor_id":2911314,"individual_id":2911080,"locations":[
{"timestamp":1214238511999,"location_long":-89.6210002,"location_lat":-1.3895437,"ground_speed":0,"heading":17.04},
{"timestamp":1214238608998,"location_long":-89.6210024,"location_lat":-1.3895456,"ground_speed":0.83,"heading":351.93},
{"timestamp":1214244055998,"location_long":-89.6209386,"location_lat":-1.3895534,"ground_speed":0.14,"heading":339.48},
{"timestamp":1214249444001,"location_long":-89.6209727,"location_lat":-1.38957,"ground_speed":0.28,"heading":99.61},
{"timestamp":1214254820001,"location_long":-89.6210144,"location_lat":-1.38957,"ground_speed":0.29,"heading":19.66}
...
```

Results will include additional specified attributes if they are available in the dataset. To evaluate which attributes are available, see [Get study attributes for a sensor in a study](#get-study-attributes-for-a-sensor-in-a-study).

#### Get event data with all of the specifications described above
`https://www.movebank.org/movebank/service/public/json?study_id=2911040&individual_local_identifiers=4262-84830876&individual_local_identifiers=1163-1163&individual_local_identifiers=2131-2131&max_events_per_individual=10&timestamp_start=1213358400000&timestamp_end=1213617600000&sensor_type=gps&attributes=timestamp,location_long,location_lat,ground_speed,heading`

These results will combine specifications for individuals, a number of events and time period per individual, and event attributes. As shown here, the specifications provided in the examples can be combined to further define what you want to access. The following is a template summarizing everything we've just described.

`https://www.movebank.org/movebank/service/public/json?study_id=<study id>&individual_local_identifiers=<animal ID 1>&individual_local_identifiers=<animal ID 2 (optional)>&max_events_per_individual=<maximum number of records to access (optional)>&timestamp_start=<timestamp in milliseconds since 1/1/1970 (optional)>&timestamp_end=<timestamp in milliseconds since 1/1/1970 (optional)>&sensor_type=<sensor type>&attributes=<attributes to display in results (optional)>`

### Displaying data using Google Maps
The JSON/JavaScript requests were designed primarily to allow users to access and display mapped Movebank data on external web pages using the Google Maps API. See [Movebank Map Demo](https://github.com/movebank/movebank-map-demo) for example code for maps that pull data from Movebank with JSON requests as described above.
