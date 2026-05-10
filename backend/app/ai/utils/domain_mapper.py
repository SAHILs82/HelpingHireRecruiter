import re

# Keyword mapping to the exact domain keys used in the dynamic_llm_prompts table.
DOMAIN_MAPPINGS = {
    # Technical
    "technical_software_engineer": ["software", "developer", "engineer", "backend", "frontend", "fullstack", "react", "node", "java", "python dev"],
    "technical_data_science": ["data science", "data scientist", "machine learning", "ai engineer", "data analyst", "nlp", "computer vision"],
    "technical_devops_cloud": ["devops", "cloud", "aws", "azure", "gcp", "site reliability", "sre", "infrastructure"],
    "technical_product_manager": ["product manager", "product owner", "pm"],
    "technical_ui_ux_designer": ["ui/ux", "designer", "user experience", "user interface", "product designer"],
    "technical_cyber_security": ["security", "cyber", "penetration", "infosec", "soc"],

    # Non-Technical
    "non_technical_sales": ["sales", "account executive", "business development", "sdr", "bdr", "revenue"],
    "non_technical_marketing": ["marketing", "seo", "content", "social media", "brand", "growth"],
    "non_technical_hr_people_ops": ["hr", "human resources", "people ops", "recruiter", "talent acquisition"],
    "non_technical_finance_accounts": ["finance", "accountant", "accounting", "cpa", "financial analyst", "controller"],
    "non_technical_operations": ["operations", "logistics", "supply chain", "chief operating"],
    "non_technical_customer_support": ["customer support", "customer success", "support agent", "helpdesk"],

    # Domain Specific
    "domain_health_care": ["health", "medical", "doctor", "nurse", "clinical", "hospital", "pharma"],
    "domain_legal": ["legal", "lawyer", "attorney", "paralegal", "counsel", "compliance"],
    "domain_education": ["education", "teacher", "professor", "instructional", "curriculum", "tutor", "edtech"],
    "domain_manufacturing": ["manufacturing", "factory", "plant", "production", "assembly"],
    "domain_retail_ecommerce": ["retail", "ecommerce", "store manager", "merchandiser", "shopify"],
    "domain_media_creative": ["media", "creative", "video", "editor", "writer", "journalist", "copywriter"]
}

def map_to_variant_key(role_or_domain: str) -> str:
    """
    Takes a free-form string (like a role title or domain) and attempts to match it
    to one of our highly specialized prompt keys.
    Returns the mapped key appended with '_system' (e.g. 'technical_software_engineer_system')
    or falls back to 'system'.
    """
    if not role_or_domain:
        return "system"
        
    normalized = role_or_domain.lower()
    
    for domain_key, keywords in DOMAIN_MAPPINGS.items():
        for keyword in keywords:
            # Check for word boundary matches to avoid partial match bugs (e.g. 'hr' matching 'chrome')
            if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                return f"{domain_key}_system"
                
    # If no match found, fallback to the default 'system' prompt
    return "system"
