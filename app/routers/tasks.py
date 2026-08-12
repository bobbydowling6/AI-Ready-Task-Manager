from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.tasks import Tasks
from app.schemas.tasks import TaskCreate, GetTasks, GetSpecificTask, UpdateTask, DeleteTask, TaskResponse, TaskPatch, CreateAiTask
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException
from app.utils.notifications import log_activity, send_notification
from app.utils.security import get_current_task
from app.main import limiter

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_task_or_404(db: Session, task_id: int) -> Tasks:
    """Helper: fetch a task or raise 404."""
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise NotFoundException("Task", task_id)
    return task


def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@limiter.limit("20/minute")
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
    responses={
        201: {"description": "Task created successfully"},
        400: {"description": "Duplicate email or bad request"},
        401: {"description": "Unauthorized access"},
        422: {"description": "Validation error on request body"},
    },
)
def create_task(
    request: Request,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_task: Tasks = Depends(get_current_task),
    background_tasks: BackgroundTasks = None,
):
    """
    Create a new task record in the system.

    * **Authentication Required:** Must provide a valid access token.
    * **Rate Limited:** Max 20 requests per minute.
    * **Background Tasks:** Triggers activity logging and a welcome notification email.
    * **Error Handling:** Returns a `400` duplicate error if the email is already registered.
    """



@limiter.limit("60/minute")
@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="Retrieve all tasks",
)
def read_tasks(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve a list of all tasks records.

    * **Public Access:** No authentication required.
    * **Rate Limited:** Max 60 requests per minute.
    * **Returns:** A list of student objects.
    """
    return db.query(Tasks).all()


@limiter.limit("60/minute")
@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve task by ID",
    responses={
        200: {"description": "Task record found"},
        404: {"description": "Task not found"},
    },
)
def read_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single task record by its unique ID.

    * **Public Access:** No authentication required.
    * **Rate Limited:** Max 60 requests per minute.
    * **Error Handling:** Raises a `404 Not Found` if the student ID does not exist.
    """
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise NotFoundException("Task", task_id)
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task updated successfully"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Fully update an existing task record by ID.

    * **Complete Replacement:** Overwrites all provided fields for the task.
    * **Error Handling:** Raises a `404 Not Found` if the task record does not exist.
    """
    task = get_task_or_404(db, task_id)
    for key, value in _model_dump(task_update).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update task",
    responses={
        200: {"description": "Profile updated successfully"},
        400: {"description": "Bad request (attempting to modify another student's profile)"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
        422: {"description": "Validation error"},
    },
)
def patch_task(
    task_id: int,
    task_patch: TaskPatch,
    db: Session = Depends(get_db),
    current_task: Tasks = Depends(get_current_task),
):
    """
    Partially update an existing task record.

    * **Authentication Required:** Users can only modify their own profile.
    * **Validation:** Ensures `task_id` matches the authenticated user ID.
    * **Partial Fields:** Only updates fields explicitly provided in the request body.
    """
    task = get_task_or_404(db, task_id)
    if task.id != current_task.id:
        raise BadRequestException("You can only modify your own task")
    for key, value in _model_dump(task_patch).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=204,
    responses={
        204: {"description": "Task deleted successfully"},
        400: {"description": "Bad request (student enrolled or modifying another profile)"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Student not found"},
    },
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_task: Tasks = Depends(get_current_task),
    background_tasks: BackgroundTasks = None,
):
    """
    Delete a task record by ID.

    * **Authentication Required:** Users can only delete their own profile.
    * **Enrollment Check:** Cannot delete a student who is currently enrolled (`is_enrolled=True`).
    * **Background Tasks:** Triggers an asynchronous activity log upon successful deletion.
    """
    task = get_task_or_404(db, task_id)
    if task.id != current_task.id:
        raise BadRequestException("You can only delete your own profile")
    if task.is_enrolled:
        raise BadRequestException("Cannot delete an enrolled task")
    db.delete(task)
    db.commit()

    if background_tasks is not None:
        background_tasks.add_task(
            log_activity,
            current_task.id,
            f"Deleted task {task_id}",
        )
    return None

@limiter.limit("60/minute")
@router.get(
    "/me",
    response_model=get_current_task,
    summary="Get current task",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Unauthorized access or invalid token"},
    },
)
def get_my_profile(request: Request, current_task: Tasks = Depends(get_current_task)):
    """
    Retrieve the profile details of the currently authenticated student.

    * **Authentication Required:** Valid access token must be supplied.
    * **Rate Limited:** Max 60 requests per minute.
    * **Returns:** The authenticated student model instance.
    """
    return current_task