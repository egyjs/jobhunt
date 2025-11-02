"""LLM helpers for tailoring application materials."""

from __future__ import annotations

import asyncio
from typing import Any

from openai import OpenAI


class AITextGenerator:
    """Wrapper around OpenAI responses API with graceful fallback."""

    def __init__(self, api_key: str | None, model: str, temperature: float = 0.2) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return self._client is not None

    async def generate(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str | None:
        if not self._client:
            return None
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        if response.choices:
            return response.choices[0].message.content
        return None

    async def resume_bullets(self, resume: str, job_description: str) -> str:
        system_prompt = "You are an assistant that rewrites resume bullet points to align with a job description."
        user_prompt = (
            "Rewrite the following resume section so that it highlights the most relevant experience for the job."
            "\n\nResume:\n" + resume + "\n\nJob Description:\n" + job_description
        )
        result = await self.generate(system_prompt, user_prompt)
        return result or self._fallback_resume(resume, job_description)

    async def cover_letter(self, profile_summary: str, job_description: str, company: str) -> str:
        system_prompt = "You craft concise, tailored cover letters for technology roles."
        user_prompt = (
            f"Create a 3-paragraph cover letter for {company}.\n"
            f"Profile Summary:\n{profile_summary}\n"
            f"Job Description:\n{job_description}"
        )
        result = await self.generate(system_prompt, user_prompt)
        return result or self._fallback_cover_letter(profile_summary, job_description, company)

    async def summarize_job(self, job_description: str, title: str, company: str) -> str:
        system_prompt = "Summarize job postings in two sentences focused on impact, stack, and location."
        user_prompt = f"Title: {title}\nCompany: {company}\nDescription: {job_description}"
        result = await self.generate(system_prompt, user_prompt)
        return result or self._fallback_summary(job_description)

    def _fallback_resume(self, resume: str, job_description: str) -> str:
        return (
            "Key Highlights:\n"
            "- Matched experience with job requirements using existing resume content.\n"
            "- Focus areas: " + ", ".join(list(dict.fromkeys(job_description.split()))[:5])
        )

    def _fallback_cover_letter(self, profile: str, job_description: str, company: str) -> str:
        return (
            f"Dear {company} Hiring Team,\n\n"
            "I was excited to find this opening and believe my background aligns well with your needs. "
            "Highlights include: "
            + " ".join(job_description.split()[:40])
            + "...\n\nBest regards,\nYour Candidate"
        )

    def _fallback_summary(self, job_description: str) -> str:
        words = job_description.split()
        return " ".join(words[:50]) + ("..." if len(words) > 50 else "")


__all__ = ["AITextGenerator"]
