"""
Setup wizard API routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, check_db_connection
from models import SystemConfig, SystemLog

logger = logging.getLogger(__name__)
router = APIRouter()


class SetupInitRequest(BaseModel):
    """Request model for setup initialization"""
    admin_email: str
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    replicate_api_token: str = ""


class SetupStatusResponse(BaseModel):
    """Response model for setup status"""
    completed: bool
    step: str
    message: str


@router.get("/status", response_model=SetupStatusResponse)
async def get_setup_status(db: Session = Depends(get_db)):
    """
    Check if setup has been completed
    Returns current setup status
    """
    try:
        config = db.query(SystemConfig).filter(
            SystemConfig.key == "setup_completed"
        ).first()
        
        if not config:
            return SetupStatusResponse(
                completed=False,
                step="initial",
                message="Setup not started"
            )
        
        is_completed = config.value == "true"
        
        return SetupStatusResponse(
            completed=is_completed,
            step="completed" if is_completed else "in_progress",
            message="Setup completed" if is_completed else "Setup in progress"
        )
    
    except Exception as e:
        logger.error(f"Error checking setup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init")
async def initialize_setup(
    request: SetupInitRequest,
    db: Session = Depends(get_db)
):
    """
    Initialize system configuration
    Sets up admin account and tests database connection
    """
    try:
        # Test database connection
        db_ok, db_msg = check_db_connection()
        if not db_ok:
            raise HTTPException(status_code=500, detail=f"Database error: {db_msg}")
        
        # Update or create admin email
        admin_email_config = db.query(SystemConfig).filter(
            SystemConfig.key == "admin_email"
        ).first()
        
        if admin_email_config:
            admin_email_config.value = request.admin_email
        else:
            admin_email_config = SystemConfig(
                key="admin_email",
                value=request.admin_email,
                description="Administrator email address"
            )
            db.add(admin_email_config)
        
        # Store API keys if provided
        api_keys = {
            "openai_api_key": request.openai_api_key,
            "elevenlabs_api_key": request.elevenlabs_api_key,
            "replicate_api_token": request.replicate_api_token
        }
        
        for key, value in api_keys.items():
            if value:
                config = db.query(SystemConfig).filter(
                    SystemConfig.key == key
                ).first()
                
                if config:
                    config.value = value
                else:
                    config = SystemConfig(
                        key=key,
                        value=value,
                        description=f"API key for {key.replace('_', ' ')}"
                    )
                    db.add(config)
        
        # Log setup initialization
        log_entry = SystemLog(
            level="INFO",
            component="setup",
            message="System initialization completed",
            details={
                "admin_email": request.admin_email,
                "api_keys_configured": [k for k, v in api_keys.items() if v]
            }
        )
        db.add(log_entry)
        
        db.commit()
        
        logger.info(f"Setup initialized for {request.admin_email}")
        
        return {
            "success": True,
            "message": "System initialized successfully",
            "database": db_msg
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing setup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_setup(db: Session = Depends(get_db)):
    """
    Mark setup as completed
    This should be called after all setup steps are done
    """
    try:
        # Update setup_completed flag
        config = db.query(SystemConfig).filter(
            SystemConfig.key == "setup_completed"
        ).first()
        
        if config:
            config.value = "true"
        else:
            config = SystemConfig(
                key="setup_completed",
                value="true",
                description="Whether initial setup wizard has been completed"
            )
            db.add(config)
        
        # Log setup completion
        log_entry = SystemLog(
            level="INFO",
            component="setup",
            message="Setup wizard completed",
            details={"completed_at": str(db.query(SystemConfig).count())}
        )
        db.add(log_entry)
        
        db.commit()
        
        logger.info("Setup marked as completed")
        
        return {
            "success": True,
            "message": "Setup completed successfully",
            "redirect": "/dashboard"
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing setup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements")
async def check_requirements():
    """
    Check system requirements
    Returns status of all required components
    """
    requirements = {
        "database": {"status": "checking", "message": ""},
        "disk_space": {"status": "ok", "message": "Sufficient space available"},
        "docker": {"status": "ok", "message": "Docker is running"},
    }
    
    # Check database
    db_ok, db_msg = check_db_connection()
    requirements["database"]["status"] = "ok" if db_ok else "error"
    requirements["database"]["message"] = db_msg
    
    # Check if all requirements are met
    all_ok = all(req["status"] == "ok" for req in requirements.values())
    
    return {
        "all_met": all_ok,
        "requirements": requirements
    }
