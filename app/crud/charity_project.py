from operator import itemgetter
from typing import Optional

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == project_name)
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_projects_by_completion_rate(self, session: AsyncSession):
        projects = (
            select(CharityProject).where(CharityProject.fully_invested)
        )
        result = await session.execute(projects)
        projects = result.scalars().all()
        closed_projects = []
        for project in projects:
            closed_projects.append({
                'name': project.name,
                'time_collected': project.close_date - project.create_date,
                'description': project.description,
            })
        return sorted(closed_projects, key=itemgetter('time_collected'))


charity_project_crud = CRUDCharityProject(CharityProject)
