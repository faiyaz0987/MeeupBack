package controllers

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"meetup/api/go_api/db"
	"meetup/api/go_api/models"
)

func CreateHost(c *gin.Context) {
	var host models.Host

	if err := c.ShouldBindJSON(&host); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	// Encode array fields to JSON strings for SQL
	updatedAtJSON, _ := json.Marshal(host.UpdatedAt)
	hostingAddrsJSON, _ := json.Marshal(host.HostingAddresses)
	localityJSON, _ := json.Marshal(host.Locality)

	// MySQL Insert
	query := `
		INSERT INTO host_participant (
			uid, full_name, email, mobile_num, address, location,
			hosting_addresses, locality, created_at, updated_at,
			password, username, ranged_id
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`
	_, err := db.MySQL.Exec(query,
		host.UID,
		host.FullName,
		host.Email,
		host.MobileNum,
		host.Address,
		host.Location,
		string(hostingAddrsJSON),
		string(localityJSON),
		host.CreatedAt,
		string(updatedAtJSON),
		host.Password,
		host.Username,
		host.RangedID,
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to insert into MySQL"})
		return
	}

	// MongoDB Insert
	_, err = db.Mongo.Collection("host_participant_docs").InsertOne(context.Background(), host)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to insert into MongoDB"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"message": "Host/Participant created successfully",
	})
}

func GetHostByUID(c *gin.Context) {
	uid := c.Param("uid")

	var host models.Host

	sql := "SELECT * FROM host_participant WHERE uid = ?"
	row := db.MySQL.QueryRow(sql, uid)
	var updatedAt, hostingAddrs, locality string

	err := row.Scan(&host.UID, &host.FullName, &host.Email, &host.MobileNum,
		&host.Address, &host.Location, &hostingAddrs, &locality, &host.CreatedAt,
		&updatedAt, &host.Password, &host.Username, &host.RangedID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host/Participant not found"})
		return
	}
	json.Unmarshal([]byte(updatedAt), &host.UpdatedAt)
	json.Unmarshal([]byte(hostingAddrs), &host.HostingAddresses)
	json.Unmarshal([]byte(locality), &host.Locality)

	// MongoDB backup
	mongoRes := db.Mongo.Collection("host_participant_docs").FindOne(context.Background(), map[string]interface{}{"uid": uid})
	var mongoData map[string]interface{}
	mongoRes.Decode(&mongoData)

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"host":    host,
		"nosql_backup": mongoData,
	})
}

func UpdateHostByUID(c *gin.Context) {
	uid := c.Param("uid")
	var updated models.Host

	if err := c.ShouldBindJSON(&updated); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	// Convert arrays to JSON
	updatedAtJSON, _ := json.Marshal(updated.UpdatedAt)
	hostingAddrsJSON, _ := json.Marshal(updated.HostingAddresses)
	localityJSON, _ := json.Marshal(updated.Locality)

	// Update MySQL
	query := `
		UPDATE host_participant SET 
			full_name = ?, email = ?, mobile_num = ?, address = ?, location = ?,
			hosting_addresses = ?, locality = ?, created_at = ?, updated_at = ?,
			password = ?, username = ?, ranged_id = ?
		WHERE uid = ?
	`
	_, err := db.MySQL.Exec(query,
		updated.FullName,
		updated.Email,
		updated.MobileNum,
		updated.Address,
		updated.Location,
		string(hostingAddrsJSON),
		string(localityJSON),
		updated.CreatedAt,
		string(updatedAtJSON),
		updated.Password,
		updated.Username,
		updated.RangedID,
		uid,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update MySQL"})
		return
	}

	// Update MongoDB
	_, err = db.Mongo.Collection("host_participant_docs").UpdateOne(
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
		"message": "Host/Participant updated successfully",
	})
}

func DeleteHostByUID(c *gin.Context) {
	uid := c.Param("uid")

	// Delete from MySQL
	query := "DELETE FROM host_participant WHERE uid = ?"
	_, err := db.MySQL.Exec(query, uid)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete from MySQL"})
		return
	}

	// Delete from MongoDB
	_, err = db.Mongo.Collection("host_participant_docs").DeleteOne(
		context.Background(),
		map[string]interface{}{"uid": uid},
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete from MongoDB"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Host/Participant deleted successfully",
	})
}

func GetAllHosts(c *gin.Context) {
	mysqlDB := db.MySQL
	mongoDB := db.MongoDB

	rows, err := mysqlDB.Query("SELECT * FROM host_participant")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch from MySQL"})
		return
	}
	defer rows.Close()

	var hosts []map[string]interface{}
	for rows.Next() {
		var host = make(map[string]interface{})
		var hostingAddrStr, localityStr, updatedAtStr string

		err := rows.Scan(
			&host["uid"], &host["full_name"], &host["email"], &host["mobile_num"],
			&host["address"], &host["location"], &hostingAddrStr, &localityStr,
			&host["created_at"], &updatedAtStr, &host["password"], &host["username"],
			&host["ranged_id"],
		)
		if err != nil {
			continue
		}

		_ = json.Unmarshal([]byte(hostingAddrStr), &host["hosting_addresses"])
		_ = json.Unmarshal([]byte(localityStr), &host["locality"])
		_ = json.Unmarshal([]byte(updatedAtStr), &host["updated_at"])

		// MongoDB backup
		var backup map[string]interface{}
		mongoDB.Collection("host_participant_docs").FindOne(c, bson.M{"uid": host["uid"]}).Decode(&backup)
		host["nosql_backup"] = backup

		hosts = append(hosts, host)
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "hosts": hosts})
}
