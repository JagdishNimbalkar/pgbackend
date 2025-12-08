# Data Configuration Guide

## Overview

The `data_config.py` file contains all static data structures and configuration values used throughout the application. This centralized approach makes it easy to maintain, update, and test configuration changes without modifying core business logic in `tools.py`.

## File Structure

### 1. **Stopwords Configuration** 
**File:** `data_config.py` - Lines 6-56

Contains comprehensive English stopwords organized by grammatical category:
- **Articles** (13 words): the, a, an, this, that, etc.
- **Pronouns** (31 words): I, you, he, she, it, they, who, what, etc.
- **Auxiliaries** (24 words): is, am, are, be, been, do, have, can, will, etc.
- **Prepositions** (24 words): in, on, at, by, for, from, to, of, with, etc.
- **Conjunctions** (14 words): and, or, but, nor, yet, so, because, as, etc.
- **Adverbs** (24 words): not, no, yes, very, just, only, more, most, etc.
- **Common Fillers** (22 words): one, two, thing, way, time, day, said, etc.
- **Low-Value Words** (22 words): use, new, old, good, bad, same, different, etc.
- **Single Letters** (26 words): a-z

**Total:** 214 unique stopwords

**Usage in Code:**
```python
from data_config import STOPWORDS_SET

# In analyze_keyword_density()
filtered_words = [
    w for w in words 
    if w not in STOPWORDS_SET and len(w) >= MIN_KEYWORD_LENGTH
]
```

### 2. **Domain Generation Configuration**
**File:** `data_config.py` - Lines 60-87

Three lists used to generate realistic-looking domain names:

#### **DOMAIN_ADJECTIVES** (20 items)
Positive/professional descriptors used as domain prefixes:
```
digital, smart, pro, best, top, perfect, ultimate, premium, advanced, elite,
expert, professional, trusted, leading, modern, innovative, optimal, superior,
dynamic, strategic
```

#### **DOMAIN_NOUNS** (29 items)
Business-relevant nouns for domain names:
```
solutions, services, hub, central, studio, agency, tech, labs, media, group,
marketing, consulting, insights, analytics, strategy, content, web, digital,
online, resources, tools, platform, network, exchange, marketplace, directory,
portal, center, syndicate
```

#### **DOMAIN_TLDS** (16 items)
Realistic top-level domains:
```
com, net, org, co, io, info, biz, blog, site, online, tech, website, space,
work, news, guru
```

**Usage in Code:**
```python
def generate_realistic_domain():
    pattern = random.choice([
        lambda: f"{random.choice(DOMAIN_ADJECTIVES)}{random.choice(DOMAIN_NOUNS)}",
        lambda: f"{random.choice(DOMAIN_ADJECTIVES)}-{random.choice(DOMAIN_NOUNS)}",
        # ... other patterns
    ])
    domain_name = pattern()
    tld = random.choice(DOMAIN_TLDS)
    return f"{domain_name}.{tld}".lower()
```

**Example Outputs:**
- `optimalgroup.co`
- `leadingresources182.website`
- `advanced-strategy.work`
- `trusted-marketing.guru`

### 3. **Link Analysis Configuration**
**File:** `data_config.py` - Lines 91-115

#### **SPAM_INDICATORS** (19 items)
Keywords that suggest spammy/suspicious domains:
```
spam, casino, poker, viagra, pharma, loan, debt, crypto, forex, trading,
xxx, adult, porn, cheap, free, money, weight loss, dating, escort
```

#### **SUSPICIOUS_TLDS** (7 items)
TLDs commonly associated with low-quality sites:
```
.biz, .info, .tk, .ml, .ga, .cf, .gq
```

#### **GENERIC_ANCHORS** (9 items)
Non-descriptive anchor text that indicates low-quality links:
```
click here, read more, check this out, here, link, more info, learn more,
continue reading, view more
```

#### **QUALITY_ANCHOR_KEYWORDS** (15 items)
High-quality, descriptive anchor text for authority links:
```
best seo tools, digital marketing, seo guide, industry leader, seo services,
marketing tools, analytics platform, optimization guide, keyword research,
link building, content strategy, ppc management, social media marketing,
conversion optimization, web analytics
```

