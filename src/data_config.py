"""
Data Configuration File
Contains all static data structures used throughout the application.
This file is designed to be easily maintainable and updatable.
"""

# ============================================================================
# STOPWORDS CONFIGURATION
# ============================================================================
# Comprehensive English stopwords list - filters common words that don't provide keyword insights
STOPWORDS = {
    # Articles & Determiners (9 items)
    "articles": [
        'the', 'a', 'an', 'this', 'that', 'these', 'those', 'some', 'any', 'all', 'each', 'every', 'other'
    ],
    
    # Pronouns (31 items)
    "pronouns": [
        'i', 'me', 'my', 'mine', 'myself',
        'we', 'us', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself',
        'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves',
        'who', 'whom', 'whose', 'what', 'which', 'whoever', 'whomever', 'whatever', 'whichever'
    ],
    
    # Auxiliary Verbs & Common Verbs (24 items)
    "auxiliaries": [
        'is', 'am', 'are', 'was', 'were', 'be', 'being', 'been',
        'do', 'does', 'did', 'doing',
        'have', 'has', 'had', 'having',
        'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'ought'
    ],
    
    # Prepositions (24 items)
    "prepositions": [
        'in', 'on', 'at', 'by', 'for', 'from', 'to', 'of', 'with', 'without',
        'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'into', 'out', 'up', 'down', 'over', 'under',
        'near', 'about'
    ],
    
    # Conjunctions & Connectors (12 items)
    "conjunctions": [
        'and', 'or', 'but', 'nor', 'yet', 'so', 'because', 'as', 'if', 'unless', 'when', 'where', 'while', 'until'
    ],
    
    # Adverbs & Modifiers (24 items)
    "adverbs": [
        'not', 'no', 'yes', 'very', 'just', 'only', 'more', 'most', 'less', 'least',
        'also', 'too', 'so', 'then', 'now', 'here', 'there',
        'how', 'why', 'when', 'where',
        'almost', 'already', 'always', 'never', 'ever', 'still'
    ],
    
    # Common Nouns & Filler Words (22 items)
    "fillers": [
        'one', 'two', 'first', 'second', 'thing', 'way', 'time', 'day', 'year',
        'place', 'people', 'man', 'woman', 'person',
        'said', 'say', 'says', 'told', 'tell', 'tells',
        'being', 'having', 'getting', 'making'
    ],
    
    # Numbers and Common Low-Value Words (22 items)
    "common_words": [
        'etc', 'amp', 'nbsp', 'quot', 'apos',
        'use', 'used', 'using',
        'new', 'old', 'good', 'bad', 'best', 'worst',
        'same', 'different', 'like', 'unlike', 'such',
        'even', 'own', 'many', 'several', 'few', 'much'
    ],
    
    # Single Letters & Common Abbreviations (26 items)
    "single_letters": [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
    ]
}

# Flattened set for quick lookup
STOPWORDS_SET = set()
for category in STOPWORDS.values():
    STOPWORDS_SET.update(category)

# ============================================================================
# DOMAIN GENERATION CONFIGURATION
# ============================================================================

# Adjectives for realistic domain names (20 items)
DOMAIN_ADJECTIVES = [
    'digital', 'smart', 'pro', 'best', 'top', 'perfect', 'ultimate', 'premium',
    'advanced', 'elite', 'expert', 'professional', 'trusted', 'leading', 'modern',
    'innovative', 'optimal', 'superior', 'dynamic', 'strategic'
]

# Business nouns for realistic domain names (26 items)
DOMAIN_NOUNS = [
    'solutions', 'services', 'hub', 'central', 'studio', 'agency', 'tech', 'labs',
    'media', 'group', 'marketing', 'consulting', 'insights', 'analytics', 'strategy',
    'content', 'web', 'digital', 'online', 'resources', 'tools', 'platform', 'network',
    'exchange', 'marketplace', 'directory', 'portal', 'center', 'syndicate'
]

# Real TLDs for realistic domains (16 items)
DOMAIN_TLDS = [
    'com', 'net', 'org', 'co', 'io', 'info', 'biz', 'blog', 'site', 'online',
    'tech', 'website', 'space', 'work', 'news', 'guru'
]

# Domain generation patterns (5 patterns)
DOMAIN_PATTERNS = [
    'simple',        # adjective + noun
    'hyphenated',    # adjective-noun
    'compound',      # noun + noun
    'numbered',      # adjective + noun + number
    'single'         # single noun
]

