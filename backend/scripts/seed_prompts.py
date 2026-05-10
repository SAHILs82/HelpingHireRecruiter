import asyncio
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.dynamic_llm_prompts import DynamicLLMPrompt
from app.core.llm_prompt_keys import LLM_USE_CASE_JD_GENERATOR, LLM_USE_CASE_CV_SCORER, LLM_USE_CASE_JD_PARSER

# --- DOMAIN INTELLIGENCE DEFINITIONS ---
# Instead of hardcoded examples, we give the LLM deep analytical frameworks for each domain.

DOMAINS = {
    # TECHNICAL
    "technical_software_engineer": {
        "focus": "software engineering, system architecture, and code quality",
        "key_metrics": "Scalability, Maintainability, Test Coverage, Algorithmic efficiency, System Design",
        "core_frameworks": "Agile/Scrum, CI/CD pipelines, Version Control (Git), Code Reviews",
        "scoring_priority": "Prioritize production experience, system design decisions, and understanding of trade-offs over mere syntax knowledge."
    },
    "technical_data_science": {
        "focus": "statistical modeling, machine learning algorithms, and data pipelines",
        "key_metrics": "Model Accuracy (F1, RMSE, etc.), Data Quality, Feature Engineering, Business Impact of Models",
        "core_frameworks": "CRISP-DM, Model Deployment (MLOps), A/B Testing, Data Governance",
        "scoring_priority": "Prioritize ability to deploy models to production, understanding of statistical assumptions, and business value generation."
    },
    "technical_devops_cloud": {
        "focus": "infrastructure as code, CI/CD, cloud architecture, and system reliability",
        "key_metrics": "Uptime (SLAs/SLOs), Deployment Frequency, Mean Time to Recovery (MTTR), Infrastructure Cost Optimization",
        "core_frameworks": "Infrastructure as Code (IaC), Containerization & Orchestration, GitOps, Site Reliability Engineering (SRE)",
        "scoring_priority": "Prioritize automated infrastructure management, security-first mindset, and experience with high-availability systems."
    },
    "technical_product_manager": {
        "focus": "product strategy, user-centric design, roadmap execution, and cross-functional leadership",
        "key_metrics": "User Adoption/Retention, Time-to-Market, Net Promoter Score (NPS), Revenue Impact",
        "core_frameworks": "Agile/Scrum, Lean Startup, PRDs/User Stories, Go-to-Market Strategy",
        "scoring_priority": "Prioritize data-driven decision making, stakeholder alignment, and demonstrated impact on product metrics."
    },
    "technical_ui_ux_designer": {
        "focus": "user experience research, interface design, prototyping, and design systems",
        "key_metrics": "Task Success Rate, User Engagement, Accessibility Compliance, Design System Adoption",
        "core_frameworks": "Human-Computer Interaction (HCI), Wireframing/Prototyping, Usability Testing, Responsive Design",
        "scoring_priority": "Prioritize portfolio quality, user research methodologies, and ability to translate complex flows into intuitive interfaces."
    },
    "technical_cyber_security": {
        "focus": "threat modeling, incident response, compliance, and secure architecture",
        "key_metrics": "Mean Time to Detect (MTTD), Mean Time to Respond (MTTR), Vulnerability Patch Rate",
        "core_frameworks": "Zero Trust Architecture, OWASP Top 10, NIST/ISO 27001, Penetration Testing",
        "scoring_priority": "Prioritize proactive threat hunting, deep network/system knowledge, and experience with regulatory compliance."
    },

    # NON-TECHNICAL
    "non_technical_sales": {
        "focus": "revenue generation, pipeline management, client acquisition, and negotiation",
        "key_metrics": "Quota Attainment, Conversion Rate, Average Deal Size, Sales Cycle Length",
        "core_frameworks": "B2B/B2C Sales Methodologies (MEDDIC, SPIN, etc.), CRM Management, Forecasting",
        "scoring_priority": "Prioritize proven track records of quota over-achievement, complex deal negotiation, and territory management."
    },
    "non_technical_marketing": {
        "focus": "brand awareness, lead generation, market positioning, and campaign ROI",
        "key_metrics": "Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), Conversion Rate, Brand Engagement",
        "core_frameworks": "SEO/SEM, Content Strategy, Performance Marketing, Market Segmentation",
        "scoring_priority": "Prioritize data-driven campaign optimization, audience understanding, and multi-channel marketing experience."
    },
    "non_technical_hr_people_ops": {
        "focus": "talent acquisition, employee retention, organizational development, and compliance",
        "key_metrics": "Time-to-Hire, Employee Turnover Rate, eNPS (Employee Net Promoter Score), Diversity Metrics",
        "core_frameworks": "Talent Lifecycle Management, Employment Law/Compliance, Performance Management",
        "scoring_priority": "Prioritize strategic workforce planning, culture building, and experience in scaling teams effectively."
    },
    "non_technical_finance_accounts": {
        "focus": "financial planning, risk management, regulatory compliance, and capital allocation",
        "key_metrics": "EBITDA, Cash Flow Variance, ROI, Working Capital Ratio",
        "core_frameworks": "GAAP/IFRS Standards, Financial Modeling (FP&A), Audit/Compliance, Tax Strategy",
        "scoring_priority": "Prioritize analytical rigor, experience with complex financial modeling, and strict adherence to regulatory standards."
    },
    "non_technical_operations": {
        "focus": "process optimization, supply chain management, resource allocation, and efficiency",
        "key_metrics": "Operating Margin, Resource Utilization, Process Cycle Time, Cost Reduction",
        "core_frameworks": "Six Sigma/Lean, Supply Chain Logistics, Vendor Management, OKR Tracking",
        "scoring_priority": "Prioritize ability to scale processes, eliminate bottlenecks, and manage cross-departmental workflows."
    },
    "non_technical_customer_support": {
        "focus": "customer satisfaction, issue resolution, client onboarding, and retention",
        "key_metrics": "CSAT/NPS, First Contact Resolution (FCR), Average Handling Time (AHT), Churn Rate",
        "core_frameworks": "Helpdesk Ticketing, Knowledge Base Management, De-escalation Techniques",
        "scoring_priority": "Prioritize empathy, rapid problem-solving, and ability to handle high-pressure customer interactions."
    },

    # DOMAIN SPECIFIC
    "domain_health_care": {
        "focus": "patient care, clinical operations, medical compliance, and health informatics",
        "key_metrics": "Patient Outcomes, Readmission Rates, Operational Efficiency, Compliance Audit Scores",
        "core_frameworks": "HIPAA/GDPR Compliance, Electronic Medical Records (EMR), Clinical Protocols",
        "scoring_priority": "Prioritize deep understanding of healthcare regulations, patient safety, and cross-functional clinical collaboration."
    },
    "domain_legal": {
        "focus": "risk mitigation, contract negotiation, regulatory compliance, and litigation",
        "key_metrics": "Contract Turnaround Time, Litigation Success Rate, Compliance Audit Results",
        "core_frameworks": "Corporate Governance, Intellectual Property Law, Dispute Resolution",
        "scoring_priority": "Prioritize attention to detail, strong negotiation skills, and ability to translate complex law into business strategy."
    },
    "domain_education": {
        "focus": "curriculum development, student engagement, learning outcomes, and edtech integration",
        "key_metrics": "Student Retention/Graduation Rates, Assessment Scores, Engagement Metrics",
        "core_frameworks": "Pedagogical Theory, Instructional Design, EdTech Platforms (LMS), Special Education",
        "scoring_priority": "Prioritize ability to design inclusive learning experiences and measurable improvements in student outcomes."
    },
    "domain_manufacturing": {
        "focus": "production efficiency, quality control, supply chain logistics, and safety",
        "key_metrics": "Overall Equipment Effectiveness (OEE), Defect Rate, Inventory Turnover, Incident Rate",
        "core_frameworks": "Lean Manufacturing, Total Quality Management (TQM), OSHA Safety Standards",
        "scoring_priority": "Prioritize experience with continuous improvement, facility safety, and optimizing production yields."
    },
    "domain_retail_ecommerce": {
        "focus": "omnichannel sales, inventory management, customer experience, and merchandising",
        "key_metrics": "Cart Abandonment Rate, Customer Lifetime Value (CLV), Inventory Turnover, GMV",
        "core_frameworks": "E-commerce Platforms (Shopify, Magento), Supply Chain Logistics, Merchandising Strategy",
        "scoring_priority": "Prioritize understanding of consumer behavior, digital conversion optimization, and supply chain efficiency."
    },
    "domain_media_creative": {
        "focus": "content creation, audience engagement, brand storytelling, and multimedia production",
        "key_metrics": "Audience Reach/Engagement, Production Timeline Adherence, Content ROI",
        "core_frameworks": "Digital Content Strategy, Post-Production Workflows, Copyright/Licensing",
        "scoring_priority": "Prioritize portfolio strength, original conceptual thinking, and ability to deliver across diverse media formats."
    }
}

