---
url: https://admin.sentera.com/api/docs/mutation/create_survey/
kind: mutation
title: create_survey
description: Create a survey for a field.
parent: null
children: []
tags: ['surveys', 'core']
last_fetched: '2026-05-31T14:18:10Z'
---

# create_survey

**Description:** Create a survey for a field.

## Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `end_time` | `ISO8601DateTime!` | Yes | The capture time of the most recent image in the survey. |
| `field_sentera_id` | `ID!` | Yes | The ID of the Field this Shape is connected to. |
| `light_sensor_condition` | `LightSensorCondition` | No | The condition of the light sensor. |
| `notes` | `String` | No | Notes for this survey. |
| `start_time` | `ISO8601DateTime!` | Yes | The capture time of the oldest image in the survey. |

## Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `action` | `UpsertActionType!` | Determines if it was a create or update. |
| `color` | `String!` | The color that can be used when rendering things like photo dots for this survey. Format is #RRGGBB. |
| `content_hash` | `String!` | The current content hash for this item. |
| `created_at` | `ISO8601DateTime!` | The timestamp of when the item was created in the system. |
| `created_by` | `User!` | The user who created this item. |
| `end_time` | `String!` | Timestamp of when the survey was completed.  This attribute can be used as the date_attribute_name in a date_range query. |
| `feature_sets` | `FeatureSetsQueryResult!` | A list of feature sets associated with this survey. |

**feature_sets arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `order_by` | `FeatureSetSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |
| `type` | `FeatureSetType` | Filter the results by feature set type. |

| `field` | `Field!` | the associated field of this survey. |
| `files` | `FilesQueryResult!` | A list of files associated with this survey. |

**files arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `date_range` | `DateRange` | Filter the results by a date range. |
| `order_by` | `FileSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |

| `image_upload_ended_at` | `ISO8601DateTime` | The time after which the last source image uploaded and processing was
requested. If uploaded multiple times, the time the last upload ended. For
surveys that lack source imagery this will be null. |
| `image_upload_started_at` | `ISO8601DateTime` | The time at which the first source image was uploaded. If uploaded multiple
times - the time the last upload started. For surveys that lack source imagery
this will be null. |
| `images` | `ImagesQueryResult!` | A list of images associated with this survey. |

**images arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `bounds` | `Bounds` | Filter the results using a bounding box. |
| `calculated_index` | `CalculatedIndex` | An index such as NDVI or NDRE calculated for this image. |
| `color_applied` | `ColorApplied` | The color application (if present) for this image. |
| `date_range` | `DateRange` | Filter the results using a date range. |
| `haversine_radius` | `HaversineRadius` | Filter the results using a haversine radius. |
| `order_by` | `ImageSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |
| `sensor_type` | `SensorType` | The type of sensor captured the image. |

| `light_sensor_condition` | `LightSensorCondition!` | The lighting condition detected by the sensor |
| `message` | `String` | A message returned for surveys that have failed during processing. |
| `mosaics` | `MosaicsQueryResult!` | A list of mosaics associated with this survey. |

**mosaics arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `mosaic_type` | `MosaicType` | Filter the results by mosaic type. |
| `order_by` | `MosaicSortingAttributes` | Order the results by a specific attribute. |
| `order_by_direction` | `SortDirection` | Direction (ascending or descending) of the ordered results. |
| `pagination` | `Pagination` | Paginate the results. |
| `quality` | `MosaicQuality` | Filter the results by mosaic quality. |

| `name` | `String!` | Name of the survey. |
| `notes` | `String` | Notes pertaining to this survey. |
| `organization` | `Organization!` | The associated organization. |
| `owner_type` | `FeatureSetOwnerType!` | Type of the feature set owner |
| `sentera_id` | `ID!` | A system-generated key identifying a specific instance of a survey. |
| `start_time` | `String!` | Timestamp when the survey was started. This attribute can be used as the date_attribute_name in a date_range query. |
| `status` | `SurveyStatus!` | The status of the survey. |
| `updated_at` | `ISO8601DateTime!` | The timestamp of when the item was last updated in the system. |
| `updated_by` | `User` | The user who last updated this item. |

## Examples

```graphql
mutation CreateSurvey {
  create_survey(
  field_sentera_id: "o2miljd_AS_phgrAcme_CV_stag_bae9392_200206_223021"
  start_time: "2025-12-18T00:00:00z"
  end_time: "2025-12-18T00:02:00z"
  ) {
  sentera_id
  start_time
  end_time
  }
}
```

```graphql
{
  "data": {
  "create_survey": {
    "sentera_id": "h7mnsa4_CO_phgrAcme_CV_stag_bae9392_200206_223021",
    "start_time": "2025-12-18T00:00:00z",
    "end_time": "2025-12-18T00:02:00z"
  }
  }
}
```


---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
