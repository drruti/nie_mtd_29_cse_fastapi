from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["hospital_db"]
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


app = FastAPI(
    title="Hospital Support Request System",
    description="API for managing hospital equipment, maintenance, IT, and facility support requests.",
    version="1.0.0"
)


# ---------------------------------------------------
# DATA MODELS
# ---------------------------------------------------

class ServiceRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    department: str
    requested_by: str


class RequestStatusUpdate(BaseModel):
    status: str


class Assignment(BaseModel):
    assigned_to: str


class Comment(BaseModel):
    user: str
    message: str


# ---------------------------------------------------
# TEMPORARY DATABASE
# ---------------------------------------------------

requests = []

request_id_counter = 1


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Hospital Support Request System API is running",
        "categories": [
            "EQUIPMENT_ISSUE",
            "MAINTENANCE",
            "IT_ISSUE",
            "FACILITY_REQUEST"
        ],
        "statuses": [
            "NEW",
            "ASSIGNED",
            "IN_PROGRESS",
            "ON_HOLD",
            "RESOLVED",
            "CLOSED"
        ]
    }


# ---------------------------------------------------
# CREATE SERVICE REQUEST
# ---------------------------------------------------

@app.post("/requests")
def create_request(request: ServiceRequest):

    global request_id_counter

    new_request = {
        "id": request_id_counter,
        "title": request.title,
        "description": request.description,
        "category": request.category,
        "priority": request.priority,
        "department": request.department,
        "requested_by": request.requested_by,
        "status": "NEW",
        "assigned_to": None,
        "comments": []
    }

    requests.append(new_request)

    request_id_counter += 1

    return {
        "message": "Hospital support request created successfully",
        "request": new_request
    }


# ---------------------------------------------------
# VIEW ALL REQUESTS
# ---------------------------------------------------

@app.get("/requests")
def get_requests():

    return {
        "total_requests": len(requests),
        "requests": requests
    }


# ---------------------------------------------------
# VIEW ONE REQUEST
# ---------------------------------------------------

@app.get("/requests/{request_id}")
def get_request(request_id: int):

    for request in requests:

        if request["id"] == request_id:
            return request

    return {
        "message": "Support request not found"
    }


# ---------------------------------------------------
# ASSIGN REQUEST TO TECHNICIAN / STAFF
# ---------------------------------------------------

@app.put("/requests/{request_id}/assign")
def assign_request(
    request_id: int,
    assignment: Assignment
):

    for request in requests:

        if request["id"] == request_id:

            request["assigned_to"] = assignment.assigned_to
            request["status"] = "ASSIGNED"

            return {
                "message": "Request assigned successfully",
                "request": request
            }

    return {
        "message": "Support request not found"
    }


# ---------------------------------------------------
# UPDATE REQUEST STATUS
# ---------------------------------------------------

@app.put("/requests/{request_id}/status")
def update_status(
    request_id: int,
    status_update: RequestStatusUpdate
):

    allowed_statuses = [
        "NEW",
        "ASSIGNED",
        "IN_PROGRESS",
        "ON_HOLD",
        "RESOLVED",
        "CLOSED"
    ]

    if status_update.status not in allowed_statuses:

        return {
            "message": "Invalid status",
            "allowed_statuses": allowed_statuses
        }

    for request in requests:

        if request["id"] == request_id:

            request["status"] = status_update.status

            return {
                "message": "Request status updated successfully",
                "request": request
            }

    return {
        "message": "Support request not found"
    }


# ---------------------------------------------------
# ADD COMMENT
# ---------------------------------------------------

@app.post("/requests/{request_id}/comments")
def add_comment(
    request_id: int,
    comment: Comment
):

    for request in requests:

        if request["id"] == request_id:

            new_comment = {
                "user": comment.user,
                "message": comment.message
            }

            request["comments"].append(new_comment)

            return {
                "message": "Comment added successfully",
                "request": request
            }

    return {
        "message": "Support request not found"
    }


# ---------------------------------------------------
# DELETE REQUEST
# ---------------------------------------------------

@app.delete("/requests/{request_id}")
def delete_request(request_id: int):

    for request in requests:

        if request["id"] == request_id:

            requests.remove(request)

            return {
                "message": "Support request deleted successfully"
            }

    return {
        "message": "Support request not found"
    }