**Usage in Code:**
```python
# In detect_toxic_characteristics()
if any(indicator in domain_lower for indicator in SPAM_INDICATORS):
    toxicity_score += TOXICITY_WEIGHTS['suspicious_domain']

# In analyze_backlinks()
anchor_text = random.choice(QUALITY_ANCHOR_KEYWORDS)  # For high-authority
anchor_text = random.choice(GENERIC_ANCHORS)  # For low-authority
```

### 4. **Keyword Analysis Configuration**
**File:** `data_config.py` - Lines 119-125

```python
MIN_KEYWORD_LENGTH = 3              # Minimum characters for meaningful keywords
TOP_KEYWORDS_COUNT = 10             # Number of top keywords to return
```

**Usage:**
```python
filtered_words = [
    w for w in words 
    if w not in STOPWORDS_SET and len(w) >= MIN_KEYWORD_LENGTH
]
top_keywords = counter.most_common(TOP_KEYWORDS_COUNT)
```

### 5. **Link Velocity Configuration**
**File:** `data_config.py` - Lines 129-156

#### **Growth Rate Thresholds**
```python
LINK_VELOCITY_MIN_GROWTH = 0.05     # 5% minimum monthly growth
LINK_VELOCITY_MAX_GROWTH = 0.15     # 15% maximum monthly growth
```

#### **Authority Weighting**
```python
AUTHORITY_WEIGHTS = {
    'high': 3.0,       # DA 60+: 3x weight
    'medium': 1.5,     # DA 30-60: 1.5x weight
    'low': 1.0         # DA < 30: 1x weight
}
```

#### **Acceleration Thresholds**
```python
ACCELERATION_ACCELERATING = 20      # >20% = Strong growth
ACCELERATION_GROWING = 5            # >5% = Steady growth
ACCELERATION_SLOWING = -5           # <-5% = Declining
ACCELERATION_DECLINING = -20        # <-20% = Major decline
```

#### **Health Score Breakpoints**
```python
VELOCITY_STALLED_THRESHOLD = 1      # <1 new link = stalled
VELOCITY_EXCELLENT_RATIO = 5        # 1 new per 5 existing = excellent
VELOCITY_GOOD_RATIO = 10            # 1 new per 10 existing = good
```

**Usage:**
```python
monthly_growth_rate = random.uniform(
    LINK_VELOCITY_MIN_GROWTH, 
    LINK_VELOCITY_MAX_GROWTH
)
weighted_total = (
    high_auth_count * AUTHORITY_WEIGHTS['high'] +
    medium_auth_count * AUTHORITY_WEIGHTS['medium'] +
    low_auth_count * AUTHORITY_WEIGHTS['low']
)
```

### 6. **Backlink Analysis Configuration**
**File:** `data_config.py` - Lines 160-185

#### **Domain Authority Classification**
```python
DOMAIN_AUTHORITY_HIGH = 60           # DA >= 60 = High authority
DOMAIN_AUTHORITY_MEDIUM_MIN = 30     # DA 30-59 = Medium authority
DOMAIN_AUTHORITY_MEDIUM_MAX = 59
DOMAIN_AUTHORITY_LOW_MAX = 29        # DA < 30 = Low authority
```

#### **Link Type Distribution**
```python
LINK_TYPE_DISTRIBUTION = {
    'homepage': 0.30,        # 30% links from homepages
    'inner_pages': 0.50,     # 50% from inner pages
    'resource_links': 0.15,  # 15% from resource pages
    'blog_links': 0.05       # 5% from blog posts
}
```

#### **Toxicity Score Thresholds**
```python
TOXICITY_HIGH = 70         # Score >= 70 = High toxicity
TOXICITY_MEDIUM = 40       # Score 40-70 = Medium toxicity
TOXICITY_LOW = 20          # Score 20-40 = Low toxicity
```

#### **Toxicity Scoring Weights**
```python
TOXICITY_WEIGHTS = {
    'very_low_da': 40,           # DA < 10
    'low_da': 20,                # DA 10-20
    'suspicious_domain': 50,     # Contains spam keywords
    'suspicious_tld': 15,        # .biz, .info, etc.
    'keyword_stuffing': 20,      # Long anchor text
    'spam_keywords': 25,         # Viagra, casino, etc.
    'risky_page_type': 30,       # Forum, blog spam, etc.
    'generic_anchor': 15         # Click here, read more, etc.
}
```

