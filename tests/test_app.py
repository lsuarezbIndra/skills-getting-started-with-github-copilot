from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Club",
        "Basketball Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club",
    }

    response = client.get("/activities")

    assert response.status_code == 200
    assert set(response.json()) == expected_activity_names
    assert all(
        {"description", "schedule", "max_participants", "participants"}
        <= set(activity)
        for activity in response.json().values()
    )


def test_signup_adds_participant_and_returns_message(client):
    activity_name = "Soccer Club"
    email = "student@example.com"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    activity_name = "Robotics Club"
    email = "student@example.com"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    activity_name = "Soccer Club"

    response = client.post(f"/activities/{activity_name}/signup")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "email"


def test_signup_supports_activity_names_with_spaces(client):
    activity_name = "Programming Class"
    email = "student@example.com"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_unregister_removes_participant_and_returns_message(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    activity_name = "Robotics Club"
    email = "student@example.com"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant(client):
    activity_name = "Soccer Club"
    email = "student@example.com"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_requires_email(client):
    activity_name = "Soccer Club"

    response = client.delete(f"/activities/{activity_name}/participants")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "email"