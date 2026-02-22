# TASK_FIX_M03 — Add PROMOTION + TIME Tags to Seed Data
**Severity:** 🟠 MAJOR — Seed data only covers 3 of 6 tag types; missing PROMOTION and TIME
**Session:** A-S8 | **Effort:** 15 min | **File:** `apps/accounts/management/commands/seed_data.py`

---

## PROBLEM

`seed_data.py` seeds 6 tags but only covers 3 of the 6 `TagType` values:
- ✅ LOCATION (2 tags)
- ✅ CATEGORY (2 tags)
- ✅ INTENT (2 tags)
- ❌ PROMOTION — missing
- ❌ TIME — missing
- ❌ SYSTEM — intentionally excluded (SYSTEM tags are created via migration/fixture only)

The `TagType` enum has 6 values. Seed data must cover all non-SYSTEM types so the development environment reflects production taxonomy.

---

## FIX

Locate the `_seed_tags()` method (or equivalent tag-seeding block) in `seed_data.py` and add 4 new tag entries — 2 for `TagType.TIME` and 2 for `TagType.PROMOTION`.

**Tags to add:**

```python
# TIME tags
{
    "name": "Happy Hour",
    "slug": "time-happy-hour",
    "tag_type": TagType.TIME,
    "display_color": "#F59E0B",
    "display_icon": "clock",
    "is_active": True,
},
{
    "name": "Weekend Special",
    "slug": "time-weekend-special",
    "tag_type": TagType.TIME,
    "display_color": "#10B981",
    "display_icon": "calendar",
    "is_active": True,
},
# PROMOTION tags
{
    "name": "20% Off",
    "slug": "promo-20-off",
    "tag_type": TagType.PROMOTION,
    "display_color": "#EF4444",
    "display_icon": "tag",
    "is_active": True,
},
{
    "name": "Buy 1 Get 1",
    "slug": "promo-bogo",
    "tag_type": TagType.PROMOTION,
    "display_color": "#8B5CF6",
    "display_icon": "gift",
    "is_active": True,
},
```

**Pattern to follow** — use the same `get_or_create` + `log_action` pattern already used for existing tags:

```python
for tag_data in tags_to_seed:
    tag, created = Tag.objects.get_or_create(
        slug=tag_data["slug"],
        defaults=tag_data,
    )
    if created:
        log_action(
            actor=system_user,
            action="TAG_SEED",
            target=tag,
            after_state={"name": tag.name, "tag_type": tag.tag_type},
        )
        self.stdout.write(f"  Created tag: {tag.name} ({tag.tag_type})")
    else:
        self.stdout.write(f"  Tag exists: {tag.name} ({tag.tag_type})")
```

---

## CONSTRAINTS

- **`get_or_create(slug=..., defaults=...)`** — idempotent; running `seed_data` twice must not create duplicates
- **`TagType.TIME`** and **`TagType.PROMOTION`** must be imported — verify they exist in `apps/tags/models.py`
- **Do NOT** seed `TagType.SYSTEM` tags — SYSTEM tags are reserved and must only be created via data migrations
- **`display_color`** and **`display_icon`** field names must match the actual `Tag` model fields — read `apps/tags/models.py` to confirm exact field names before writing
- **`log_action`** must be called for each created tag — R5 (AuditLog on every mutation)
- The seed command output must print a summary line like `"Seeded 10 tags (4 new, 6 existing)"` — update the count if a summary line exists

---

## VERIFICATION

```bash
cd airaad/backend

# Run seed command (idempotent — safe to run multiple times)
python manage.py seed_data --no-vendors

# Verify all 6 non-SYSTEM tag types are present
python manage.py shell -c "
from apps.tags.models import Tag, TagType
for tt in [TagType.LOCATION, TagType.CATEGORY, TagType.INTENT, TagType.TIME, TagType.PROMOTION]:
    count = Tag.objects.filter(tag_type=tt).count()
    print(f'{tt}: {count} tags')
"
# Expected output:
# LOCATION: 2 tags
# CATEGORY: 2 tags
# INTENT: 2 tags
# TIME: 2 tags
# PROMOTION: 2 tags

# Verify idempotency — running twice must not create duplicates
python manage.py seed_data --no-vendors
python manage.py shell -c "from apps.tags.models import Tag; print('Total tags:', Tag.objects.count())"
# Expected: Total tags: 10 (same after second run)
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** `get_or_create` on `slug` — slug is unique, prevents duplicates on re-run
- **Type Safety:** `TagType.TIME` and `TagType.PROMOTION` constants — no magic strings
- **Style:** Consistent with existing seed pattern; `log_action` on every created tag (R5)
