Events API  

[GET /api/events/](./api/events/) → list all events  
[POST /api/events/](./api/events/) → create a new event (admin only)  
[GET /api/events/{id}/](./api/events/{id}/) → retrieve event details  
[PUT /api/events/{id}/](./api/events/{id}/) → update event (admin only)  
[PATCH /api/events/{id}/](./api/events/{id}/) → partial update (admin only)  
[DELETE /api/events/{id}/](./api/events/{id}/) → delete event (admin only)  

Custom Event Actions:  
[POST /api/events/{id}/register/](./api/events/{id}/register/) → register a student to event  
[POST /api/events/{id}/attendance/](./api/events/{id}/attendance/) → mark attendance  
[POST /api/events/{id}/feedback/](./api/events/{id}/feedback/) → submit feedback  


Students API  

[GET /api/students/](./api/students/) → list students  
[POST /api/students/](./api/students/) → create new student (admin only)  
[GET /api/students/{id}/](./api/students/{id}/) → retrieve student  
[PUT /api/students/{id}/](./api/students/{id}/) → update student (admin only)  
[PATCH /api/students/{id}/](./api/students/{id}/) → partial update (admin only)  
[DELETE /api/students/{id}/](./api/students/{id}/) → delete student (admin only)  


Colleges API  

[GET /api/colleges/](./api/colleges/) → list colleges  
[POST /api/colleges/](./api/colleges/) → create new college (admin only)  
[GET /api/colleges/{id}/](./api/colleges/{id}/) → retrieve college  
[PUT /api/colleges/{id}/](./api/colleges/{id}/) → update college (admin only)  
[PATCH /api/colleges/{id}/](./api/colleges/{id}/) → partial update (admin only)  
[DELETE /api/colleges/{id}/](./api/colleges/{id}/) → delete college (admin only)  


Reports API  

[GET /api/reports/event-metrics/{event_id}/](./api/reports/event-metrics/{event_id}/)  
→ returns registrations, attendance %, avg feedback for one event  

[GET /api/reports/event-popularity/?college={id}&type=WORKSHOP](./api/reports/event-popularity/?college={id}&type=WORKSHOP)  
→ ranked events by registration count (optionally filter)  

[GET /api/reports/student-participation/{student_id}/](./api/reports/student-participation/{student_id}/)  
→ participation stats for one student  

[GET /api/reports/top-students/?limit=3&college={id}](./api/reports/top-students/?limit=3&college={id})  
→ top engaged students (by events attended)  
