# Movebank REST API
See [movebank-api](https://github.com/movebank/movebank-api-doc/blob/master/movebank-api.md) for a description of the download interface to build calls to the Movebank database using HTTP/CSV or JSON/JavaScript requests. [Movebank](https://www.movebank.org/node/2) is a free, online database and research platform for animal tracking and other on-animal sensor data hosted by the Max Planck Institute for Animal Behavior that helps animal tracking researchers manage, share, protect, analyze and archive their data. For working in R be sure to check out the [move2 package](http://cran.r-project.org/web/packages/move2/index.html).

## Getting started
If you are not already familiar with Movebank, we recommend spending some time with the [Tracking Data Map](https://www.movebank.org/panel_embedded_movebank_webapp) to better understand how data are organized, viewed and accessed there. If you want to compile existing studies for analysis, check out our [Collaborations using Movebank](https://www.movebank.org/node/30029) page for tips.

Data in Movebank are stored in user-created studies and used during all stages of research. This means that studies have varying levels of completeness—e.g. deployment periods and species names might or might not be defined, outliers might or might not be flagged. Because studies are treated independently, animal and tag identifiers can be assumed to be unique within a study but not across studies. The [Movebank Data Repository](https://www.movebank.org/node/15294) comprises a subset of Movebank studies that are curated and publicly archived. Data access and use are subject to Movebank's [user agreement](https://www.movebank.org/cms/movebank-content/data-policy#user_agreement) and [general terms of use](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use).

## Acknowledgements
[Schäuffelhut Berger Software Engineering](https://www.schaeuffelhut-berger.de)

Thank you to [Xianghui Dong](https://github.com/xhdong-umd) for converting this document to markdown!
