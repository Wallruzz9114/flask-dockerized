from flask import Flask


def test_passwords_are_random(test_app: Flask, test_database, create_user):
    user_one = create_user("justatest", "test@test.com", "greaterthaneight")
    user_two = create_user("justatest2", "test@test2.com", "greaterthaneight")
    assert user_one.password != user_two.password
