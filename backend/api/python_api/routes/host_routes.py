import sys
import os

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from utils.db_sync import DBSync
from dependencies.db_loader import get_db_sync
from auth.auth_bearer import JWTBearer
from fastapi import APIRouter, Depends, HTTPException, status


host_router = APIRouter(
    prefix="/host",
    tags=["Host"],
    dependencies=[Depends(JWTBearer())]  # ✅ applies JWT to all host routes
)


router = APIRouter()

class HostCreate(BaseModel):
    uid: str
    full_name: str
    email: str
    mobile_num: str
    address: str
    location: str
    hosting_addresses: list[str]
    locality: list[str]
    updated_at: list[str]
    password: str
    username: str
    ranged_id: int

@router.post("/create", dependencies=[Depends(JWTBearer())])
def create_host(host: HostCreate):
    db = get_db_sync()
    try:
        data = host.dict()
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.insert_host_participant(data)
        return {"status": "success", "uid": host.uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating host/participant: {e}")
    
# @host_router.get("/get/{uid}", dependencies=[Depends(JWTBearer())])
@router.get("/get/{uid}", dependencies=[Depends(JWTBearer())])
def get_host(uid: str, dbs: DBSync = Depends(get_db_sync)):
    try:
        # ✅ Fix MySQL fetch
        cursor = dbs.sql.cursor(dictionary=True)
        cursor.execute("SELECT * FROM host_participant WHERE uid = %s", (uid,))
        host_data = cursor.fetchone()
        cursor.close()

        if not host_data:
            raise HTTPException(status_code=404, detail="Host/Participant not found")

        # ✅ Fix MongoDB fetch
        mongo_data = dbs.mongo['host_participant_docs'].find_one({"uid": uid}, {"_id": 0})
        host_data["nosql_backup"] = mongo_data or {}

        return {"success": True, "host": host_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
@router.put("/update/{uid}", dependencies=[Depends(JWTBearer())])
def update_host(uid: str, update_data: dict, db: DBSync = Depends(get_db_sync)):
    try:
        # --- MySQL Update ---
        mysql_fields = ", ".join([f"{key} = %s" for key in update_data.keys()])
        mysql_query = f"UPDATE host_participant SET {mysql_fields} WHERE uid = %s"
        mysql_values = list(update_data.values()) + [uid]
        db.mysql_cursor.execute(mysql_query, tuple(mysql_values))
        db.mysql_conn.commit()

        # --- SQLite Update ---
        sqlite_fields = ", ".join([f"{key} = ?" for key in update_data.keys()])
        sqlite_query = f"UPDATE host_participant SET {sqlite_fields} WHERE uid = ?"
        sqlite_values = list(update_data.values()) + [uid]
        db.sqlite_cursor.execute(sqlite_query, tuple(sqlite_values))
        db.sqlite_conn.commit()

        # --- MongoDB Update ---
        db.mongo_db['host_participant_docs'].update_one({"uid": uid}, {"$set": update_data})

        return {"success": True, "message": f"Host/Participant {uid} updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/delete/{uid}", dependencies=[Depends(JWTBearer())])
def delete_host(uid: str, db: DBSync = Depends(get_db_sync)):
    try:
        # --- MySQL Delete ---
        db.mysql_cursor.execute("DELETE FROM host_participant WHERE uid = %s", (uid,))
        db.mysql_conn.commit()

        # --- SQLite Delete ---
        db.sqlite_cursor.execute("DELETE FROM host_participant WHERE uid = ?", (uid,))
        db.sqlite_conn.commit()

        # --- MongoDB Delete ---
        db.mongo_db['host_participant_docs'].delete_one({"uid": uid})

        return {"success": True, "message": f"Host/Participant {uid} deleted from all databases."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/all", dependencies=[Depends(JWTBearer())])
def get_all_hosts(dbs: DBSync = Depends(get_db_sync)):
    try:
        # MySQL fetch
        mysql_cursor = dbs.mysql_conn.cursor(dictionary=True)
        mysql_cursor.execute("SELECT * FROM host_participant")
        hosts = mysql_cursor.fetchall()
        mysql_cursor.close()

        # MongoDB fetch for optional backup view
        mongo_hosts = list(dbs.mongo_db.host_participant_docs.find({}, {"_id": 0}))

        return {
            "success": True,
            "source": "MySQL",
            "hosts": hosts,
            "nosql_backup": mongo_hosts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")



