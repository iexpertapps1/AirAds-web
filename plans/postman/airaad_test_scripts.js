/**
 * AirAd Postman Test Scripts
 * Copy-paste each block into the "Tests" tab of the matching request
 * after importing the OpenAPI schema from GET /api/v1/schema/.
 */

/* ── POST /api/v1/auth/login/ ─────────────────────────────────────────────── */
// Tests tab
const loginTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("success=true", () => pm.expect(b.success).to.be.true);
pm.test("access token present", () => pm.expect(b.data.tokens.access).to.be.a("string").and.not.empty);
pm.test("refresh token present", () => pm.expect(b.data.tokens.refresh).to.be.a("string").and.not.empty);
pm.test("role is valid", () => {
  const roles = ["SUPER_ADMIN","CITY_MANAGER","DATA_ENTRY","QA_REVIEWER","FIELD_AGENT","ANALYST","SUPPORT"];
  pm.expect(roles).to.include(b.data.user.role);
});
pm.environment.set("access_token", b.data.tokens.access);
pm.environment.set("refresh_token", b.data.tokens.refresh);
`;

/* ── POST /api/v1/auth/login/ — lockout scenario (5 bad attempts) ─────────── */
const loginLockoutTests = `
pm.test("Status 429", () => pm.response.to.have.status(429));
pm.test("Retry-After header ≤900s", () => {
  const ra = parseInt(pm.response.headers.get("Retry-After"), 10);
  pm.expect(ra).to.be.at.most(900);
});
pm.test("success=false", () => pm.expect(pm.response.json().success).to.be.false);
`;

/* ── POST /api/v1/auth/refresh/ ───────────────────────────────────────────── */
const refreshTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("new access token", () => pm.expect(b.access).to.be.a("string").and.not.empty);
pm.environment.set("access_token", b.access);
`;

/* ── POST /api/v1/auth/logout/ ────────────────────────────────────────────── */
const logoutTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("success=true", () => pm.expect(pm.response.json().success).to.be.true);
pm.environment.unset("access_token");
pm.environment.unset("refresh_token");
`;

/* ── POST /api/v1/auth/users/ (SUPER_ADMIN only) ──────────────────────────── */
const createAdminUserTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("UUID id", () => pm.expect(b.data.id).to.match(/^[0-9a-f-]{36}$/i));
pm.test("role matches request", () => pm.expect(b.data.role).to.equal(JSON.parse(pm.request.body.raw).role));
pm.environment.set("created_admin_user_id", b.data.id);
`;

/* ── POST /api/v1/auth/users/ — non-SUPER_ADMIN ──────────────────────────── */
const createAdminUserForbiddenTests = `
pm.test("Status 403", () => pm.response.to.have.status(403));
pm.test("success=false", () => pm.expect(pm.response.json().success).to.be.false);
`;

/* ── POST /api/v1/geo/countries/ ─────────────────────────────────────────── */
const createCountryTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("code is 2 chars", () => pm.expect(b.data.code).to.have.lengthOf(2));
pm.environment.set("country_id", b.data.id);
`;

/* ── POST /api/v1/geo/cities/ ────────────────────────────────────────────── */
const createCityTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("slug present", () => pm.expect(b.data.slug).to.be.a("string").and.not.empty);
pm.environment.set("city_id", b.data.id);
`;

/* ── PATCH /api/v1/geo/cities/{pk}/ with slug — immutability ─────────────── */
const patchCitySlugImmutableTests = `
pm.test("Status 400", () => pm.response.to.have.status(400));
pm.test("immutable error", () => pm.expect(pm.response.json().message.toLowerCase()).to.include("immutable"));
`;

/* ── POST /api/v1/geo/areas/ ─────────────────────────────────────────────── */
const createAreaTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("area_id", pm.response.json().data.id);
`;

/* ── POST /api/v1/geo/landmarks/ ─────────────────────────────────────────── */
const createLandmarkTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("landmark_id", pm.response.json().data.id);
`;