# --- PROMPT TEMPLATES ---

JD_GENERATOR_TEMPLATE = """\
You are an elite Human Resources analyst and recruiter specializing deeply in the {domain_key} sector.
Your expertise lies heavily in {focus}.

Your objective is to generate a comprehensive, production-ready job description based on a structured HR intake form.

────────────────────────────────────────────
DOMAIN INTELLIGENCE & EVALUATION CRITERIA
────────────────────────────────────────────
When interpreting the intake form, you MUST apply the following domain-specific standards:
1. CORE METRICS: Ensure the job description reflects accountability for: {key_metrics}.
2. FRAMEWORKS: Naturally integrate the expectation of proficiency in: {core_frameworks}.
3. IDEAL CANDIDATE PROFILE: The responsibilities and requirements must align with this core priority: {scoring_priority}.

────────────────────────────────────────────
INSTRUCTIONS
────────────────────────────────────────────
1. DO NOT rely on generic filler text. Use precise, industry-standard terminology appropriate for {domain_key}.
2. Infer necessary foundational skills, tools, and methodologies that are mandatory for this role, even if the recruiter omitted them.
3. Determine the seniority level based on the experience years and structure the tone accordingly.
4. Output MUST be valid JSON mapping perfectly to the JDGeneratorResponse schema.

Ensure the "must_have_skills" and "nice_to_have_skills" strictly differentiate between fundamental domain knowledge and specialized bonus skills.
"""

