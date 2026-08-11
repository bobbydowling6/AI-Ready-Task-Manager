from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.tasks import Tasks
from app.schemas.tasks import StudentCreate, StudentUpdate, StudentPatch, StudentResponse
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException
from app.utils.notifications import log_activity, send_notification
from app.utils.security import get_current_task
from app.main import limiter