/* ── POST /api/v1/tags/ ──────────────────────────────────────────────────── */
const createTagTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("not SYSTEM type", () => pm.expect(b.data.tag_type).to.not.equal("SYSTEM"));
pm.environment.set("tag_id", b.data.id);
`;

/* ── POST /api/v1/tags/ with tag_type=SYSTEM ─────────────────────────────── */
const createSystemTagRejectedTests = `
pm.test("Status 403", () => pm.response.to.have.status(403));
pm.test("SYSTEM error", () => pm.expect(pm.response.json().message.toLowerCase()).to.include("system"));
`;

/* ── POST /api/v1/vendors/ ───────────────────────────────────────────────── */
const createVendorTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("qc_status=PENDING", () => pm.expect(b.data.qc_status).to.equal("PENDING"));
pm.test("phone decrypted (starts with +)", () => pm.expect(b.data.phone).to.match(/^\+/));
pm.test("gps_point is GeoJSON Point", () => {
  pm.expect(b.data.gps_point.type).to.equal("Point");
  pm.expect(b.data.gps_point.coordinates).to.have.lengthOf(2);
});
pm.test("is_deleted=false", () => pm.expect(b.data.is_deleted).to.be.false);
pm.environment.set("vendor_id", b.data.id);
`;

/* ── POST /api/v1/vendors/ — invalid business_hours ─────────────────────── */
const createVendorInvalidHoursTests = `
pm.test("Status 400", () => pm.response.to.have.status(400));
pm.test("business_hours error", () => {
  const msg = pm.response.json().message.toLowerCase();
  pm.expect(msg.includes("business_hours") || msg.includes("open") || msg.includes("close")).to.be.true;
});
`;

/* ── DELETE /api/v1/vendors/{pk}/ — soft delete ─────────────────────────── */
const softDeleteVendorTests = `
pm.test("Status 204", () => pm.response.to.have.status(204));
pm.sendRequest({
  url: pm.environment.get("base_url") + "/api/v1/vendors/" + pm.environment.get("vendor_id") + "/",
  method: "GET",
  header: { "Authorization": "Bearer " + pm.environment.get("access_token") }
}, (err, res) => {
  pm.test("Soft-deleted vendor returns 404", () => pm.expect(res.code).to.equal(404));
});
`;

/* ── PATCH /api/v1/vendors/{pk}/qc-status/ ───────────────────────────────── */
const updateQCStatusTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("qc_status updated", () => pm.expect(b.data.qc_status).to.equal(JSON.parse(pm.request.body.raw).qc_status));
pm.test("qc_reviewed_by set", () => pm.expect(b.data.qc_reviewed_by).to.not.be.null);
pm.test("qc_reviewed_at set", () => pm.expect(b.data.qc_reviewed_at).to.not.be.null);
`;

/* ── PATCH /api/v1/vendors/{pk}/qc-status/ — DATA_ENTRY blocked ─────────── */
const updateQCStatusForbiddenTests = `
pm.test("Status 403", () => pm.response.to.have.status(403));
`;

/* ── POST /api/v1/imports/ (multipart CSV upload) ────────────────────────── */
const uploadCSVTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("status=QUEUED", () => pm.expect(b.data.status).to.equal("QUEUED"));
pm.test("file_key is S3 key not URL", () => {
  pm.expect(b.data.file_key).to.not.include("https://");
  pm.expect(b.data.file_key).to.not.include("http://");
});
pm.environment.set("import_batch_id", b.data.id);
`;

/* ── GET /api/v1/imports/{pk}/ ───────────────────────────────────────────── */
const getImportBatchTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("valid status", () => pm.expect(["QUEUED","PROCESSING","DONE","FAILED"]).to.include(b.data.status));
if (b.data.status === "DONE") {
  pm.test("error_log ≤1000 entries", () => pm.expect(b.data.error_log.length).to.be.at.most(1000));
}
`;

/* ── POST /api/v1/field-ops/ ─────────────────────────────────────────────── */
const createFieldVisitTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("GPS point is GeoJSON", () => pm.expect(b.data.gps_confirmed_point.type).to.equal("Point"));
pm.environment.set("field_visit_id", b.data.id);
`;

/* ── POST /api/v1/field-ops/{visit_pk}/photos/upload/ ────────────────────── */
const uploadFieldPhotoTests = `
pm.test("Status 201", () => pm.response.to.have.status(201));
const b = pm.response.json();
pm.test("presigned URL returned", () => pm.expect(b.data.presigned_url).to.include("X-Amz-Signature"));
pm.test("s3_key NOT exposed", () => pm.expect(b.data.s3_key).to.be.undefined);
`;

