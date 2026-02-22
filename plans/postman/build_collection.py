#!/usr/bin/env python3
"""
Build a complete Postman Collection v2.1 JSON for AirAd backend.
Reads the live OpenAPI schema from http://localhost:8000/api/v1/schema/
and produces airaad_collection.json with all endpoints, test scripts,
example payloads, and Bearer auth pre-configured.
"""
import json, uuid, re
import urllib.request
import yaml  # PyYAML

BASE_URL = "{{base_url}}"

# ── Test scripts per operationId ──────────────────────────────────────────────
TEST_SCRIPTS = {
    "auth_login_create": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("success=true", () => pm.expect(b.success).to.be.true);
pm.test("access token present", () => pm.expect(b.data.tokens.access).to.be.a("string").and.not.empty);
pm.test("refresh token present", () => pm.expect(b.data.tokens.refresh).to.be.a("string").and.not.empty);
pm.test("role is valid", () => {
  const roles = ["SUPER_ADMIN","CITY_MANAGER","DATA_ENTRY","QA_REVIEWER","FIELD_AGENT","ANALYST","SUPPORT"];
  pm.expect(roles).to.include(b.data.user.role);
});
pm.environment.set("access_token", b.data.tokens.access);
pm.environment.set("refresh_token", b.data.tokens.refresh);""",

    "auth_refresh_create": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("new access token", () => pm.expect(b.access).to.be.a("string").and.not.empty);
pm.environment.set("access_token", b.access);""",

    "auth_logout_create": """pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("success=true", () => pm.expect(pm.response.json().success).to.be.true);
pm.environment.unset("access_token");
pm.environment.unset("refresh_token");""",

    "auth_profile_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("email present", () => pm.expect(b.data.email).to.be.a("string"));
pm.test("role present", () => pm.expect(b.data.role).to.be.a("string"));""",

    "auth_users_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("UUID id", () => pm.expect(b.data.id).to.match(/^[0-9a-f-]{36}$/i));
pm.test("role matches request", () => pm.expect(b.data.role).to.equal(JSON.parse(pm.request.body.raw).role));
pm.environment.set("created_admin_user_id", b.data.id);""",

    "geo_countries_list": """pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("results array", () => pm.expect(pm.response.json().data).to.be.an("array"));""",

    "geo_countries_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("code is 2 chars", () => pm.expect(b.data.code).to.have.lengthOf(2));
pm.environment.set("country_id", b.data.id);""",

    "geo_cities_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "geo_cities_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("slug present", () => pm.expect(b.data.slug).to.be.a("string").and.not.empty);
pm.environment.set("city_id", b.data.id);""",

    "geo_cities_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "geo_cities_partial_update": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "geo_areas_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "geo_areas_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("area_id", pm.response.json().data.id);""",

    "geo_landmarks_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "geo_landmarks_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("landmark_id", pm.response.json().data.id);""",

    "tags_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "tags_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("not SYSTEM type", () => pm.expect(b.data.tag_type).to.not.equal("SYSTEM"));
pm.environment.set("tag_id", b.data.id);""",

    "tags_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "tags_partial_update": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "tags_destroy": """pm.test("Status 204", () => pm.response.to.have.status(204));""",

    "vendors_list": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("paginated", () => pm.expect(b.count).to.be.a("number"));
if (b.data && b.data.length > 0) {
  pm.test("no deleted vendors", () => b.data.forEach(v => pm.expect(v.is_deleted).to.be.false));
}""",

    "vendors_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("qc_status=PENDING", () => pm.expect(b.data.qc_status).to.equal("PENDING"));
pm.test("gps_point is GeoJSON Point", () => {
  pm.expect(b.data.gps_point.type).to.equal("Point");
  pm.expect(b.data.gps_point.coordinates).to.have.lengthOf(2);
});
pm.test("is_deleted=false", () => pm.expect(b.data.is_deleted).to.be.false);
pm.environment.set("vendor_id", b.data.id);""",

    "vendors_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("is_deleted=false", () => pm.expect(pm.response.json().data.is_deleted).to.be.false);""",

    "vendors_partial_update": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "vendors_destroy": """pm.test("Status 204", () => pm.response.to.have.status(204));
pm.sendRequest({
  url: pm.environment.get("base_url") + "/api/v1/vendors/" + pm.environment.get("vendor_id") + "/",
  method: "GET",
  header: { "Authorization": "Bearer " + pm.environment.get("access_token") }
}, (err, res) => {
  pm.test("Soft-deleted vendor returns 404", () => pm.expect(res.code).to.equal(404));
});""",

    "vendors_qc_status_partial_update": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("qc_status updated", () => pm.expect(b.data.qc_status).to.equal(JSON.parse(pm.request.body.raw).qc_status));
pm.test("qc_reviewed_by set", () => pm.expect(b.data.qc_reviewed_by).to.not.be.null);
pm.test("qc_reviewed_at set", () => pm.expect(b.data.qc_reviewed_at).to.not.be.null);""",

    "imports_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "imports_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("status=QUEUED", () => pm.expect(b.data.status).to.equal("QUEUED"));
pm.test("file_key is S3 key not URL", () => {
  pm.expect(b.data.file_key).to.not.include("https://");
  pm.expect(b.data.file_key).to.not.include("http://");
});
pm.environment.set("import_batch_id", b.data.id);""",

    "imports_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("valid status", () => pm.expect(["QUEUED","PROCESSING","DONE","FAILED"]).to.include(b.data.status));
if (b.data.status === "DONE") {
  pm.test("error_log ≤1000 entries", () => pm.expect(b.data.error_log.length).to.be.at.most(1000));
}""",

    "field_ops_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "field_ops_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("GPS point is GeoJSON", () => pm.expect(b.data.gps_confirmed_point.type).to.equal("Point"));
pm.environment.set("field_visit_id", b.data.id);""",

    "field_ops_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "field_ops_photos_list": """pm.test("Status 200", () => pm.response.to.have.status(200));""",

    "field_ops_photos_upload_create": """pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("presigned URL returned", () => pm.expect(b.data.presigned_url).to.include("X-Amz-Signature"));
pm.test("s3_key NOT exposed", () => pm.expect(b.data.s3_key).to.be.undefined);""",

    "qa_dashboard_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
if (b.data && b.data.vendors && b.data.vendors.length > 0) {
  pm.test("all vendors NEEDS_REVIEW", () => b.data.vendors.forEach(v => pm.expect(v.qc_status).to.equal("NEEDS_REVIEW")));
}""",

    "analytics_kpis_retrieve": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("total_vendors present", () => pm.expect(b.data.total_vendors).to.be.a("number"));""",

    "audit_list": """pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("paginated count", () => pm.expect(b.count).to.be.a("number"));
pm.sendRequest({
  url: pm.environment.get("base_url") + "/api/v1/audit/",
  method: "POST",
  header: { "Authorization": "Bearer " + pm.environment.get("access_token"), "Content-Type": "application/json" },
  body: { mode: "raw", raw: "{}" }
}, (err, res) => {
  pm.test("POST /audit/ returns 405 (immutable)", () => pm.expect(res.code).to.equal(405));
});""",

    "health_retrieve": """pm.test("200 or 503", () => pm.expect([200, 503]).to.include(pm.response.code));
const b = pm.response.json();
pm.test("status field present", () => pm.expect(b.status).to.be.oneOf(["healthy", "degraded"]));
pm.sendRequest({ url: pm.environment.get("base_url") + "/api/v1/health/", method: "GET" }, (err, res) => {
  pm.test("health accessible without token", () => pm.expect([200, 503]).to.include(res.code));
});""",
}

# ── Example request bodies ────────────────────────────────────────────────────
EXAMPLE_BODIES = {
    "auth_login_create": {"email": "{{super_admin_email}}", "password": "{{super_admin_password}}"},
    "auth_refresh_create": {"refresh": "{{refresh_token}}"},
    "auth_logout_create": {"refresh": "{{refresh_token}}"},
    "auth_users_create": {"email": "newuser@airaad.com", "password": "NewUser@2024!", "full_name": "New User", "role": "DATA_ENTRY"},
    "geo_countries_create": {"name": "Pakistan", "code": "PK"},
    "geo_cities_create": {"name": "Islamabad", "country_id": "{{country_id}}", "centroid": {"type": "Point", "coordinates": [73.0479, 33.6844]}},
    "geo_cities_partial_update": {"name": "Islamabad Updated"},
    "geo_areas_create": {"name": "F-10 Markaz", "city_id": "{{city_id}}"},
    "geo_landmarks_create": {"name": "Centaurus Mall", "area_id": "{{area_id}}", "location": {"type": "Point", "coordinates": [73.0479, 33.6844]}},
    "tags_create": {"name": "Pizza", "tag_type": "CATEGORY"},
    "tags_partial_update": {"name": "Pizza Updated"},
    "vendors_create": {
        "business_name": "Karachi Biryani House",
        "city_id": "{{city_id}}",
        "area_id": "{{area_id}}",
        "latitude": 24.8607,
        "longitude": 67.0011,
        "phone": "+923001234567",
        "description": "Famous biryani restaurant",
        "address_text": "Shop 5, Block 2, Clifton, Karachi",
        "data_source": "MANUAL_ENTRY",
        "business_hours": {
            "MON": {"open": "09:00", "close": "22:00", "is_closed": False},
            "TUE": {"open": "09:00", "close": "22:00", "is_closed": False},
            "WED": {"open": "09:00", "close": "22:00", "is_closed": False},
            "THU": {"open": "09:00", "close": "22:00", "is_closed": False},
            "FRI": {"open": "09:00", "close": "23:00", "is_closed": False},
            "SAT": {"open": "10:00", "close": "23:00", "is_closed": False},
            "SUN": {"open": "00:00", "close": "00:00", "is_closed": True},
        },
    },
    "vendors_partial_update": {"description": "Updated description", "qc_notes": "Verified on-site."},
    "vendors_qc_status_partial_update": {"qc_status": "APPROVED", "qc_notes": "Verified on-site. GPS accurate within 5m."},
    "field_ops_create": {
        "vendor_id": "{{vendor_id}}",
        "latitude": 24.8607,
        "longitude": 67.0011,
        "visit_notes": "Confirmed active. Signage visible.",
        "visited_at": "2024-01-06T10:00:00Z",
    },
}

# ── Collection-level pre-request script ──────────────────────────────────────
COLLECTION_PRE_REQUEST = """if (!pm.environment.get("access_token")) {
  pm.sendRequest({
    url: pm.environment.get("base_url") + "/api/v1/auth/login/",
    method: "POST",
    header: { "Content-Type": "application/json" },
    body: { mode: "raw", raw: JSON.stringify({
      email: pm.environment.get("super_admin_email"),
      password: pm.environment.get("super_admin_password")
    })}
  }, (err, res) => {
    if (!err && res.code === 200) {
      const b = res.json();
      pm.environment.set("access_token", b.data.tokens.access);
      pm.environment.set("refresh_token", b.data.tokens.refresh);
      console.log("Auto-login OK. Role:", b.data.user.role);
    }
  });
}"""

# ── Path param → env var mapping ─────────────────────────────────────────────
PATH_PARAM_MAP = {
    "pk": {
        "vendor": "{{vendor_id}}",
        "city": "{{city_id}}",
        "area": "{{area_id}}",
        "landmark": "{{landmark_id}}",
        "tag": "{{tag_id}}",
        "import": "{{import_batch_id}}",
        "field": "{{field_visit_id}}",
        "default": "{{vendor_id}}",
    },
    "visit_pk": "{{field_visit_id}}",
    "id": "{{vendor_id}}",
}


def resolve_path(path: str) -> str:
    """Convert OpenAPI path params {pk} to Postman {{var}} format."""
    def replace(m):
        param = m.group(1)
        if param == "visit_pk":
            return "{{field_visit_id}}"
        if param == "pk":
            # Guess from path context
            if "vendor" in path:
                return "{{vendor_id}}"
            if "cit" in path:
                return "{{city_id}}"
            if "area" in path:
                return "{{area_id}}"
            if "landmark" in path:
                return "{{landmark_id}}"
            if "tag" in path:
                return "{{tag_id}}"
            if "import" in path:
                return "{{import_batch_id}}"
            if "field" in path:
                return "{{field_visit_id}}"
            return "{{vendor_id}}"
        return "{{" + param + "}}"
    return re.sub(r"\{(\w+)\}", replace, path)


def make_request_item(path: str, method: str, op: dict) -> dict:
    op_id = op.get("operationId", "")
    summary = op.get("summary", op_id)
    tags = op.get("tags", ["Other"])
    is_auth_required = bool(op.get("security"))

    # URL
    resolved = resolve_path(path)
    url_raw = BASE_URL + resolved

    # Headers
    headers = [{"key": "Content-Type", "value": "application/json"}]
    if is_auth_required:
        headers.append({"key": "Authorization", "value": "Bearer {{access_token}}"})

    # Body
    body = None
    req_body = op.get("requestBody", {})
    if req_body:
        content = req_body.get("content", {})
        if "multipart/form-data" in content:
            headers = [h for h in headers if h["key"] != "Content-Type"]
            body = {
                "mode": "formdata",
                "formdata": [{"key": "file", "type": "file", "src": "/path/to/vendors.csv"}],
            }
        elif op_id in EXAMPLE_BODIES:
            body = {"mode": "raw", "raw": json.dumps(EXAMPLE_BODIES[op_id], indent=2), "options": {"raw": {"language": "json"}}}
        elif "application/json" in content:
            schema = content["application/json"].get("schema", {})
            body = {"mode": "raw", "raw": json.dumps({"_note": "Fill in required fields"}, indent=2), "options": {"raw": {"language": "json"}}}

    # Query params
    query = []
    for param in op.get("parameters", []):
        if param.get("in") == "query":
            query.append({"key": param["name"], "value": "", "disabled": True, "description": param.get("description", "")})

    # Test script
    test_script = TEST_SCRIPTS.get(op_id, f'pm.test("Status 2xx", () => pm.expect(pm.response.code).to.be.oneOf([200, 201, 204]));')

    item = {
        "name": summary,
        "request": {
            "method": method.upper(),
            "header": headers,
            "url": {
                "raw": url_raw + ("?" if query else ""),
                "host": ["{{base_url}}"],
                "path": [p for p in resolved.split("/") if p],
                "query": query,
            },
        },
        "event": [
            {
                "listen": "test",
                "script": {"type": "text/javascript", "exec": test_script.split("\n")},
            }
        ],
        "_postman_id": str(uuid.uuid4()),
    }

    if body:
        item["request"]["body"] = body

    return item


def build_collection(schema: dict) -> dict:
    paths = schema.get("paths", {})
    info = schema.get("info", {})

    # Group by tag
    folders: dict[str, list] = {}
    tag_order = ["Auth", "Geo", "Tags", "Vendors", "Imports", "Field Ops", "QA", "Analytics", "Audit", "Health", "Schema"]

    for path, path_item in paths.items():
        for method, op in path_item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            tags = op.get("tags", ["Other"])
            tag = tags[0] if tags else "Other"
            if tag not in folders:
                folders[tag] = []
            folders[tag].append(make_request_item(path, method, op))

    # Build folder items in order
    items = []
    for tag in tag_order:
        if tag in folders:
            items.append({
                "name": tag,
                "_postman_id": str(uuid.uuid4()),
                "item": folders[tag],
            })
    # Any remaining tags
    for tag, reqs in folders.items():
        if tag not in tag_order:
            items.append({"name": tag, "_postman_id": str(uuid.uuid4()), "item": reqs})

    collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": "AirAd API — Phase A",
            "description": f"AirAd backend API collection. {info.get('description', '')} Generated from live OpenAPI schema at /api/v1/schema/.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "event": [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": COLLECTION_PRE_REQUEST.split("\n"),
                },
            }
        ],
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
        },
        "variable": [{"key": "base_url", "value": "http://localhost:8000"}],
        "item": items,
    }

    return {"collection": collection}


if __name__ == "__main__":
    # Fetch live schema
    print("Fetching OpenAPI schema from http://localhost:8000/api/v1/schema/ ...")
    with urllib.request.urlopen("http://localhost:8000/api/v1/schema/") as r:
        schema = yaml.safe_load(r.read())

    collection = build_collection(schema)

    out_path = "/Users/syedsmacbook/Developer/AirAds-web/plans/postman/airaad_collection.json"
    with open(out_path, "w") as f:
        json.dump(collection, f, indent=2)

    # Count items
    total = sum(len(f["item"]) for f in collection["collection"]["item"])
    print(f"✅ Collection written to {out_path}")
    print(f"   Folders: {len(collection['collection']['item'])}")
    print(f"   Requests: {total}")
