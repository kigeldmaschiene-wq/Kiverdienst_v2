"""
Debug and troubleshooting API routes
"""
import logging
import os
import socket
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from database import get_db, check_db_connection
from models import SystemLog

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    component: Optional[str] = Query(None, description="Filter by component"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    db: Session = Depends(get_db)
):
    """
    Get system logs with optional filtering
    Returns recent logs ordered by creation time (newest first)
    """
    try:
        query = db.query(SystemLog)
        
        # Apply filters
        if level:
            query = query.filter(SystemLog.level == level.upper())
        
        if component:
            query = query.filter(SystemLog.component == component)
        
        # Order by creation time (newest first) and limit
        logs = query.order_by(desc(SystemLog.created_at)).limit(limit).all()
        
        return {
            "total": len(logs),
            "filters": {
                "level": level,
                "component": component
            },
            "logs": [
                {
                    "id": log.id,
                    "level": log.level,
                    "component": log.component,
                    "message": log.message,
                    "details": log.details,
                    "brand_id": log.brand_id,
                    "video_id": log.video_id,
                    "created_at": str(log.created_at)
                }
                for log in logs
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs")
async def clear_logs(
    older_than_days: Optional[int] = Query(None, description="Delete logs older than N days"),
    db: Session = Depends(get_db)
):
    """
    Clear system logs
    Optionally delete only logs older than specified days
    """
    try:
        query = db.query(SystemLog)
        
        if older_than_days:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            query = query.filter(SystemLog.created_at < cutoff_date)
            message = f"Logs older than {older_than_days} days deleted"
        else:
            message = "All logs deleted"
        
        deleted_count = query.delete()
        db.commit()
        
        # Log the deletion
        log_entry = SystemLog(
            level="WARNING",
            component="debug",
            message="System logs cleared",
            details={
                "deleted_count": deleted_count,
                "older_than_days": older_than_days
            }
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"Deleted {deleted_count} log entries")
        
        return {
            "success": True,
            "deleted": deleted_count,
            "message": message
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database")
async def test_database(db: Session = Depends(get_db)):
    """
    Test database connection and return detailed information
    """
    try:
        # Test basic connection
        db_ok, db_msg = check_db_connection()
        
        if not db_ok:
            return {
                "success": False,
                "message": db_msg
            }
        
        # Get database version
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        
        # Get database size
        db_name = os.getenv("POSTGRES_DB", "kiverdienst_v2")
        result = db.execute(text(
            f"SELECT pg_size_pretty(pg_database_size('{db_name}'))"
        ))
        db_size = result.fetchone()[0]
        
        # Count tables
        result = db.execute(text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ))
        table_count = result.fetchone()[0]
        
        return {
            "success": True,
            "message": "Database connection successful",
            "version": version,
            "database_name": db_name,
            "database_size": db_size,
            "table_count": table_count
        }
    
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/test-api")
async def test_external_apis():
    """
    Test external API connections
    Checks if API keys are configured and services are reachable
    """
    results = {}
    
    # Test OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    results["openai"] = {
        "configured": bool(openai_key),
        "key_present": bool(openai_key),
        "status": "configured" if openai_key else "not configured"
    }
    
    # Test ElevenLabs
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    results["elevenlabs"] = {
        "configured": bool(elevenlabs_key),
        "key_present": bool(elevenlabs_key),
        "status": "configured" if elevenlabs_key else "not configured"
    }
    
    # Test Replicate
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    results["replicate"] = {
        "configured": bool(replicate_token),
        "key_present": bool(replicate_token),
        "status": "configured" if replicate_token else "not configured"
    }
    
    # Test Ollama
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    try:
        import httpx
        response = httpx.get(f"{ollama_host}/api/tags", timeout=5)
        ollama_available = response.status_code == 200
        results["ollama"] = {
            "configured": True,
            "host": ollama_host,
            "status": "available" if ollama_available else "unavailable"
        }
    except Exception as e:
        results["ollama"] = {
            "configured": True,
            "host": ollama_host,
            "status": "error",
            "error": str(e)
        }
    
    return {
        "success": True,
        "apis": results
    }


@router.get("/ports")
async def check_ports():
    """
    Check which ports are in use
    Returns status of commonly used ports
    """
    ports_to_check = {
        "Frontend": int(os.getenv("FRONTEND_PORT", 5000)),
        "Backend": int(os.getenv("BACKEND_PORT", 8000)),
        "PostgreSQL": int(os.getenv("POSTGRES_PORT", 5432)),
        "Nginx": 80,
        "Nginx HTTPS": 443,
        "Ollama": 11434
    }
    
    port_status = {}
    
    for service, port in ports_to_check.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        try:
            result = sock.connect_ex(('localhost', port))
            in_use = result == 0
            port_status[service] = {
                "port": port,
                "in_use": in_use,
                "status": "open" if in_use else "closed"
            }
        except Exception as e:
            port_status[service] = {
                "port": port,
                "in_use": False,
                "status": "error",
                "error": str(e)
            }
        finally:
            sock.close()
    
    return {
        "success": True,
        "ports": port_status
    }


@router.get("/env")
async def get_environment():
    """
    Get environment variables (sanitized)
    Hides sensitive information like passwords and API keys
    """
    env_vars = {}
    
    sensitive_keys = [
        "PASSWORD", "SECRET", "KEY", "TOKEN", "API"
    ]
    
    for key, value in os.environ.items():
        if key.startswith("POSTGRES") or key.startswith("KIVERDIENST"):
            # Check if it's sensitive
            is_sensitive = any(s in key.upper() for s in sensitive_keys)
            
            if is_sensitive:
                env_vars[key] = "***HIDDEN***" if value else "(not set)"
            else:
                env_vars[key] = value
    
    return {
        "success": True,
        "environment": env_vars
    }


@router.get("/components")
async def list_components(db: Session = Depends(get_db)):
    """
    List all components that have logged messages
    Useful for filtering logs
    """
    try:
        result = db.query(SystemLog.component).distinct().all()
        components = [row[0] for row in result if row[0]]
        
        return {
            "success": True,
            "total": len(components),
            "components": sorted(components)
        }
    
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail=str(e))
