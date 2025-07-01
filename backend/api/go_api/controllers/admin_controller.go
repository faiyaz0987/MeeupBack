package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"meetup/db"
	"meetup/models"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func CreateAdmin(c *gin.Context) {
	var admin models.Admin

	if err := c.ShouldBindJSON(&admin); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	// Timestamps
	now := time.Now().Format(time.RFC3339)
	admin.CreatedAt = now
	admin.UpdatedAt = []string{now}

	// MySQL Insert
	sql := "INSERT INTO admin (uid, full_name, address, mobile_num, email, valid_id_numbers, created_at, updated_at, password, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	_, err := db.MySQL.Exec(sql,
		admin.UID, admin.FullName, admin.Address, admin.MobileNum, admin.Email,
		toJSONString(admin.ValidIDNumbers), admin.CreatedAt, toJSONString(admin.UpdatedAt),
		admin.Password, admin.Username,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("MySQL error: %v", err)})
		return
	}

	// SQLite Insert
	sqlite := "INSERT INTO admin (uid, full_name, address, mobile_num, email, valid_id_numbers, created_at, updated_at, password, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	_, err = db.SQLite.Exec(sqlite,
		admin.UID, admin.FullName, admin.Address, admin.MobileNum, admin.Email,
		toJSONString(admin.ValidIDNumbers), admin.CreatedAt, toJSONString(admin.UpdatedAt),
		admin.Password, admin.Username,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("SQLite error: %v", err)})
		return
	}

	// MongoDB Insert
	_, err = db.Mongo.Collection("admin_docs").InsertOne(context.Background(), admin)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("MongoDB error: %v", err)})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Admin created successfully", "admin": admin})
}

func toJSONString(v interface{}) string {
	bytes, _ := json.Marshal(v)
	return string(bytes)
}

func GetAdminByUID(c *gin.Context) {
	uid := c.Param("uid")

	var admin models.Admin

	// Fetch from MySQL
	sql := "SELECT * FROM admin WHERE uid = ?"
	row := db.MySQL.QueryRow(sql, uid)
	var updatedAt, validIDs string

	err := row.Scan(&admin.UID, &admin.FullName, &admin.Address, &admin.MobileNum,
		&admin.Email, &validIDs, &admin.CreatedAt, &updatedAt,
		&admin.Password, &admin.Username)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Admin not found"})
		return
	}
	// Decode JSON arrays
	json.Unmarshal([]byte(validIDs), &admin.ValidIDNumbers)
	json.Unmarshal([]byte(updatedAt), &admin.UpdatedAt)

	// Fetch MongoDB backup
	mongoRes := db.Mongo.Collection("admin_docs").FindOne(context.Background(), map[string]interface{}{"uid": uid})
	var mongoData map[string]interface{}
	mongoRes.Decode(&mongoData)

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"admin":   admin,
		"nosql_backup": mongoData,
	})
}

func UpdateAdminByUID(c *gin.Context) {
	uid := c.Param("uid")
	var updated models.Admin

	if err := c.ShouldBindJSON(&updated); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	// JSON encode fields
	updatedAtJSON, _ := json.Marshal(updated.UpdatedAt)
	validIDsJSON, _ := json.Marshal(updated.ValidIDNumbers)

	// Update MySQL
	query := `
		UPDATE admin SET
			full_name = ?, address = ?, mobile_num = ?, email = ?, 
			valid_id_numbers = ?, created_at = ?, updated_at = ?, 
			password = ?, username = ?
		WHERE uid = ?
	`
	_, err := db.MySQL.Exec(query,
		updated.FullName,
		updated.Address,
		updated.MobileNum,
		updated.Email,
		string(validIDsJSON),
		updated.CreatedAt,
		string(updatedAtJSON),
		updated.Password,
		updated.Username,
		uid,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update MySQL"})
		return
	}

	// Update MongoDB
	_, err = db.Mongo.Collection("admin_docs").UpdateOne(
		context.Background(),
		map[string]interface{}{"uid": uid},
		map[string]interface{}{"$set": updated},
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update MongoDB"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Admin updated successfully",
	})
}

func GetAllAdmins(c *gin.Context) {
	mysqlDB := db.MySQL
	mongoDB := db.MongoDB

	rows, err := mysqlDB.Query("SELECT * FROM admin")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch from MySQL"})
		return
	}
	defer rows.Close()

	var admins []map[string]interface{}
	for rows.Next() {
		var admin = make(map[string]interface{})
		var validIDStr, updatedAtStr string
		err := rows.Scan(
			&admin["uid"], &admin["full_name"], &admin["address"],
			&admin["mobile_num"], &admin["email"],
			&validIDStr, &admin["created_at"], &updatedAtStr,
			&admin["password"], &admin["username"],
		)
		if err != nil {
			continue
		}

		_ = json.Unmarshal([]byte(validIDStr), &admin["valid_id_numbers"])
		_ = json.Unmarshal([]byte(updatedAtStr), &admin["updated_at"])

		// Add backup from MongoDB
		var backup map[string]interface{}
		mongoDB.Collection("admin_docs").FindOne(c, bson.M{"uid": admin["uid"]}).Decode(&backup)
		admin["nosql_backup"] = backup

		admins = append(admins, admin)
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "admins": admins})
}
