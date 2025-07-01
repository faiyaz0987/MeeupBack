package routes

import (
	"github.com/gin-gonic/gin"
	"meetup/api/go_api/controllers"
	"meetup/api/go_api/middleware"
)


func RegisterHostRoutes(r *gin.Engine) {
	host := r.Group("/host")
	{
		host.POST("/create", middleware.JWTAuthMiddleware(), controllers.CreateHost)
		host.GET("/get/:uid", middleware.JWTAuthMiddleware(), controllers.GetHostByUID)
		host.PUT("/update/:uid", middleware.JWTAuthMiddleware(), controllers.UpdateHostByUID)
		host.DELETE("/delete/:uid", middleware.JWTAuthMiddleware(), controllers.DeleteHostByUID)
		host.GET("/all", controllers.GetAllHosts)
	}
}