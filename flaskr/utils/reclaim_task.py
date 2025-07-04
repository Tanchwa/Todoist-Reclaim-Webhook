def create_reclaim_task(todoist_json_body)
    try:
        task = Task(
                title = event_data["content"],
                due = reclaim_due_date,
                priority = TaskPriority.P3,
        )

        task.notes              = (
            "Event Created By Tanchwa's Todoist:\n"
            f"{event_data['url']}"
        )
        task.duration           = 0.5
        task.max_work_duration  = 1.5
        task.min_work_duration  = 0.5

        # colour / time‑scheme
        label = (event_data.get("labels") or [None])[0]
        hour_ids = {h.title: h.id for h in Hours.list()}
        working  = hour_ids.get("Working Hours")
        personal = hour_ids.get("Personal Hours")

        if label == "reclaim":
            task.event_color   = EventColor.LAVENDER
            task.time_scheme_id = working
        else:  # default & "reclaim_personal"
            task.event_color   = EventColor.TANGERINE
            task.time_scheme_id = personal

        task.save()

    except RecordNotFound as e:
        print(f"Record not found: {e}")
    except InvalidRecord as e:
        print(f"Invalid record: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except ReclaimAPIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



