from __future__ import annotations

import logging
import requests
from typing import Dict, Any
from uuid import UUID

from langchain_community.tools import DuckDuckGoSearchRun

from app.db.session import SessionLocal
from app.db.models.candidate_details import Candidate
from app.db.models.job_description import JobDescription
from app.db.models.candidate_application import CandidateApplication
from app.db.models.cv_score import CVScore
from app.db.models.skill_gap_report import SkillGapReportRecord
from app.ai.schema.agent_skill_gap import AgentSkillGapOutput

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Core Service Logic
# ---------------------------------------------------------------------------

def execute_market_search(query: str) -> str:
    """
    Business logic to search the web for current market trends.
    """
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        logger.error(f"Market search failed: {e}")
        return f"Search failed: {e}"

def execute_github_scan(repo_url: str, file_path: str = "") -> str:
    """
    Business logic to scan a public GitHub repository.
    """
    try:
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            return "Invalid GitHub URL."
        owner, repo = parts[-2], parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 404:
            return "File or repository not found. If package.json is missing, try searching for other files."
        
        if response.status_code != 200:
            return f"Failed to fetch from GitHub API: {response.status_code}"
            
        data = response.json()
        
        if isinstance(data, list):
            files = [item["name"] for item in data]
            return f"Directory contents: {', '.join(files)}"
            
        if isinstance(data, dict) and "download_url" in data and data["download_url"]:
            raw_response = requests.get(data["download_url"], timeout=5)
            if raw_response.status_code == 200:
                content = raw_response.text
                if len(content) > 3000:
                    return content[:3000] + "\\n...[TRUNCATED]..."
                return content
                
        return "Could not parse GitHub API response."
        
    except Exception as e:
        logger.error(f"GitHub scan failed: {e}")
        return f"GitHub scan failed: {e}"


def fetch_skill_gap_inputs(application_id: str) -> Dict[str, Any]:
    """
    Fetches the necessary data for the Skill Gap Agent to analyze.
    """
    try:
        parsed_uuid = UUID(application_id)
    except ValueError:
        raise ValueError(f"Invalid application UUID format: {application_id}")

    db = SessionLocal()
    try:
        # Get the application
        application = db.query(CandidateApplication).filter(
            CandidateApplication.id == parsed_uuid
        ).first()
        if not application:
            raise ValueError(f"No application found with ID {application_id}")

        # Get the candidate
        candidate = db.query(Candidate).filter(
            Candidate.id == application.candidate_id
        ).first()
        if not candidate:
            raise ValueError(f"No candidate found with ID {application.candidate_id}")

        # Get the job description
        job = db.query(JobDescription).filter(
            JobDescription.id == application.job_id
        ).first()
        if not job or not job.structured_output:
            raise ValueError(f"No job description or rubric found for job ID {application.job_id}")

        # Get the CV Score weaknesses (latest version)
        cv_score = db.query(CVScore).filter(
            CVScore.candidate_id == candidate.id,
            CVScore.job_id == job.id
        ).order_by(CVScore.version.desc()).first()
        
        weaknesses = cv_score.weaknesses if cv_score and cv_score.weaknesses else []

        return {
            "application_id": str(application.id),
            "candidate_id": str(candidate.id),
            "job_id": str(job.id),
            "must_have_skills": job.structured_output.get("must_have_skills", []),
            "nice_to_have_skills": job.structured_output.get("nice_to_have_skills", []),
            "github_url": candidate.github_url,
            "work_experience": candidate.work_experience or [],
            "projects": candidate.projects or [],
            "claimed_skills": candidate.skills or {},
            "cv_score_weaknesses": weaknesses,
            "cv_text": candidate.cv_text,
        }
    finally:
        db.close()


def store_skill_gap_report(
    application_id: str,
    job_id: str,
    candidate_id: str,
    agent_output: AgentSkillGapOutput,
    scoring_model: str = "unknown",
) -> Dict[str, Any]:
    """
    Persists the Skill Gap Agent output to the skill_gap_report table.
    Overwrites the existing report for this application if it exists.
    """
    try:
        parsed_application_id = UUID(application_id)
        parsed_job_id = UUID(job_id)
        parsed_candidate_id = UUID(candidate_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID format: {e}")

    db = SessionLocal()
    try:
        # Check for existing report for this application
        existing = db.query(SkillGapReportRecord).filter(
            SkillGapReportRecord.application_id == parsed_application_id
        ).first()

        if existing:
            # Update existing
            existing.gaps = [gap.model_dump() for gap in agent_output.gaps]
            existing.impact_score = agent_output.impact_score
            existing.summary = agent_output.summary
            existing.analyzed_by = "skill_gap_agent"
            existing.analysis_model = scoring_model
            report = existing
        else:
            # Create new
            report = SkillGapReportRecord(
                application_id=parsed_application_id,
                job_id=parsed_job_id,
                candidate_id=parsed_candidate_id,
                gaps=[gap.model_dump() for gap in agent_output.gaps],
                impact_score=agent_output.impact_score,
                summary=agent_output.summary,
                analyzed_by="skill_gap_agent",
                analysis_model=scoring_model,
            )
            db.add(report)

        db.commit()
        db.refresh(report)

        return {
            "report_id": str(report.id),
            "application_id": str(report.application_id),
            "impact_score": report.impact_score,
            "status": "success",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store skill gap report: {e}")
        raise
    finally:
        db.close()