CV_SCORER_TEMPLATE = """\
You are an elite Technical Recruiter and Hiring Manager evaluating candidates for a role in the {domain_key} sector.
You possess a deep, rigorous understanding of {focus}.

Your objective is to evaluate a candidate's parsed CV against the requirements of a Job Description, producing a highly accurate JSON score.

────────────────────────────────────────────
DOMAIN EVALUATION LENS
────────────────────────────────────────────
You must evaluate the candidate through the strict lens of this domain:
1. KEY METRIC EVIDENCE: Look for quantifiable impact related to: {key_metrics}. If a candidate only lists responsibilities without impact, score them lower.
2. FRAMEWORK FLUENCY: Verify actual, contextual usage of: {core_frameworks}. Just listing a keyword is not enough; look for application.
3. ULTIMATE PRIORITY: Above all, prioritize candidates who demonstrate: {scoring_priority}.

────────────────────────────────────────────
SCORING INSTRUCTIONS
────────────────────────────────────────────
1. Be ruthless but fair. Do not award high scores for basic keyword matching. Evaluate the DEPTH of experience.
2. Cross-reference the candidate's project descriptions to validate their claimed skills.
3. Ensure your 'reasoning' strictly references evidence found in the CV text. Avoid assumptions.
4. Your output MUST be strict JSON matching the CVScoringResponse schema.
"""

JD_PARSER_TEMPLATE = """\
You are an expert HR Data Extraction Specialist focusing on the {domain_key} sector.
Your core competency is understanding the nuances of {focus}.

Your objective is to extract structured parameters from raw, conversational recruiter notes or rough job intake drafts.

────────────────────────────────────────────
DOMAIN CONTEXT
────────────────────────────────────────────
When extracting data, be aware that recruiters in this domain prioritize: {scoring_priority}.
Watch for implicit references to standard tools and frameworks such as: {core_frameworks}.

────────────────────────────────────────────
EXTRACTION RULES
────────────────────────────────────────────
1. Extract the Title, Level, Experience Range, and key Skills from the raw text.
2. If a skill is mentioned via an acronym standard to this domain, normalize it.
3. Identify implicit constraints (e.g., if the text implies a senior role, set the minimum experience appropriately).
4. Output MUST be valid JSON matching the exact expected schema. Do not include markdown formatting.
"""

def seed_prompts():
    db: Session = SessionLocal()
    
    print("Starting database seeding for Dynamic LLM Prompts...")
    
    # 1. Clear existing prompts to avoid duplicates if re-running
    # Note: the unique constraint handles this, but doing an upsert or clearing is safer for development.
    db.query(DynamicLLMPrompt).delete()
    db.commit()

    prompts_to_add = []
    
    for domain_key, intelligence in DOMAINS.items():
        # Prepare the formatted prompts
        jd_gen_text = JD_GENERATOR_TEMPLATE.format(
            domain_key=domain_key.replace("_", " ").title(),
            focus=intelligence["focus"],
            key_metrics=intelligence["key_metrics"],
            core_frameworks=intelligence["core_frameworks"],
            scoring_priority=intelligence["scoring_priority"]
        )
        
        cv_score_text = CV_SCORER_TEMPLATE.format(
            domain_key=domain_key.replace("_", " ").title(),
            focus=intelligence["focus"],
            key_metrics=intelligence["key_metrics"],
            core_frameworks=intelligence["core_frameworks"],
            scoring_priority=intelligence["scoring_priority"]
        )
        
        jd_parse_text = JD_PARSER_TEMPLATE.format(
            domain_key=domain_key.replace("_", " ").title(),
            focus=intelligence["focus"],
            key_metrics=intelligence["key_metrics"],
            core_frameworks=intelligence["core_frameworks"],
            scoring_priority=intelligence["scoring_priority"]
        )

        # Append to batch list
        prompts_to_add.extend([
            DynamicLLMPrompt(
                use_case=LLM_USE_CASE_JD_GENERATOR,
                variant_key=f"{domain_key}_system",
                prompt_body=jd_gen_text,
                is_active=True
            ),
            DynamicLLMPrompt(
                use_case=LLM_USE_CASE_CV_SCORER,
                variant_key=f"{domain_key}_system",
                prompt_body=cv_score_text,
                is_active=True
            ),
            DynamicLLMPrompt(
                use_case=LLM_USE_CASE_JD_PARSER,
                variant_key=f"{domain_key}_system",
                prompt_body=jd_parse_text,
                is_active=True
            )
        ])
    
    # Bulk insert
    try:
        db.bulk_save_objects(prompts_to_add)
        db.commit()
        print(f"Successfully seeded {len(prompts_to_add)} dynamic prompts.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed prompts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_prompts()
