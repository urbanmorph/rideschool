@sessions_bp.route('/participant_admin/<int:participant_id>')
def participant_admin(participant_id):
    try:
        # Fetch participant details based on participant_id from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.participant_id,
                p.participant_name,
                p.participant_email,
                p.participant_contact,
                p.participant_age,
                p.participant_gender,
                p.participant_address,
                tl.training_location_address,
                p.participant_created_at,
                p.participant_status,
                p.participant_code
            FROM participants p
            JOIN sessions s ON p.participant_id = s.participant_id
            LEFT JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id
            WHERE p.participant_id = %s
            GROUP BY p.participant_id
        """, (participant_id,))

        participant_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if participant_data:
            (
                participant_id,
                participant_name,
                participant_email,
                participant_contact,
                participant_age,
                participant_gender,
                participant_address,
                training_location_address,
                participant_created_at,
                participant_status,
                participant_code
            ) = participant_data

            return render_template(
                'participant_admin.html',
                participant_id=participant_id,
                participant_name=participant_name,
                participant_email=participant_email,
                participant_contact=participant_contact,
                participant_age=participant_age,
                participant_gender=participant_gender,
                participant_address=participant_address,
                training_location_address=training_location_address,
                participant_created_at=participant_created_at,
                participant_status=participant_status,
                participant_code=participant_code
            )
        else:
            return 'Participant not found'
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching participant details. Please try again later.'
