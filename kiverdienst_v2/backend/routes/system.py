"""
System status and monitoring API routes
"""
import logging
import os
import subprocess
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, check_db_connection
from models import Brand, Video, VideoScript, SystemLog

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def system_health(db: Session = Depends(get_db)):
    """
    Get overall system health status
    Checks all critical services
    """
    health_status = {
        "overall": "healthy",
        "services": {}
    }
    
    # Check database
    db_ok, db_msg = check_db_connection()
    health_status["services"]["database"] = {
        "status": "healthy" if db_ok else "unhealthy",
        "message": db_msg
    }
    
    # Check backend
    health_status["services"]["backend"] = {
        "status": "healthy",
        "message": "API is running"
    }
    
    # Check Docker containers (if docker command available)
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            containers = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) == 2:
                        name, status = parts
                        is_up = 'Up' in status
                        containers[name] = {
                            "status": "healthy" if is_up else "unhealthy",
                            "details": status
                        }
            
            health_status["services"]["docker"] = {
                "status": "healthy",
                "containers": containers
            }
        else:
            health_status["services"]["docker"] = {
                "status": "unknown",
                "message": "Could not check Docker status"
            }
    except Exception as e:
        health_status["services"]["docker"] = {
            "status": "unknown",
            "message": str(e)
        }
    
    # Determine overall health
    unhealthy_services = [
        name for name, service in health_status["services"].items()
        if service.get("status") == "unhealthy"
    ]
    
    if unhealthy_services:
        health_status["overall"] = "degraded"
        health_status["unhealthy_services"] = unhealthy_services
    
    return health_status


@router.get("/stats")
async def system_stats(db: Session = Depends(get_db)):
    """
    Get quick system statistics
    Returns counts of main entities
    """
    try:
        # Count brands by status
        total_brands = db.query(func.count(Brand.id)).scalar()
        active_brands = db.query(func.count(Brand.id)).filter(
            Brand.status == 'active'
        ).scalar()
        
        # Count videos by status
        total_videos = db.query(func.count(Video.id)).scalar()
        posted_videos = db.query(func.count(Video.id)).filter(
            Video.status == 'posted'
        ).scalar()
        
        # Count scripts
        total_scripts = db.query(func.count(VideoScript.id)).scalar()
        approved_scripts = db.query(func.count(VideoScript.id)).filter(
            VideoScript.status == 'approved'
        ).scalar()
        
        # Count recent logs (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_errors = db.query(func.count(SystemLog.id)).filter(
            SystemLog.level == 'ERROR',
            SystemLog.created_at >= yesterday
        ).scalar()
        
        return {
            "brands": {
                "total": total_brands,
                "active": active_brands,
                "paused": total_brands - active_brands
            },
            "videos": {
                "total": total_videos,
                "posted": posted_videos,
                "pending": total_videos - posted_videos
            },
            "scripts": {
                "total": total_scripts,
                "approved": approved_scripts
            },
            "logs": {
                "recent_errors": recent_errors
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docker")
async def docker_status():
    """
    Get Docker containers status
    Returns information about all running containers
    """
    try:
        # Get container information
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", 
             "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.CreatedAt}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "message": "Could not get Docker status",
                "error": result.stderr
            }
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    container_id, name, status, image = parts[:4]
                    created = parts[4] if len(parts) > 4 else "Unknown"
                    
                    is_running = 'Up' in status
                    
                    containers.append({
                        "id": container_id[:12],
                        "name": name,
                        "status": "running" if is_running else "stopped",
                        "status_details": status,
                        "image": image,
                        "created": created
                    })
        
        return {
            "success": True,
            "total": len(containers),
            "running": sum(1 for c in containers if c["status"] == "running"),
            "containers": containers
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Docker command timed out"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "Docker command not found"
        }
    except Exception as e:
        logger.error(f"Error getting Docker status: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/info")
async def system_info():
    """
    Get system information
    Returns environment and configuration details
    """
    return {
        "version": "2.0.0",
        "environment": {
            "debug": os.getenv("DEBUG", "false"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "backend_port": os.getenv("BACKEND_PORT", "8000"),
            "frontend_port": os.getenv("FRONTEND_PORT", "5000")
        },
        "database": {
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "kiverdienst_v2")
        },
        "features": {
            "ollama_enabled": os.getenv("OLLAMA_HOST") is not None,
            "openai_enabled": bool(os.getenv("OPENAI_API_KEY")),
            "elevenlabs_enabled": bool(os.getenv("ELEVENLABS_API_KEY"))
        }
    }


@router.post("/restart/{service}")
async def restart_service(service: str):
    """
    Restart a specific Docker service
    Available services: backend, frontend, postgres, nginx
    """
    valid_services = ["backend", "frontend", "postgres", "nginx"]
    
    if service not in valid_services:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service. Must be one of: {', '.join(valid_services)}"
        )
    
    try:
        result = subprocess.run(
            ["docker", "compose", "restart", service],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/opt/kiverdienst_v2"
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "service": service,
                "message": f"Service {service} restarted successfully"
            }
        else:
            return {
                "success": False,
                "service": service,
                "message": "Failed to restart service",
                "error": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Restart command timed out")
    except Exception as e:
        logger.error(f"Error restarting service {service}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
