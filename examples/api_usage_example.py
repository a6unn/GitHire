#!/usr/bin/env python3
"""
Example script demonstrating GitHire Backend API usage.

This script shows a complete workflow:
1. Register a new user
2. Login to get access token
3. Run a recruitment pipeline
4. Check pipeline status
5. List all projects
6. Get detailed project information
7. Export project results
8. Delete a project

Usage:
    python3 examples/api_usage_example.py

Requirements:
    pip install httpx
"""

import asyncio
import json
from typing import Optional

import httpx


# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "demo@example.com"
PASSWORD = "demopassword123"


class GitHireAPIClient:
    """Simple async client for GitHire API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None

    def _headers(self) -> dict:
        """Get headers with authentication if token exists."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def register(self, email: str, password: str) -> dict:
        """Register a new user."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password},
            )
            response.raise_for_status()
            return response.json()

    async def login(self, email: str, password: str) -> dict:
        """Login and store access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            return data

    async def run_pipeline(self, job_description: str) -> dict:
        """Run recruitment pipeline."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/pipeline/run",
                json={"job_description_text": job_description},
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_pipeline_status(self, project_id: str) -> dict:
        """Get pipeline execution status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pipeline/status/{project_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def list_projects(self) -> dict:
        """List all projects for current user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_project(self, project_id: str) -> dict:
        """Get detailed project information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects/{project_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def export_project(self, project_id: str) -> dict:
        """Export project results as JSON."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects/{project_id}/export",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def delete_project(self, project_id: str) -> dict:
        """Delete a project."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/projects/{project_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def logout(self) -> dict:
        """Logout current user."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/logout",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()


async def main():
    """Demonstrate complete API workflow."""
    client = GitHireAPIClient(BASE_URL)

    print("=" * 60)
    print("GitHire API Example Workflow")
    print("=" * 60)

    try:
        # Step 1: Register
        print("\n[1/9] Registering new user...")
        try:
            user = await client.register(EMAIL, PASSWORD)
            print(f"✓ Registered user: {user['email']}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                print("✓ User already exists, continuing...")
            else:
                raise

        # Step 2: Login
        print("\n[2/9] Logging in...")
        login_data = await client.login(EMAIL, PASSWORD)
        print(f"✓ Logged in successfully")
        print(f"  Token: {login_data['access_token'][:20]}...")

        # Step 3: Run pipeline
        print("\n[3/9] Running recruitment pipeline...")
        job_description = """
        We're looking for a Senior Python Developer with 5+ years of experience.

        Required Skills:
        - Python (expert level)
        - FastAPI, Flask, or Django
        - SQLAlchemy or similar ORM
        - PostgreSQL or MySQL
        - REST API design
        - Git and GitHub

        Nice to have:
        - Docker and Kubernetes
        - AWS or GCP experience
        - Machine learning experience
        """

        pipeline_result = await client.run_pipeline(job_description.strip())
        project_id = pipeline_result["project_id"]
        print(f"✓ Pipeline completed successfully")
        print(f"  Project ID: {project_id}")
        print(f"  Status: {pipeline_result['status']}")
        print(f"  Candidates found: {pipeline_result['metadata']['candidates_found']}")
        print(f"  Execution time: {pipeline_result['metadata']['execution_time_seconds']:.2f}s")

        # Step 4: Check status
        print("\n[4/9] Checking pipeline status...")
        status = await client.get_pipeline_status(project_id)
        print(f"✓ Status: {status['status']}")
        print(f"  Progress: {status['progress_percentage']}%")

        # Step 5: List projects
        print("\n[5/9] Listing all projects...")
        projects = await client.list_projects()
        print(f"✓ Found {projects['total']} project(s)")
        for i, project in enumerate(projects['projects'], 1):
            print(f"  {i}. {project['project_id']} - {project['status']} - {project['candidate_count']} candidates")

        # Step 6: Get project details
        print("\n[6/9] Getting project details...")
        project_detail = await client.get_project(project_id)
        print(f"✓ Project details retrieved")
        print(f"  Status: {project_detail['status']}")
        print(f"  Candidates: {project_detail['candidate_count']}")
        print(f"  Created: {project_detail['created_at']}")

        if project_detail['results_json']:
            results = project_detail['results_json']
            print(f"\n  Pipeline Results:")
            print(f"    - Candidates found: {len(results.get('candidates', []))}")
            print(f"    - Ranked candidates: {len(results.get('ranked_candidates', []))}")
            print(f"    - Messages generated: {len(results.get('outreach_messages', []))}")

            # Show top candidate if available
            if results.get('ranked_candidates'):
                top = results['ranked_candidates'][0]
                print(f"\n  Top Candidate:")
                print(f"    - Username: {top['github_username']}")
                print(f"    - Score: {top['total_score']:.1f}")
                print(f"    - Rank: {top['rank']}")

        # Step 7: Export project
        print("\n[7/9] Exporting project results...")
        export_data = await client.export_project(project_id)
        export_filename = f"project_{project_id[:8]}.json"
        with open(export_filename, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"✓ Exported to {export_filename}")

        # Step 8: Delete project
        print("\n[8/9] Deleting project...")
        delete_result = await client.delete_project(project_id)
        print(f"✓ {delete_result['message']}")

        # Step 9: Logout
        print("\n[9/9] Logging out...")
        logout_result = await client.logout()
        print(f"✓ {logout_result['message']}")

        print("\n" + "=" * 60)
        print("Workflow completed successfully!")
        print("=" * 60)

    except httpx.HTTPStatusError as e:
        print(f"\n✗ HTTP Error: {e.response.status_code}")
        print(f"  {e.response.text}")
    except httpx.RequestError as e:
        print(f"\n✗ Request Error: {e}")
        print("\nMake sure the API server is running:")
        print("  cd src/backend_api")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
