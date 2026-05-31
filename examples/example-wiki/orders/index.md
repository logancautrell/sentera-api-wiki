---
url: https://admin.sentera.com/api/docs/orders/index.html
kind: page
title: Orders
description: 'Placing orders for analytics is one of the main use-cases for the Sentera
  GraphQL API.

  The first thing you need to know is which product you want to order. You can get
  a list

  by using thecatalog query. You use theProductKeytype inplace_orderto order that
  specific product. You can determine if you

  have purchased that pr'
parent: null
children: []
tags: ['orders', 'analytics', 'core', 'howto']
last_fetched: '2026-05-31T14:18:04Z'
---

# Orders

**Description:** Placing orders for analytics is one of the main use-cases for the Sentera GraphQL API.
The first thing you need to know is which product you want to order. You can get a list
by using thecatalog query. You use theProductKeytype inplace_orderto order that specific product. You can determine if you
have purchased that pr

## Orders

Placing orders for analytics is one of the main use-cases for the Sentera GraphQL API.
The first thing you need to know is which product you want to order. You can get a list
by using the catalog query . You use the ProductKey type in place_order to order that specific product. You can determine if you
have purchased that product using the user_subscription_details query. Different products
also require certain types of input images / sensors. This is the minimum information needed
to place an order.


### Order Processing

Orders cannot proceed to processing until images are available. In addition certain products require
you to provide certain settings such as row_spacing and crop_type . If you create an order
without any of the required inputs for processing you can update the order later
with the update_order mutation.


### Order Status

Orders flow through a series of states on their way to completion.

```
stateDiagram-v2
    [*] --> Pending
    Pending --> NeedsSettings: CaptureComplete
    Pending --> Canceled: Cancel
    NeedsSettings --> Canceled: Cancel
    NeedsSettings --> Failure: Failed
    NeedsSettings --> Processing: SettingsComplete
    NeedsSettings --> NeedsSettings: UpdateSettings
    Processing --> Complete: AnalyticsComplete
    Processing --> Failure
    Processing --> Canceled: Cancel
    Failure --> Processing: Reprocess
    Failure --> Refly: Refly
    Canceled --> [*]
    Complete --> [*]
    Refly --> [*]
```


### Code Examples

Query orders and create or update orders


#### Introspection


##### Nested Introspection - ProductSettingsInput

This is a deeply nested introspection example that reveals all possible inputs for the ProductSettingsInput INPUT_OBJECT . To understand what settings go to what Product see our Catalog with settings query example.

```graphql
query ProductSettingsInput {
  __type(name: "ProductSettingsInput") {
    description
    inputFields {
      name
      type {
        name
        description
        inputFields {
          name
          type {
            kind
            ofType {
              name
              enumValues {
                name
              }
            }
          }
        }
        enumValues {
          name
        }
      }
    }
  }
}
```

