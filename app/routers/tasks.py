from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskCreate, UpdateTask, TaskResponse, TaskPatch
from app.utils.exceptions import NotFoundException, BadRequestException
from app.utils.notifications import log_activity
from app.utils.security import get_current_user
from app.main import limiter

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_task_or_404(db: Session, task_id: int) -> Task:
    """Helper: fetch a task or raise 404."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException("Task", task_id)
    return task


def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


@limiter.limit("20/minute")
@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
)
def create_task(
    request: Request,
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        due_date=task_in.due_date,
        is_completed=task_in.is_completed or False,
        user_id=current_user.id,  # FIXED: Removed .value from integer id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    background_tasks.add_task(
        log_activity,
        current_user,  # FIXED: Removed .value  # pyright: ignore[reportArgumentType]
        f"Created task {db_task.id}",
    )
    return db_task


@limiter.limit("60/minute")
@router.get(
    "/tasks",
    response_model=list[TaskResponse],
    summary="Retrieve all tasks",
)
def read_tasks(request: Request, db: Session = Depends(get_db)):
    """Retrieve a list of all task records."""
    return db.query(Task).all()


@limiter.limit("60/minute")
@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve task by ID",
)
def read_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    """Retrieve a single task record by its unique ID."""
    return get_task_or_404(db, task_id)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(task_id: int, task_update: UpdateTask, db: Session = Depends(get_db)):
    """Fully update an existing task record by ID."""
    task = get_task_or_404(db, task_id)
    for key, value in _model_dump(task_update).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Partially update task",
)
def patch_task(
    task_id: int,
    task_patch: TaskPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update an existing task owned by the authenticated user."""
    task = get_task_or_404(db, task_id)
    if task.user_id != current_user.id:  # FIXED: Removed .value and checked task.user_id instead of task.id  # pyright: ignore[reportGeneralTypeIssues]
        raise BadRequestException("You can only modify your own tasks")
    for key, value in _model_dump(task_patch).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
)
def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task owned by the authenticated user."""
    task = get_task_or_404(db, task_id)
    if task.user_id != current_user.id:  # FIXED: Removed .value from both user ids  # pyright: ignore[reportGeneralTypeIssues]
        raise BadRequestException("You can only delete your own tasks")
    db.delete(task)
    db.commit()

    background_tasks.add_task(
        log_activity,
        current_user.id,  # FIXED: Removed .value  # pyright: ignore[reportArgumentType]
        f"Deleted task {task_id}",
    )
    return None


@limiter.limit("60/minute")
@router.get(
    "/me/mine",
    response_model=list[TaskResponse],
    summary="Get current user's tasks",
)
def get_my_tasks(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve tasks belonging to the authenticated user."""
    return db.query(Task).filter(Task.user_id == current_user.id).all()

@router.post(
    "/{task_id}/suggest",
    response_model=TaskResponse,
    summary="Accepts the task description and returns a placeholder AI response",
)
def suggest_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI suggestion placeholder endpoint."""