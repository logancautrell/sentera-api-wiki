"""
Test fixtures and stubs for sentera-wiki-builder.

These provide realistic (but minimal) HTML snippets that mimic the stable
CSS classes used by the live Sentera docs (.field-entry, .deprecation-notice,
table.arguments, etc.). This allows pure unit testing with no network calls.
"""

import pytest
from pathlib import Path


# =============================================================================
# Minimal realistic HTML fixtures (stubs of live pages)
# =============================================================================

CATALOG_HTML = """<!DOCTYPE html>
<html>
<head><title>catalog</title></head>
<body>
<div id="wrap"><div id="content">
  <h1>catalog</h1>
  <p>Retrieve a list of all Sentera's FieldInsights products.</p>

  <h2>Return fields</h2>

  <div class="field-entry">
    <span class="field-name anchored" id="products">
      products (
      <code><a href="/api/docs/object/product">[Product!]!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <p>The list of products.</p>
    </div>
  </div>

  <div class="field-entry">
    <span class="field-name anchored" id="version">
      version (
      <code><a href="/api/docs/scalar/string">String!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <p>The version of the product catalog represented by this query result.</p>
    </div>
  </div>

  <h2>Examples</h2>
  <h3>Catalog (with flight specifications)</h3>
  <pre>query ProductCatalog { catalog { products { name sku } } }</pre>
  <pre>{ "data": { "catalog": { "products": [ { "name": "Test", "sku": "123" } ] } } }</pre>
</div></div>
</body>
</html>
"""

UPDATE_SHAPE_HTML = """<!DOCTYPE html>
<html>
<body>
<div id="content">
  <h1>update_shape</h1>
  <p>Update a shape for a field.</p>

  <h2>Input fields</h2>

  <div class="field-entry">
    <span class="field-name anchored" id="sentera_id">
      sentera_id (
      <code><a href="/api/docs/scalar/id">ID!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <p>Read-only Sentera ID of the shape.</p>
    </div>
  </div>

  <div class="field-entry">
    <span class="field-name anchored" id="geometry">
      geometry (
      <code><a href="/api/docs/scalar/geojson">GeoJSON</a></code>
      )
    </span>
    <div class="description-wrapper">
      <p>A GeoJSON FeatureCollection...</p>
    </div>
  </div>

  <h2>Return fields</h2>

  <div class="field-entry">
    <span class="field-name anchored" id="acres">
      acres (
      <code><a href="/api/docs/scalar/float">Float!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <div class="deprecation-notice">
        <span class="deprecation-title">Deprecation notice</span>
        <p>Support added for metric units. Please use area instead.</p>
      </div>
      <p>Amount of acreage contained in this shape.</p>
    </div>
  </div>

  <div class="field-entry">
    <span class="field-name anchored" id="area">
      area (
      <code><a href="/api/docs/object/area">Area!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <p>Area of the shape with the specified units.</p>
      <table class="arguments">
        <thead><tr><th>Argument</th><th>Type</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>unit</td><td><code>AreaUnitType</code></td><td>The unit...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="field-entry">
    <span class="field-name anchored" id="geo_positions">
      geo_positions (
      <code><a href="/api/docs/object/geoposition">[GeoPosition]!</a></code>
      )
    </span>
    <div class="description-wrapper">
      <div class="deprecation-notice">
        <span class="deprecation-title">Deprecation notice</span>
        <p>Please use the geometry GeoJSON field.</p>
      </div>
      <p>A closed collection of geo-positions...</p>
    </div>
  </div>
</div>
</body>
</html>
"""

UPLOADING_FILES_HTML = """<!DOCTYPE html>
<html>
<body>
<div id="content">
  <h1>Uploading Files</h1>
  <p>Sentera's GraphQL API supports two different approaches for uploading files.</p>

  <h2>Approaches</h2>
  <h3>Single-part Uploads</h3>
  <p>This is the easiest way to upload small files.</p>

  <h3>Multi-part Uploads</h3>
  <p>This is the preferred way to upload larger files (greater than 10MB).</p>

  <h2>File Upload Owners</h2>
  <p>Certain mutations accept a list of file IDs...</p>
</div>
</body>
</html>
"""


@pytest.fixture
def sample_html():
    """Return a dict of minimal but realistic HTML stubs keyed by kind."""
    return {
        "query": CATALOG_HTML,
        "mutation": UPDATE_SHAPE_HTML,
        "howto": UPLOADING_FILES_HTML,
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a clean temporary output directory for build_wiki tests."""
    return tmp_path / "test-wiki"


@pytest.fixture
def schema_file(tmp_path):
    """Create a minimal wiki_schema.yaml for testing."""
    content = """- url: "https://admin.sentera.com/api/docs/query/catalog/"
  tags: ["core", "test"]
- url: "https://admin.sentera.com/api/docs/mutation/update_shape/"
  tags: ["shapes", "test"]
"""
    path = tmp_path / "wiki_schema.yaml"  # tests use a flat temp dir simulating the new layout
    path.write_text(content)
    return path