# ============================================================================
# LINK ANALYSIS CONFIGURATION
# ============================================================================

# Spam indicators for toxic link detection
SPAM_INDICATORS = [
    "spam", "casino", "poker", "viagra", "pharma", "loan", "debt",
    "crypto", "forex", "trading", "xxx", "adult", "porn", "cheap",
    "free", "money", "weight loss", "dating", "escort"
]

# Suspicious TLDs
SUSPICIOUS_TLDS = [
    ".biz", ".info", ".tk", ".ml", ".ga", ".cf", ".gq"
]

# Generic/manipulative anchor text (low-quality link indicators)
GENERIC_ANCHORS = [
    "click here", "read more", "check this out", "here", "link",
    "more info", "learn more", "continue reading", "view more"
]

# High-quality anchor text examples for reference
QUALITY_ANCHOR_KEYWORDS = [
    "best seo tools", "digital marketing", "seo guide", "industry leader",
    "seo services", "marketing tools", "analytics platform", "optimization guide",
    "keyword research", "link building", "content strategy", "ppc management",
    "social media marketing", "conversion optimization", "web analytics"
]

# ============================================================================
# KEYWORD ANALYSIS CONFIGURATION
# ============================================================================

# Minimum word length for meaningful keywords (in characters)
MIN_KEYWORD_LENGTH = 3

# Number of top keywords to return
TOP_KEYWORDS_COUNT = 10

# ============================================================================
# PAGE SPEED CONFIGURATION
# ============================================================================

# Performance thresholds (in milliseconds)
SPEED_GOOD_THRESHOLD = 800      # < 800ms = Good
SPEED_WARNING_THRESHOLD = 2000  # > 2000ms = Needs Improvement

# Page size threshold (in KB)
PAGE_SIZE_WARNING = 2000  # > 2000KB = Large page

# ============================================================================
# LINK VELOCITY CONFIGURATION
# ============================================================================

# Sustainable monthly growth rate (as percentage)
LINK_VELOCITY_MIN_GROWTH = 0.05   # 5%
LINK_VELOCITY_MAX_GROWTH = 0.15   # 15%

# Authority weighting for velocity calculation
AUTHORITY_WEIGHTS = {
    'high': 3.0,      # DA 60+
    'medium': 1.5,    # DA 30-60
    'low': 1.0        # DA < 30
}

# Acceleration thresholds for velocity trend detection
ACCELERATION_ACCELERATING = 20     # > 20% acceleration
ACCELERATION_GROWING = 5           # > 5% acceleration
ACCELERATION_SLOWING = -5          # < -5% acceleration
ACCELERATION_DECLINING = -20       # < -20% acceleration

# Velocity health score breakpoints
VELOCITY_STALLED_THRESHOLD = 1     # Less than 1 link in 30 days
VELOCITY_EXCELLENT_RATIO = 5       # 1 new link per 5 existing
VELOCITY_GOOD_RATIO = 10           # 1 new link per 10 existing

# ============================================================================
# BACKLINK ANALYSIS CONFIGURATION
# ============================================================================

# Domain authority classification
DOMAIN_AUTHORITY_HIGH = 60
DOMAIN_AUTHORITY_MEDIUM_MIN = 30
DOMAIN_AUTHORITY_MEDIUM_MAX = 59
DOMAIN_AUTHORITY_LOW_MAX = 29

# Link type distribution (percentage of total referring domains)
LINK_TYPE_DISTRIBUTION = {
    'homepage': 0.30,
    'inner_pages': 0.50,
    'resource_links': 0.15,
    'blog_links': 0.05
}

# Toxicity score thresholds
TOXICITY_HIGH = 70
TOXICITY_MEDIUM = 40
TOXICITY_LOW = 20

# Toxicity scoring weights
TOXICITY_WEIGHTS = {
    'very_low_da': 40,           # DA < 10
    'low_da': 20,                # DA 10-20
    'suspicious_domain': 50,     # Contains spam keywords
    'suspicious_tld': 15,        # .biz, .info, etc.
    'keyword_stuffing': 20,      # Long anchor text
    'spam_keywords': 25,         # Viagra, casino, etc.
    'risky_page_type': 30,       # Comment, forum, blog spam
    'generic_anchor': 15         # Click here, read more, etc.
}

