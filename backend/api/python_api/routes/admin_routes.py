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


admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(JWTBearer())]  # ✅ protects all routes under /admin
)


router = APIRouter()

class AdminCreate(BaseModel):
    uid: str
    full_name: str
    address: str
    mobile_num: str
    email: str
    valid_id_numbers: list[str]
    updated_at: list[str]
    password: str
    username: str

@router.post("/create", dependencies=[Depends(JWTBearer())])
def create_admin(admin: AdminCreate):
    db = get_db_sync()
    try:
        data = admin.dict()
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.insert_admin(data)
        return {"status": "success", "uid": admin.uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin: {e}")
    
# @admin_router.get("/get/{uid}", dependencies=[Depends(JWTBearer())])
@router.get("/get/{uid}", dependencies=[Depends(JWTBearer())])
def get_admin(uid: str, dbs: DBSync = Depends(get_db_sync)):
    try:
        # ✅ Fix MySQL fetch
        cursor = dbs.sql.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE uid = %s", (uid,))
        admin_data = cursor.fetchone()
        cursor.close()

        if not admin_data:
            raise HTTPException(status_code=404, detail="Admin not found")

        # ✅ Fix MongoDB fetch
        mongo_data = dbs.mongo['admin_docs'].find_one({"uid": uid}, {"_id": 0})
        admin_data["nosql_backup"] = mongo_data or {}

        return {"success": True, "admin": admin_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.put("/update/{uid}", dependencies=[Depends(JWTBearer())])
def update_admin(uid: str, update_data: dict, db: DBSync = Depends(get_db_sync)):
    try:
        # --- MySQL Update ---
        mysql_fields = ", ".join([f"{key} = %s" for key in update_data.keys()])
        mysql_query = f"UPDATE admin SET {mysql_fields} WHERE uid = %s"
        mysql_values = list(update_data.values()) + [uid]
        db.mysql_cursor.execute(mysql_query, tuple(mysql_values))
        db.mysql_conn.commit()

        # --- SQLite Update ---
        sqlite_fields = ", ".join([f"{key} = ?" for key in update_data.keys()])
        sqlite_query = f"UPDATE admin SET {sqlite_fields} WHERE uid = ?"
        sqlite_values = list(update_data.values()) + [uid]
        db.sqlite_cursor.execute(sqlite_query, tuple(sqlite_values))
        db.sqlite_conn.commit()

        # --- MongoDB Update ---
        db.mongo_db['admin_docs'].update_one({"uid": uid}, {"$set": update_data})

        return {"success": True, "message": f"Admin {uid} updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/delete/{uid}", dependencies=[Depends(JWTBearer())])
def delete_admin(uid: str, db: DBSync = Depends(get_db_sync)):
    try:
        # --- MySQL Delete ---
        db.mysql_cursor.execute("DELETE FROM admin WHERE uid = %s", (uid,))
        db.mysql_conn.commit()

        # --- SQLite Delete ---
        db.sqlite_cursor.execute("DELETE FROM admin WHERE uid = ?", (uid,))
        db.sqlite_conn.commit()

        # --- MongoDB Delete ---
        db.mongo_db['admin_docs'].delete_one({"uid": uid})

        return {"success": True, "message": f"Admin {uid} deleted from all databases."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/all", dependencies=[Depends(JWTBearer())])
def get_all_admins(dbs: DBSync = Depends(get_db_sync)):
    try:
        # MySQL fetch
        mysql_cursor = dbs.mysql_conn.cursor(dictionary=True)
        mysql_cursor.execute("SELECT * FROM admin")
        admins = mysql_cursor.fetchall()
        mysql_cursor.close()

        # MongoDB fetch for optional backup view
        mongo_admins = list(dbs.mongo_db.admin_docs.find({}, {"_id": 0}))

        return {
            "success": True,
            "source": "MySQL",
            "admins": admins,
            "nosql_backup": mongo_admins
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")



