package main

import (
	"meetup/db"
	"meetup/routes"

	"github.com/gin-gonic/gin"
)

func main() {
	db.InitMySQL()
	db.InitMongo()
	db.InitSQLite()

	router := gin.Default()

	// Register routes
	routes.RegisterAdminRoutes(router)

	// Add others as they come (e.g., host, auth, etc.)

	router.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "MeetUp Go API is running"})
	})

	router.Run(":8080")
}
