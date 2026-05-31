---
url: https://admin.sentera.com/api/docs/mutation/place_order/
kind: mutation
title: place_order
description: 'Create an order for one of Sentera''s FieldInsight products. Goherefor
  a general explanation of Orders

  and their statuses. For examples of theplace_ordermutation checkhere.'
parent: null
children: []
tags: ['orders', 'surveys', 'workflows']
last_fetched: '2026-05-31T14:18:12Z'
---

# place_order

**Description:** Create an order for one of Sentera's FieldInsight products. Goherefor a general explanation of Orders
and their statuses. For examples of theplace_ordermutation checkhere.

## Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deal_sentera_id` | `ID` | No | The Sentera ID of a deal to which the cost of this order should be charged. |
| `external_id` | `ExternalID` | No | The ID of the order in an external system. |
| `organization_sentera_id` | `ID` | No | The ID of the Organization to which this Order belongs. If not provided the
Order will be placed within the calling user's default organization. |
| `product_key` | `ProductKey!` | Yes | The product being ordered. |
| `product_variant_key` | `ProductVariantKey` | No | The specific variant of this product you would like. |
| `sensor_types` | `[SensorType!]` | Yes | **Deprecated:** Deprecated in favor of using product variant key. This allows for greater specificity in the deliverables requested for a given product. The sensor types that will be used to capture data for this order. |
| `settings` | `ProductSettingsInput` | No | The settings needed to process the Order. If the settings are incomplete
but the Order has a processable Survey, the Order will move to the "Needs
Settings" status. The settings are passed as JSON object in which each key corresponds to an input_type . An example demonstrating the settings for
each product can be found in the Catalog and you can introspect on the settings
input_types to determine their structure. |
| `survey_sentera_id` | `ID` | No | A survey containing the images necessary to process this order. Cannot be combined with the task input. |
| `task` | `OrderTaskInput` | No | The details of the task that will provide FieldCapture for the order. If not
provided one will be created without a specified Field. |

## Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `analytics` | `[Analytic!]!` | The set of analytics that comprise the product that was ordered. |
| `completed_at` | `ISO8601DateTime` | Date and time when the order was completed, in ISO 8601 format. |
| `content_hash` | `String!` | The current content hash for this item. |
| `created_at` | `ISO8601DateTime!` | The timestamp of when the item was created in the system. |
| `created_by` | `User!` | The user who created this item. |
| `deal` | `Deal` | The deal for the order, if any. |
| `external_id` | `ExternalID` | The unique identifier of this order in a customer's system. |
| `field` | `Field` | The field associated with this order. |
| `missing_settings` | `Boolean!` | **Deprecated:** Replaced with needs_settings. Is this order missing the settings necessary to begin processing an order? |
| `needs_settings` | `Boolean!` | Does this order need settings that are required to begin processing? |
| `organization` | `Organization!` | The organization in which this order was placed. |
| `organization_sentera_id` | `ID` | **Deprecated:** Use organization instead. The ID of the organization in which this order was placed. |
| `product` | `Product!` | The product that this order will fulfill. |
| `product_variant_key` | `ProductVariantKey` | The specific variant of the product that was ordered. |
| `sentera_id` | `ID!` | A system-generated key identifying a specific instance of an order. |
| `settings` | `ProductSettings` | The product settings for this order. |
| `status` | `OrderStatus!` | The status of the order. |
| `survey` | `Survey` | The survey containing the images to fulfill this order. |
| `task` | `FlightTask` | A task to capture the images for this order. |
| `updated_at` | `ISO8601DateTime!` | The timestamp of when the item was last updated in the system. |
| `updated_by` | `User` | The user who last updated this item. |

## Examples

```graphql
mutation PlaceOrder {
  place_order(product_key: FIELD_SCALE_STAND_COUNT, product_variant_key: "STANDARD") {
  sentera_id
  organization_sentera_id
  status
  product {
    sku
    name
  }
  settings {
    row_spacing {
      unit
      value
    }
    row_fill
    seeding_rate {
      unit
      value
    }
  }
  analytics {
    sku
    name
  }
  }
}
```

```graphql
{
  "data": {
  "place_order": {
    "sentera_id": "7qhgc8l_OD_phgrAcme_CV_deve_5ab6a8995_221219_142757",
    "organization_sentera_id": "121amqh_OR_phgrAcme_CV_deve_a7f4fbad8_221216_115034",
    "status": "PENDING",
    "product": {
      "sku": "71301-00",
      "name": "Field Scale Stand Count"
    },
    "settings": null,
    "analytics": [
      {
        "sku": "84001-00",
        "name": "Spot Scout Stand Count"
      }
    ]
  }
  }
}
```

```graphql
mutation PlaceOrder {
  place_order(product_key: FIELD_SCALE_STAND_COUNT,
            product_variant_key: "STANDARD",
            task: {
              field_sentera_id: "jzt2lzz_AS_8brhbkSentera_CV_deve_a66dedf98_200410_121407"
           }) {
  sentera_id
  organization_sentera_id
  status
  product {
    sku
    name
  }
  settings {
    row_spacing {
      unit
      value
    }
    row_fill
    seeding_rate {
      unit
      value
    }
  }
  task {
    sentera_id
  }
  analytics {
    sku
    name
  }
  }
}
```

```graphql
{
  "data": {
  "place_order": {
    "sentera_id": "7qhgc8l_OD_phgrAcme_CV_deve_5ab6a8995_221219_142757",
    "organization_sentera_id": "121amqh_OR_phgrAcme_CV_deve_a7f4fbad8_221216_115034",
    "status": "PENDING",
    "product": {
      "sku": "71301-00",
      "name": "Field Scale Stand Count"
    },
    "settings": null,
    "task": {
      "sentera_id": "v65zlut_TA_SHORT1_CV_deve_daa3db7bf_230314_081227"
    },
    "analytics": [
      {
        "sku": "84001-00",
        "name": "Spot Scout Stand Count"
      }
    ]
  }
  }
}
```


---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
