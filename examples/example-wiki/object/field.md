---
url: https://admin.sentera.com/api/docs/object/field/
kind: object
title: Field
description: ''
parent: null
children: []
tags: ['fields', 'flight-planning', 'core']
last_fetched: '2026-05-31T14:18:05Z'
---

# Field

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `acres` | `Float!` | **Deprecated:** Support added for retrieving area in metric units. Please use area instead. The acres of the boundary of the field. |
| `action` | `UpsertActionType!` | Determines if it was a create or update. |
| `active` | `Boolean!` | Indicator of whether or not this field is currently active. |
| `address` | `String` | Field address. |
| `alerts` | `AlertsQueryResult!` | A list of alerts associated with this field. |

**alerts arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `apply_user_preferences_filter` | `Boolean` | Filter the alerts according to a user's notification delivery preferences. |
| `pagination` | `Pagination` | Paginate the results. |
| `status` | `AlertStatusType` | Filter the alerts by status. |

| `area` | `Area!` | The area of the boundary of the field in the specified unit system. |

**area arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `unit` | `AreaUnitType` | The unit in which a client would like the area. |
| `unit_system` | `UnitSystem` | The unit system in which a client would like the area. Defaults to IMPERIAL if not provided. |

| `bbox` | `[Float!]!` | A simple (w, s, e, n) box that represents the extreme coordinates of the field's boundary. |
| `boundary` | `GeoJSON!` | A GeoJson FeatureCollection that includes a MultiPolygon representing the field boundary. |
| `city` | `String` | Field city. |
| `content_hash` | `String!` | The current content hash for this item. |
| `country_code` | `String` | Field country code (ISO 3166-1). |
| `county` | `String` | Field county. |
| `created_at` | `ISO8601DateTime!` | The timestamp of when the item was created in the system. |
| `created_by` | `User!` | The user who created this item. |
| `crop_season_years` | `[Int!]!` | The years that crop seasons were planted on this field. |
| `crop_seasons` | `[CropSeason!]!` | A list of crop seasons associated with this field. |

**crop_seasons arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `active` | `Boolean` | Limit crop seasons based on if they are active or not. |
| `crop_type` | `CropType` | Limit crop seasons by crop type. |

| `distance_from_origin` | `Float` | The distance in miles from an origin geo-position of this field. Only
available when using the haversine radius query input; null otherwise. |
| `external_connection` | `ExternalCredential` | **Deprecated:** Please use the external_id and external_partner fields. The external connection that this field is linked to. |
| `external_id` | `String` | The id of the field in the external partner's system. |
| `external_partner` | `ExternalPartner` | The external partner the field was imported from. |
| `farm` | `String` | Field farm name |
| `feature_sets` | `FeatureSetsQueryResult!` | A list of feature sets for this field. |

**feature_sets arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `order_by` | `FeatureSetSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |
| `type` | `FeatureSetType` | Filter the results by feature set type. |

| `field_boundary` | `[GeoPosition]!` | **Deprecated:** Please use the boundary GeoJSON field. A closed collection of geo-positions representing the field boundary. |
| `files` | `FilesQueryResult!` | A list of files associated with this field. |

**files arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `date_range` | `DateRange` | Filter the results by a date range. |
| `order_by` | `FileSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |

| `grower` | `String` | Field grower name. |
| `latitude` | `Float!` | The latitude value for the center of the field. |
| `longitude` | `Float!` | The longitude value for the center of the field. |
| `name` | `String!` | Field name. |
| `organization` | `Organization!` | The organization associated with this field. |
| `owner_type` | `FeatureSetOwnerType!` | Type of the feature set owner |
| `sentera_id` | `ID!` | ID of the feature set owner |
| `shapes` | `ShapesQueryResult!` | A list of shapes associated with this field. |

**shapes arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `date_range` | `DateRange` | Filter the results by date range |
| `order_by` | `ShapeSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |

| `shared` | `Boolean!` | Indicates if this field has been shared from another account. |
| `state` | `String` | Field state/province/region code (ISO 3166-2). |
| `surveys` | `SurveysQueryResult!` | A list of surveys associated with this field.. |

**surveys arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `date_range` | `DateRange` | Filter the results by date range. |
| `order_by` | `SurveySortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `organization_sentera_id` | `ID` | List surveys for this organization. |
| `pagination` | `Pagination` | Paginate the results. |

| `tasks` | `TasksQueryResult!` | A list of tasks associated with this field. |

**tasks arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `assigned_to` | `ID` | Filter tasks by the "assigned to" user. Specify null to retrieve unassigned tasks. |
| `created_by` | `ID` | Filter tasks by the user that created them. Can be used to list tasks you created. |
| `pagination` | `Pagination!` | Paginate the results. |
| `status` | `TaskStatus` | Filter tasks by status. |
| `statuses` | `[TaskStatus!]` | Filter tasks by one or more statuses. |
| `task_type` | `TaskType` | Filter tasks by their type. |

| `time_zone` | `String!` | The time zone of the field. Zone names are from the "TZ database name" column
from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List. |
| `updated_at` | `ISO8601DateTime!` | The timestamp of when the item was last updated in the system. |
| `updated_by` | `User` | The user who last updated this item. |
| `years_planted` | `[Int!]!` | The years that this field was planted. |
| `zip_code` | `String` | Field zip code. |

## Examples

```graphql
query FieldBySenteraID{
  field(sentera_id: "zx0tsts_AS_SHORT1_CV_test_1ba88e5_170907_220547") {
  sentera_id
  name
  latitude
  longitude
  }
}
```

```graphql
{
  "data": {
  "field": {
    "sentera_id": "zx0tsts_AS_SHORT1_CV_test_1ba88e5_170907_220547",
    "name": "Field 5524",
    "latitude": 45.0,
    "longitude": -93.4
  }
  }
}
```

```graphql
query FieldBySenteraIDWithSurveysAndFiles{
  field(sentera_id: "zx0tsts_AS_SHORT1_CV_test_1ba88e5_170907_220547") {
  sentera_id
  name
  latitude
  longitude
  files(pagination: {page_size: 10, page: 1}, order_by: FILENAME, order_by_direction: ASCENDING) {
    total_count
    page
    page_size
    results {
      sentera_id
    }
  }
  surveys(pagination: {page_size: 10, page: 1}, order_by: START_TIME, order_by_direction: DESCENDING) {
    total_count
    page
    page_size
    results {
      sentera_id
      start_time
      end_time
    }
  }
  }
}
```

```graphql
{
  "data": {
  "field": {
    "sentera_id": "zx0tsts_AS_SHORT1_CV_test_1ba88e5_170907_220547",
    "name": "Field 5524",
    "latitude": 45.0,
    "longitude": -93.4,
    "files": {
      "total_count": 467,
      "page": 1,
      "page_size": 10,
      "results": [
        {
          "sentera_id": "itqkn28_FI_SHORT1_CV_test_dc0d87d_170907_235328"
        }
      ]
    },
    "surveys": {
      "total_count": 4,
      "page": 1,
      "page_size": 10,
      "results": [
        {
          "sentera_id": "itqkn28_CO_SHORT1_CV_test_dc0d87d_170907_235328",
          "start_time": "2017-09-03T16:25:32Z",
          "end_time": "2017-09-03T16:45:32Z"
        }
      ]
    }
  }
  }
}
```


---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
