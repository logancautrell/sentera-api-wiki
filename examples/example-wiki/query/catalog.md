---
url: https://admin.sentera.com/api/docs/query/catalog/
kind: query
title: catalog
description: Retrieve a list of all Sentera's FieldInsights products.
parent: null
children: []
tags: ['core', 'products', 'catalog']
last_fetched: '2026-05-31T14:18:03Z'
---

# catalog

**Description:** Retrieve a list of all Sentera's FieldInsights products.

## Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `products` | `[Product!]!` | The list of products. |
| `version` | `String!` | The version of the product catalog represented by this query result. |

## Examples

```graphql
query ProductCatalog {
  catalog {
  products {
    name
    sku
    key
    description
    url
    settings_keys
    category
    group
    variants {
      name
      key
    }
    flight_specifications {
      key
      specs {
        speed {
          miles_per_hour
          meters_per_second
        }
        heading
        flight_direction
        buffer {
          feet
          meters
        }
        gimbal_pitch_degrees
        overlap_percentage
        terrain_informed
      }
    }
  }
  }
}
```

```graphql
{
  "data": {
  "catalog": {
    "products": [
      {
        "name": "Agronomic Advisor Stand Count",
        "sku": "71101-00",
        "key": "ADVISOR_STAND",
        "description": "Agronomic Advisor Stand Count provides plant population count and emergence percentage across a field. This product utilizes high-resolution RGB imagery captured at sampled locations across a field to deliver a Spot Scout layer. Specific deliverables for this product are crop dependent.",
        "url": "https://catalog.sentera.com/products/advisor_stand",
        "settings_keys": [
          "row_fill",
          "crop_type",
          "seeding_rate",
          "row_spacing"
        ],
        "category": "ADVISOR",
        "group": "STAND_COUNT",
        "variants": [
          {
            "name": null,
            "key": "STANDARD"
          }
        ],
        "flight_specifications": [
          {
            "key": "SPEC_ADVISOR_STAND",
            "specs": [
              {
                "speed": {
                  "miles_per_hour": 22,
                  "meters_per_second": 10
                },
                "heading": "FORWARD",
                "flight_direction": "ANY",
                "buffer": {
                  "feet": -100,
                  "meters": -30
                },
                "gimbal_pitch_degrees": -90,
                "overlap_percentage": -70,
                "terrain_informed": true
              },
              {
                "speed": {
                  "miles_per_hour": 10,
                  "meters_per_second": 4.5
                },
                "heading": "FORWARD",
                "flight_direction": "ANY",
                "buffer": {
                  "feet": -100,
                  "meters": -30
                },
                "gimbal_pitch_degrees": -90,
                "overlap_percentage": -300,
                "terrain_informed": true
              }
            ]
          }
        ]
      }
    ]
  }
  }
}
```

```graphql
query ProductCatalogWithSettings {
  catalog {
  products {
    key
    settings {
      key
      input_type
      kind
      required
    }
  }
  }
}
```

```graphql
{
  "data": {
  "catalog": {
    "products": [
      {
        "key": "ADVISOR_STAND_COUNT",
        "settings": [
          {
            "key": "row_fill",
            "input_type": "Boolean",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "seeding_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "ADVISOR_TASSEL_COUNT",
        "settings": [
          {
            "key": "row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "seeding_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "ADVISOR_CROP_HEALTH",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_SETUP",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_STAND_COUNT_UNIFORMITY",
        "settings": [
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_UNIFORMITY",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_UNIFORMITY_MASKED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_MULTISPECTRAL_UNIFORMITY",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_MULTISPECTRAL_UNIFORMITY_MASKED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_MULTISPECTRAL_THERMAL_UNIFORMITY_MASKED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CROP_HEALTH_MULTISPECTRAL_UNIFORMITY_MASKED_TEMPERATURE",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CANOPY_COVER_UNIFORMITY",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CANOPY_COVER_UNIFORMITY_CHANGE",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_FLOWER_COVER_UNIFORMITY",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CANOPY_HEIGHT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_CANOPY_HEIGHT_LODGING",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PLOT_MATURITY_DATE",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_SETUP",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_STAND_COUNT",
        "settings": [
          {
            "key": "row_fill",
            "input_type": "Boolean",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "seeding_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_STAND_COUNT_UNIFORMITY",
        "settings": [
          {
            "key": "row_fill",
            "input_type": "Boolean",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "seeding_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_STAND_COUNT_MF_UNIFORMITY",
        "settings": [
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "male_seed_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "female_seed_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "male_row_count",
            "input_type": "Int",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "female_row_count",
            "input_type": "Int",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "male_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "female_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "male_female_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_TASSEL_COUNT",
        "settings": [
          {
            "key": "row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "seeding_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_TASSEL_COUNT_MF",
        "settings": [
          {
            "key": "crop_type",
            "input_type": "CropType",
            "kind": "ENUM",
            "required": true
          },
          {
            "key": "male_seed_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "female_seed_rate",
            "input_type": "AnalyticsPlantingRateInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "male_row_count",
            "input_type": "Int",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "female_row_count",
            "input_type": "Int",
            "kind": "SCALAR",
            "required": true
          },
          {
            "key": "male_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "female_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "male_female_row_spacing",
            "input_type": "RowSpacingInput",
            "kind": "INPUT_OBJECT",
            "required": true
          },
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_MOSAIC_RGB",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_MOSAIC_RGB_ALIGNED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_MOSAIC",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_MOSAIC_ALIGNED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_MOSAIC_MULTISPECTRAL",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_MOSAIC_MULTISPECTRAL_ALIGNED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_MOSAIC_MULTISPECTRAL_TEMPERATURE_ALIGNED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_HEALTH_GRID",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CANOPY_COVER_SPOT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CANOPY_COVER_GRID",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_FLOWER_COVER_SPOT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_FLOWER_COVER_GRID",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_RESIDUE_COVER_SPOT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_RESIDUE_COVER_GRID",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_CROP_AREA",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_ELEVATION_HYDROLOGY",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "FIELD_SCALE_ELEVATION",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_SETUP",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_COUNT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_COUNT_ADVANCED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_STATUS",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_STATUS_ADVANCED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_HEALTH",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_CANOPY_COVER",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_FLOWER_COVER",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "PERMANENT_CROP_TREE_CANOPY_HEIGHT",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": false
          }
        ]
      },
      {
        "key": "CONTRACT_DEFINED_NON_MOSAIC_BASED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": true
          }
        ]
      },
      {
        "key": "CONTRACT_DEFINED_MOSAIC_BASED",
        "settings": [
          {
            "key": "fulfillment_instructions",
            "input_type": "String",
            "kind": "SCALAR",
            "required": true
          }
        ]
      }
    ]
  }
  }
}
```


---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
