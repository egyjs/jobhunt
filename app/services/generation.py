from __future__ import annotations

import logging
from textwrap import dedent

from ..config import get_settings

logger = logging.getLogger(__name__)


class TailoredContentGenerator:
    """Generates resume highlights and cover letters using OpenAI when available."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        if self.settings.openai_api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self.settings.openai_api_key)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenAI client: %s", exc)
                self._client = None

    def resume_highlights(self, job_summary: str, profile_text: str) -> str:
        prompt = dedent(
            f"""
            Craft three bullet points highlighting the strongest alignment between the
            candidate profile and the following job description. Focus on measurable
            impact, Laravel/PHP expertise, and leadership traits when available.

            Job description:
            {job_summary}

            Candidate profile:
            {profile_text}
            """
        ).strip()
        return self._generate(prompt, fallback=self._fallback_resume(job_summary, profile_text))

    def cover_letter(self, job_title: str, company: str, job_summary: str, profile_text: str) -> str:
        prompt = dedent(
            f"""
            Draft a concise cover letter (<= 250 words) for the position "{job_title}" at
            "{company}". Use a confident, professional tone. Reference the candidate's key
            achievements and how they support the job requirements below.

            Job summary:
            {job_summary}

            Candidate profile:
            {profile_text}
            """
        ).strip()
        return self._generate(prompt, fallback=self._fallback_cover_letter(job_title, company, job_summary, profile_text))

    def _generate(self, prompt: str, fallback: str) -> str:
        if not self._client:
            return fallback
        try:
            response = self._client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=600,
            )
            content = response.output_text.strip()
            return content or fallback
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI generation failed: %s", exc)
            return fallback

    @staticmethod
    def _fallback_resume(job_summary: str, profile_text: str) -> str:
        return dedent(
            f"""
            - Delivered Laravel features relevant to: {job_summary[:120]}...
            - Applied core strengths ({profile_text[:120]}...) to meet role requirements.
            - Proven track record collaborating with cross-functional teams to ship web
              applications on time.
            """
        ).strip()

    @staticmethod
    def _fallback_cover_letter(job_title: str, company: str, job_summary: str, profile_text: str) -> str:
        return dedent(
            f"""
            Dear Hiring Team,

            I am excited to apply for the {job_title} role at {company}. My background combines
            hands-on Laravel delivery with leadership experience that mirrors your needs for:
            {job_summary[:150]}...

            Highlights from my profile: {profile_text[:150]}...

            I would welcome the opportunity to discuss how I can contribute from day one.

            Sincerely,
            JobApply Candidate
            """
        ).strip()


__all__ = ["TailoredContentGenerator"]