### 7. **HTTP Configuration**
**File:** `data_config.py` - Lines 189-200

```python
DEFAULT_USER_AGENT = 'Mozilla/5.0...'  # Browser user agent for requests

# Request timeouts (in seconds)
REQUEST_TIMEOUT = 10                   # General HTTP requests
HEAD_REQUEST_TIMEOUT = 5               # HEAD requests for link checking
```

### 8. **API Configuration**
**File:** `data_config.py` - Lines 204-211

```python
BROKEN_LINK_CHECKER_LIMIT = 10         # Max links to check per page
MAX_EXTERNAL_DOMAINS = 10              # Max external domains in results
```

### 9. **Competitor Analysis Configuration**
**File:** `data_config.py` - Lines 215-230

```python
COMPETITORS_TO_ANALYZE = 3             # Number of competitors to analyze

# Confidence thresholds (0-1)
COMPETITOR_CONFIDENCE_HIGH = 0.85
COMPETITOR_CONFIDENCE_MEDIUM = 0.75
COMPETITOR_CONFIDENCE_LOW = 0.60

# Authority gap impact thresholds
AUTHORITY_GAP_HIGH_IMPACT = 15         # >15 links = high impact
AUTHORITY_GAP_MEDIUM_IMPACT = 5        # >5 links = medium impact

DOMAIN_DIVERSITY_HIGH_IMPACT = 50      # >50 domains = high impact
DOMAIN_DIVERSITY_MEDIUM_IMPACT = 20    # >20 domains = medium impact

DOFOLLOW_QUALITY_GAP_IMPACT = 5        # >5% ratio difference
```

---

## How to Update Configuration Values

### Example: Adjusting Keyword Filtering

**Before:**
```python
# Hard-coded in tools.py
stop_words = set(['the', 'a', 'an', ...])  # All 214 words listed inline
```

**After:**
```python
# In data_config.py
STOPWORDS_SET = set([...])

# In tools.py - imported from config
from data_config import STOPWORDS_SET, MIN_KEYWORD_LENGTH
filtered_words = [w for w in words if w not in STOPWORDS_SET]
```

### Example: Changing Domain Generation Pattern

To add new adjectives:
```python
# In data_config.py - update DOMAIN_ADJECTIVES
DOMAIN_ADJECTIVES = [
    'digital', 'smart', 'pro', 'best', 'top',
    # Add new ones here:
    'quantum', 'nexus', 'apex'
]
```

### Example: Adjusting Toxicity Thresholds

```python
# In data_config.py
TOXICITY_HIGH = 75         # Changed from 70
TOXICITY_WEIGHTS = {
    'very_low_da': 45,     # Changed from 40
    # ... other weights
}
```

---

## Testing Configuration Changes

After updating `data_config.py`, validate with:

```bash
# Syntax check
python3 -m py_compile data_config.py tools.py

# Run test
python3 << 'EOF'
from data_config import STOPWORDS_SET
print(f"Total stopwords: {len(STOPWORDS_SET)}")
EOF
```

---

## Benefits of Centralized Configuration

1. **Easy Maintenance** - All settings in one file
2. **No Code Changes** - Update behavior without touching logic
3. **A/B Testing** - Easy to test different config values
4. **Documentation** - Config values are self-documenting
5. **Reusability** - Multiple functions use same config
6. **Version Control** - Track config changes in git
7. **Quick Iteration** - Fast to tweak thresholds and lists

---

## Statistics

| Category | Count |
|----------|-------|
| Stopwords | 214 |
| Domain Adjectives | 20 |
| Domain Nouns | 29 |
| Domain TLDs | 16 |
| Spam Indicators | 19 |
| Suspicious TLDs | 7 |
| Generic Anchors | 9 |
| Quality Anchor Keywords | 15 |
| Toxicity Weight Categories | 8 |
| Configuration Parameters | 30+ |

---

## Related Files

- `tools.py` - Functions that use these configurations
- `main.py` - FastAPI endpoints that call tools
- `agent.py` - LangGraph agents that orchestrate tools

---

## Last Updated

December 8, 2025

Refactored from inline hardcoded values to external configuration management.
