# Quick Configuration Reference

## Most Common Updates

### 1. Add/Remove Stopwords
**File:** `data_config.py` - Lines 10-56

```python
STOPWORDS = {
    "articles": ['the', 'a', 'an', ...],
    # Add new category or append to existing
}

# Flattened set is auto-generated:
STOPWORDS_SET = set()
for category in STOPWORDS.values():
    STOPWORDS_SET.update(category)
```

**Example:** Add "said" to fillers
```python
"fillers": [
    'one', 'two', 'first', 'second', 'thing', 'way', 'time', 'day', 'year',
    'place', 'people', 'man', 'woman', 'person',
    'said', 'say', 'says', 'told', 'tell', 'tells', 'being', 'having', 'getting', 'making'
]
```

---

### 2. Change Toxicity Thresholds
**File:** `data_config.py` - Lines 178-182

```python
# Before:
TOXICITY_HIGH = 70         # Score >= 70 = high
TOXICITY_MEDIUM = 40       # Score >= 40 = medium

# After: Make detection stricter
TOXICITY_HIGH = 60         # Lower threshold = catch more toxic
TOXICITY_MEDIUM = 30
```

**Impact:** Affects all toxic link detection

---

### 3. Adjust Link Velocity Growth
**File:** `data_config.py` - Lines 132-133

```python
# Before: 5-15% monthly growth
LINK_VELOCITY_MIN_GROWTH = 0.05
LINK_VELOCITY_MAX_GROWTH = 0.15

# After: More aggressive target 10-20%
LINK_VELOCITY_MIN_GROWTH = 0.10
LINK_VELOCITY_MAX_GROWTH = 0.20
```

**Impact:** Changes link velocity calculations globally

---

### 4. Add Domain Name Pattern
**File:** `data_config.py` - Lines 63-87

Add words to lists:
```python
DOMAIN_ADJECTIVES = [
    'digital', 'smart', 'pro', 'best', 'top', 'perfect', 'ultimate', 'premium',
    'advanced', 'elite', 'expert', 'professional', 'trusted', 'leading', 'modern',
    'innovative', 'optimal', 'superior', 'dynamic', 'strategic',
    'quantum'  # NEW
]
```

---

### 5. Increase Competitor Analysis Detail
**File:** `data_config.py` - Line 216

```python
# Before: Analyze top 3 competitors
COMPETITORS_TO_ANALYZE = 3

# After: Analyze top 5 competitors
COMPETITORS_TO_ANALYZE = 5
```

---

### 6. Strict Spam Detection
**File:** `data_config.py` - Lines 100-115

Add new spam indicators:
```python
SPAM_INDICATORS = [
    "spam", "casino", "poker", "viagra", "pharma", "loan", "debt",
    "crypto", "forex", "trading", "xxx", "adult", "porn", "cheap",
    "free", "money", "weight loss", "dating", "escort",
    "mlm", "pyramid"  # NEW
]
```

---

## Configuration by Use Case

### For Stricter Link Quality Assessment
```python
# data_config.py
TOXICITY_HIGH = 50              # Line 181 - Catch more toxic links
DOMAIN_AUTHORITY_HIGH = 70      # Line 165 - Higher bar for "high"
TOXICITY_WEIGHTS['suspicious_domain'] = 60  # Line 200 - Heavier penalty
```

### For More Aggressive Link Building
```python
# data_config.py
LINK_VELOCITY_MAX_GROWTH = 0.25        # Line 133 - Allow 25% growth
VELOCITY_EXCELLENT_RATIO = 3           # Line 154 - 1 per 3 = excellent
AUTHORITY_WEIGHTS['low'] = 1.5         # Line 140 - Value low-auth more
```

### For Better Keyword Filtering
```python
# data_config.py
MIN_KEYWORD_LENGTH = 4                 # Line 122 - Longer = more meaningful
TOP_KEYWORDS_COUNT = 15                # Line 123 - Return more keywords
# And/or add more stopwords
```

### For Realistic Domain Generation
```python
# data_config.py
# Add industry-specific words
DOMAIN_ADJECTIVES.extend(['quantum', 'meta', 'neo', 'hyper'])
DOMAIN_NOUNS.extend(['labs', 'collective', 'syndicate', 'hub'])
DOMAIN_TLDS.extend(['ai', 'dev', 'app', 'cloud'])
```

---

## Import Pattern

Always import from `data_config.py`:

```python
# ✅ CORRECT
from data_config import STOPWORDS_SET, TOXICITY_HIGH

# ❌ WRONG - Don't hardcode values
STOPWORDS = {'the', 'a', 'an', ...}  # Don't do this!
TOXICITY_HIGH = 70                    # Don't do this!
```

---

## Testing Changes

After updating `data_config.py`:

```bash
# 1. Syntax check
python3 -m py_compile data_config.py

# 2. Quick test
python3 << 'EOF'
from data_config import STOPWORDS_SET
print(f"Stopwords: {len(STOPWORDS_SET)}")
EOF

# 3. Run tools test
python3 << 'EOF'
from tools import analyze_keyword_density
result = analyze_keyword_density(text="test text here")
print(result['top_keywords'])
EOF
```

---

## Key Files Map

| Purpose | File | Lines |
|---------|------|-------|
| Stopwords | `data_config.py` | 6-56 |
| Domain words | `data_config.py` | 60-87 |
| Spam detection | `data_config.py` | 91-115 |
| Keyword settings | `data_config.py` | 119-125 |
| Link velocity | `data_config.py` | 129-156 |
| Backlinks | `data_config.py` | 160-185 |
| HTTP settings | `data_config.py` | 189-200 |
| API limits | `data_config.py` | 204-211 |
| Competitor analysis | `data_config.py` | 215-230 |
| Functions | `tools.py` | All |

---

## Common Patterns

### Loop Through Config
```python
# Iterate all domain words
for adj in DOMAIN_ADJECTIVES:
    for noun in DOMAIN_NOUNS:
        domain = f"{adj}{noun}"

# Check toxicity weights
for category, weight in TOXICITY_WEIGHTS.items():
    print(f"{category}: {weight}")
```

### Conditional Based on Config
```python
if score >= TOXICITY_HIGH:
    severity = "high"
elif score >= TOXICITY_MEDIUM:
    severity = "medium"

if new_links >= total // VELOCITY_EXCELLENT_RATIO:
    rating = "excellent"
```

### Random Selection
```python
import random
domain = random.choice(DOMAIN_ADJECTIVES)
anchor = random.choice(QUALITY_ANCHOR_KEYWORDS)
confidence = random.uniform(COMPETITOR_CONFIDENCE_MEDIUM, COMPETITOR_CONFIDENCE_HIGH)
```

---

## Validation Checklist

After making configuration changes:

- [ ] File syntax is valid (`python3 -m py_compile`)
- [ ] All imports still work from `tools.py`
- [ ] Functions produce expected output
- [ ] No hardcoded values remain
- [ ] Configuration values are reasonable
- [ ] Documentation updated if needed

---

## Emergency Revert

If something breaks, revert to last working config:

```bash
# Check what changed
git diff data_config.py

# Revert to last commit
git checkout data_config.py

# Reload changes
python3 -m py_compile data_config.py
```

---

## Need More Details?

- **Full Documentation:** See `DATA_CONFIG_README.md`
- **Refactoring Summary:** See `CONFIG_REFACTORING_SUMMARY.md`
- **Function Code:** See `tools.py`
- **Usage Examples:** See test outputs above

---

**Last Updated:** December 8, 2025