# ============================================================================
# USER AGENT FOR WEB REQUESTS
# ============================================================================

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Request timeouts (in seconds)
REQUEST_TIMEOUT = 10
HEAD_REQUEST_TIMEOUT = 5

# Maximum links to check in broken link checker
BROKEN_LINK_CHECKER_LIMIT = 10

# Maximum external domains to return in backlink extraction
MAX_EXTERNAL_DOMAINS = 10

# ============================================================================
# COMPETITOR ANALYSIS CONFIGURATION
# ============================================================================

# Number of competitors to analyze
COMPETITORS_TO_ANALYZE = 3

# Competitor detection confidence thresholds
COMPETITOR_CONFIDENCE_HIGH = 0.85
COMPETITOR_CONFIDENCE_MEDIUM = 0.75
COMPETITOR_CONFIDENCE_LOW = 0.60

# Authority gap detection thresholds
AUTHORITY_GAP_HIGH_IMPACT = 15      # More than 15 high-authority links difference
AUTHORITY_GAP_MEDIUM_IMPACT = 5     # More than 5 high-authority links difference

DOMAIN_DIVERSITY_HIGH_IMPACT = 50   # More than 50 referring domains difference
DOMAIN_DIVERSITY_MEDIUM_IMPACT = 20 # More than 20 referring domains difference

DOFOLLOW_QUALITY_GAP_IMPACT = 5     # More than 5% dofollow ratio difference

# ============================================================================
# SITEMAP & LINK CATEGORIZATION CONFIGURATION
# ============================================================================

# Link categories for classification
LINK_CATEGORIES = {
    'navigation': {
        'keywords': ['home', 'about', 'contact', 'menu', 'nav', 'header', 'footer', 'sitemap'],
        'description': 'Navigation and menu links'
    },
    'ecommerce': {
        'keywords': ['shop', 'store', 'cart', 'checkout', 'buy', 'purchase', 'order', 'product', 'products', 'item', 'items'],
        'description': 'E-commerce and shopping links'
    },
    'product': {
        'keywords': ['product', 'item', 'catalog', 'inventory', 'merchandise', 'goods', 'sku'],
        'description': 'Product pages and listings'
    },
    'account': {
        'keywords': ['login', 'signup', 'register', 'account', 'profile', 'dashboard', 'settings', 'logout', 'signin'],
        'description': 'User account and authentication links'
    },
    'support': {
        'keywords': ['help', 'support', 'faq', 'documentation', 'docs', 'tutorial', 'guide', 'contact', 'service'],
        'description': 'Support and help resources'
    },
    'social': {
        'keywords': ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok', 'reddit', 'social', 'share'],
        'description': 'Social media links'
    },
    'legal': {
        'keywords': ['privacy', 'terms', 'disclaimer', 'legal', 'cookie', 'policy', 'gdpr', 'compliance', 'license'],
        'description': 'Legal and policy pages'
    },
    'content': {
        'keywords': ['blog', 'article', 'post', 'news', 'story', 'press', 'magazine', 'publication'],
        'description': 'Blog and content pages'
    },
    'business': {
        'keywords': ['pricing', 'plans', 'features', 'case-study', 'resources', 'solutions', 'enterprise', 'demo'],
        'description': 'Business and marketing pages'
    },
    'careers': {
        'keywords': ['career', 'careers', 'jobs', 'hiring', 'employment', 'work', 'join', 'team', 'vacancy'],
        'description': 'Career and job opportunity links'
    },
    'external': {
        'keywords': [],  # Will be determined by domain check
        'description': 'External third-party links'
    },
    'media': {
        'keywords': ['image', 'video', 'pdf', 'download', 'media', 'gallery', 'photo', 'audio', 'file'],
        'description': 'Media and downloadable content'
    },
    'utility': {
        'keywords': ['search', 'filter', 'tag', 'category', 'archive', 'rss', 'feed', 'print', 'email'],
        'description': 'Utility and functional pages'
    }
}

# Sitemap processing configuration
SITEMAP_MAX_URLS = 1000  # Maximum URLs to process from sitemap
SITEMAP_TIMEOUT = 30      # Timeout for sitemap fetching
MAX_PAGES_TO_CRAWL = 50   # Maximum pages to crawl from sitemap
CRAWL_TIMEOUT = 10        # Timeout per page crawl