/* ── GET /api/v1/qa/dashboard/ ───────────────────────────────────────────── */
const qaDashboardTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
if (b.data.vendors && b.data.vendors.length > 0) {
  pm.test("all vendors NEEDS_REVIEW", () => b.data.vendors.forEach(v => pm.expect(v.qc_status).to.equal("NEEDS_REVIEW")));
}
`;

/* ── GET /api/v1/analytics/kpis/ ─────────────────────────────────────────── */
const analyticsKPITests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("total_vendors present", () => pm.expect(b.data.total_vendors).to.be.a("number"));
`;

/* ── GET /api/v1/audit/ ──────────────────────────────────────────────────── */
const auditLogTests = `
pm.test("Status 200", () => pm.response.to.have.status(200));
const b = pm.response.json();
pm.test("paginated count", () => pm.expect(b.count).to.be.a("number"));
pm.sendRequest({
  url: pm.environment.get("base_url") + "/api/v1/audit/",
  method: "POST",
  header: { "Authorization": "Bearer " + pm.environment.get("access_token"), "Content-Type": "application/json" },
  body: { mode: "raw", raw: "{}" }
}, (err, res) => {
  pm.test("POST /audit/ returns 405 (immutable)", () => pm.expect(res.code).to.equal(405));
});
`;

/* ── GET /api/v1/health/ ─────────────────────────────────────────────────── */
const healthCheckTests = `
pm.test("200 or 503", () => pm.expect([200, 503]).to.include(pm.response.code));
const b = pm.response.json();
pm.test("status field present", () => pm.expect(b.status).to.be.oneOf(["ok", "degraded"]));
pm.test("database check present", () => pm.expect(b.checks).to.have.property("database"));
pm.test("redis check present", () => pm.expect(b.checks).to.have.property("redis"));
pm.sendRequest({ url: pm.environment.get("base_url") + "/api/v1/health/", method: "GET" }, (err, res) => {
  pm.test("health accessible without token", () => pm.expect([200, 503]).to.include(res.code));
});
`;

/* ── COLLECTION-LEVEL Pre-request Script ─────────────────────────────────── */
// Set this on the Collection root → Pre-request Scripts tab.
// Auto-logs in as SUPER_ADMIN if access_token is missing.
const collectionPreRequestScript = `
if (!pm.environment.get("access_token")) {
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
}
`;

/* ── RBAC Role-Switch Pre-request Script ─────────────────────────────────── */
// Set pm.environment.set("test_role", "DATA_ENTRY") before the request,
// then attach this as the Pre-request Script on any RBAC test request.
const rbacSwitchRolePreRequest = `
const creds = {
  SUPER_ADMIN:  { email: pm.environment.get("super_admin_email"),  password: pm.environment.get("super_admin_password") },
  CITY_MANAGER: { email: pm.environment.get("city_manager_email"), password: pm.environment.get("city_manager_password") },
  DATA_ENTRY:   { email: pm.environment.get("data_entry_email"),   password: pm.environment.get("data_entry_password") },
  QA_REVIEWER:  { email: pm.environment.get("qa_reviewer_email"),  password: pm.environment.get("qa_reviewer_password") },
  FIELD_AGENT:  { email: pm.environment.get("field_agent_email"),  password: pm.environment.get("field_agent_password") },
  ANALYST:      { email: pm.environment.get("analyst_email"),      password: pm.environment.get("analyst_password") },
};
const role = pm.environment.get("test_role") || "SUPER_ADMIN";
const c = creds[role];
if (c) {
  pm.sendRequest({
    url: pm.environment.get("base_url") + "/api/v1/auth/login/",
    method: "POST",
    header: { "Content-Type": "application/json" },
    body: { mode: "raw", raw: JSON.stringify({ email: c.email, password: c.password }) }
  }, (err, res) => {
    if (!err && res.code === 200) {
      pm.environment.set("access_token", res.json().data.tokens.access);
      console.log("Switched to role:", role);
    }
  });
}
`;