```
{
  "data": {
    "__type": {
      "description": "All possible settings for ordering a product.",
      "inputFields": [
        {
          "name": "crop_type",
          "type": {
            "name": "CropType",
            "description": "Enumeration of the types of crops planted in a crop season.",
            "inputFields": null,
            "enumValues": [
              {
                "name": "ALFALFA"
              },
              {
                "name": "BARLEY"
              },
              {
                "name": "CANOLA"
              },
              {
                "name": "CORN"
              },
              {
                "name": "COTTON"
              },
              {
                "name": "POTATOES"
              },
              {
                "name": "RICE"
              },
              {
                "name": "SOYBEANS"
              },
              {
                "name": "SUGAR_BEET"
              },
              {
                "name": "UNKNOWN"
              },
              {
                "name": "WHEAT"
              }
            ]
          }
        },
        {
          "name": "male_seed_rate",
          "type": {
            "name": "AnalyticsPlantingRateInput",
            "description": "Analytics Planting Rate",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "AnalyticsPlantingRateType",
                    "enumValues": [
                      {
                        "name": "SEEDS_PER_ACRE"
                      },
                      {
                        "name": "SEEDS_PER_HECTARE"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "female_seed_rate",
          "type": {
            "name": "AnalyticsPlantingRateInput",
            "description": "Analytics Planting Rate",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "AnalyticsPlantingRateType",
                    "enumValues": [
                      {
                        "name": "SEEDS_PER_ACRE"
                      },
                      {
                        "name": "SEEDS_PER_HECTARE"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "male_row_count",
          "type": {
            "name": "Int",
            "description": "Represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.",
            "inputFields": null,
            "enumValues": null
          }
        },
        {
          "name": "female_row_count",
          "type": {
            "name": "Int",
            "description": "Represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.",
            "inputFields": null,
            "enumValues": null
          }
        },
        {
          "name": "male_row_spacing",
          "type": {
            "name": "RowSpacingInput",
            "description": "Row Spacing",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "RowSpacingUnit",
                    "enumValues": [
                      {
                        "name": "CENTIMETERS"
                      },
                      {
                        "name": "INCHES"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "female_row_spacing",
          "type": {
            "name": "RowSpacingInput",
            "description": "Row Spacing",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "RowSpacingUnit",
                    "enumValues": [
                      {
                        "name": "CENTIMETERS"
                      },
                      {
                        "name": "INCHES"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "row_spacing",
          "type": {
            "name": "RowSpacingInput",
            "description": "Row Spacing",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "RowSpacingUnit",
                    "enumValues": [
                      {
                        "name": "CENTIMETERS"
                      },
                      {
                        "name": "INCHES"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "seeding_rate",
          "type": {
            "name": "AnalyticsPlantingRateInput",
            "description": "Analytics Planting Rate",
            "inputFields": [
              {
                "name": "unit",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "AnalyticsPlantingRateType",
                    "enumValues": [
                      {
                        "name": "SEEDS_PER_ACRE"
                      },
                      {
                        "name": "SEEDS_PER_HECTARE"
                      }
                    ]
                  }
                }
              },
              {
                "name": "value",
                "type": {
                  "kind": "NON_NULL",
                  "ofType": {
                    "name": "Float",
                    "enumValues": null
                  }
                }
              }
            ],
            "enumValues": null
          }
        },
        {
          "name": "row_fill",
          "type": {
            "name": "Boolean",
            "description": "Represents `true` or `false` values.",
            "inputFields": null,
            "enumValues": null
          }
        }
      ]
    }
  }
}
```


##### Introspect an ENUM - CropType

This is an example of introspecting an ENUM type. ENUM types have enumValues .

```graphql
query EnumIntrospectionCropType {
  __type(name: "CropType") {
    kind
    description
    enumValues {
      name
    }
  }
}
```

```
{
  "data": {
    "__type": {
      "kind": "ENUM",
      "description": "Enumeration of the types of crops planted in a crop season.",
      "enumValues": [
        {
          "name": "ALFALFA"
        },
        {
          "name": "BARLEY"
        },
        {
          "name": "CANOLA"
        },
        {
          "name": "CORN"
        },
        {
          "name": "COTTON"
        },
        {
          "name": "POTATOES"
        },
        {
          "name": "RICE"
        },
        {
          "name": "SOYBEANS"
        },
        {
          "name": "SUGAR_BEET"
        },
        {
          "name": "UNKNOWN"
        },
        {
          "name": "WHEAT"
        }
      ]
    }
  }
}
```


##### Introspect an INPUT_OBJECT - RowSpacingInput

This is an example of introspecting an INPUT_OBJECT . These have inputFields and require a more
deeply nested query than the ENUM type above to get a full description.

```graphql
query InputObjectIntrospectionRowSpacing {
  __type(name: "RowSpacingInput") {
    description
    inputFields {
      description
      type {
        kind
        ofType {
          name
          kind
          description
          enumValues {
            name
          }
        }
      }
    }
  }
}
```

```
{
  "data": {
    "__type": {
      "description": "Row Spacing",
      "inputFields": [
        {
          "description": "The unit that provides meaning to the value of the row spacing.",
          "type": {
            "kind": "NON_NULL",
            "ofType": {
              "name": "RowSpacingUnit",
              "kind": "ENUM",
              "description": "Enumeration of the units of measure for the distance between rows of a crop in a field.",
              "enumValues": [
                {
                  "name": "CENTIMETERS"
                },
                {
                  "name": "INCHES"
                }
              ]
            }
          }
        },
        {
          "description": "The scalar value of the row spacing.",
          "type": {
            "kind": "NON_NULL",
            "ofType": {
              "name": "Float",
              "kind": "SCALAR",
              "description": "Represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).",
              "enumValues": null
            }
          }
        }
      ]
    }
  }
}
```

---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
