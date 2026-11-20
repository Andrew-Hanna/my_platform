"""Request bodies for the account endpoints. Field checks here are shape checks only; rules live in services."""

from pydantic import BaseModel


class LoginIn(BaseModel):
    email: str
    password: str


class AcceptInviteIn(BaseModel):
    token: str
    password: str


class ForgotPasswordIn(BaseModel):
    email: str


class ResetPasswordIn(BaseModel):
    token: str
    password: str


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str


class InviteStudentIn(BaseModel):
    name: str
    email: str
