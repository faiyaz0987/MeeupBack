package routes

import (
	"meetup/controllers"

	"github.com/gin-gonic/gin"
)

func RegisterAdminRoutes(r *gin.Engine) {
	admin := r.Group("/admin")
	{
		admin.POST("/create", controllers.CreateAdmin)
		admin.GET("/get/:uid", middleware.JWTAuthMiddleware(), controllers.GetAdminByUID)
		admin.PUT("/update/:uid", middleware.JWTAuthMiddleware(), controllers.UpdateAdminByUID)
		admin.DELETE("/delete/:uid", middleware.JWTAuthMiddleware(), controllers.DeleteAdminByUID)
		admin.GET("/all", controllers.GetAllAdmins)
	}
}

